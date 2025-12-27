import os
import logging
import datetime
import time
import re
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import storage
from google.cloud import firestore
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Initialize App
app = FastAPI()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "xmas-lights-demo")
REGION = os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
BUCKET_NAME = f"{PROJECT_ID}-animations"
FIRESTORE_COLLECTION = "prompt_history"

# Initialize GCP Clients
try:
    storage_client = storage.Client()
    firestore_client = firestore.Client()
    
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=REGION)
except Exception as e:
    logger.error(f"Failed to initialize GCP clients: {e}")

# Models
class PromptRequest(BaseModel):
    prompt: str

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.post("/generate")
async def generate_animation(request: PromptRequest):
    prompt = request.prompt
    logger.info(f"Received prompt: {prompt}")
    start_time = time.time()

    # 1. Generate Code with Gemini (Vertex AI)
    try:
        t0 = time.time()
        model = GenerativeModel("gemini-2.5-flash")
        
        system_prompt = """The PromptSystem Role: You are an expert Python developer specializing in procedural LED animations for holiday lighting.
Environment Context:
Execution Loop: The function anim_generated is called inside a high-frequency while loop (approx. 30-60 FPS).
Spatial Orientation: The LED strip is wrapped around a tree. Index 0 is the absolute BOTTOM of the tree. Index num_leds - 1 is the absolute TOP.
Physics Direction: "Downward" movement must decrement indices toward 0. "Upward" movement must increment indices toward num_leds - 1.

Function Signature:
def anim_generated(current_state, state, step, num_leds):
    \"\"\"
    current_state: List of (r, g, b) tuples representing the frame currently displayed.
    state: Persistent dictionary to store variables like positions, velocities, or timers.
    step: Integer that increments by 1 every frame.
    num_leds: Integer count of the total LEDs.
    Returns: A list of num_leds (r, g, b) tuples for the next frame.
    \"\"\"

Implementation Constraints:
Strict Return Type: You must return a list containing exactly num_leds tuples. Never return None.
No External Dependencies: Use only standard libraries (math, random). No API calls or external assets.
State Initialization: Always check if your variables exist in state (e.g., if 'pos' not in state:) to avoid KeyError.
Value Safety: Ensure all RGB components are integers clamped between 0 and 255.
Efficiency: Use O(N) logic. Avoid heavy computation that would drop the frame rate.
Output Format: Output ONLY the python code for the function. No markdown formatting, no backticks.

Animation Requirements:
Smoothness: Use math functions (sine, cosine, power functions) for fluid motion rather than jittery random steps.
Directional Accuracy: Respect the tree orientation (0=Bottom, Max=Top).
Dynamics: Use step to drive time-based oscillations and the state dict to drive physics-based movement.
User Theme: """
        
        full_prompt = f"{system_prompt} {prompt}"
        
        # Async generation
        response = await model.generate_content_async(full_prompt)
        raw_text = response.text
        
        # Robust extraction: Look for code inside ```python ... ``` or ``` ... ```
        # If not found, assume the whole text is code (after stripping)
        match = re.search(r'```(?:python)?\s*(.*?)```', raw_text, re.DOTALL | re.IGNORECASE)
        if match:
            generated_code = match.group(1).strip()
        else:
            generated_code = raw_text.strip()
            
        # Fallback: If code starts with "python", strip it (rare edge case)
        if generated_code.startswith("python"):
            generated_code = generated_code[6:].strip()
            
        logger.info(f"Step 1 (Gemini Generation) took {time.time() - t0:.2f}s")
        
    except Exception as e:
        logger.error(f"Vertex AI Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

    # 2. Upload to Cloud Storage
    try:
        t1 = time.time()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob("current_anim.py")
        
        # Storage upload is technically sync in this library version usually, 
        # but fast enough. Run in threadpool if strictly needed, but keep simple for now.
        blob.upload_from_string(generated_code, content_type="text/x-python")
        
        try:
            blob.make_public()
        except Exception:
            pass
            
        public_url = blob.public_url
        logger.info(f"Step 2 (GCS Upload) took {time.time() - t1:.2f}s")
    except Exception as e:
        logger.error(f"GCS Upload Error: {e}")
        raise HTTPException(status_code=500, detail=f"Storage upload failed: {str(e)}")

    # 3. Save to Firestore
    try:
        t2 = time.time()
        doc_ref = firestore_client.collection(FIRESTORE_COLLECTION).document()
        doc_ref.set({
            "prompt": prompt,
            "code": generated_code,
            "timestamp": datetime.datetime.now(datetime.timezone.utc),
            "file_url": public_url
        })
        logger.info(f"Step 3 (Firestore Save) took {time.time() - t2:.2f}s")
    except Exception as e:
        logger.error(f"Firestore Error: {e}")
        # Don't fail the request if history save fails
    
    total_time = time.time() - start_time
    logger.info(f"Total processing time: {total_time:.2f}s")
    
    return {
        "status": "success", 
        "message": "Animation generated and deployed", 
        "url": public_url,
        "code_snippet": generated_code[:200] + "..."
    }

@app.get("/history")
async def get_history():
    try:
        history = []
        docs = (
            firestore_client.collection(FIRESTORE_COLLECTION)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(20)
            .stream()
        )
            
        for doc in docs:
            data = doc.to_dict()
            history.append({
                "prompt": data.get("prompt"),
                "timestamp": data.get("timestamp").isoformat() if data.get("timestamp") else None
            })
        return history
    except Exception as e:
        logger.error(f"Firestore Read Error: {e}")
        return []

app.mount("/static", StaticFiles(directory="static"), name="static")