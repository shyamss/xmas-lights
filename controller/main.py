import spidev
import time
import threading
import os
import importlib
import sys
import json
import logging
import animations

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CONFIGURATION ---
NUM_LEDS = 100
SPI_SPEED = 3200000
P0, P1 = 0x80, 0xF0
GENERATED_FILE = "generated_anim.py"
CONFIG_FILE = "config.json"

# Default State
config = {
    "mode": "generated",
    "brightness": 0.3
}
keep_running = True
generated_module = None
last_anim_mtime = 0
last_config_mtime = 0

# --- HARDWARE SETUP ---
try:
    spi = spidev.SpiDev()
    spi.open(1, 0)
    spi.max_speed_hz = SPI_SPEED
    logger.info("SPI Interface initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize SPI: {e}")
    # Continue? Without SPI we can't do much, but maybe we can dry-run.
    # For now, let's allow crash or mock.
    # spi = None 

def push_to_strip(led_state):
    """Encodes and pushes with global brightness scaling."""
    if not spi:
        return

    full_buffer = [(0, 0, 0)] + led_state
    raw_bytes = []
    
    current_brightness = config.get("brightness", 0.3)

    for (r, g, b) in full_buffer:
        r_scaled = int(r * current_brightness)
        g_scaled = int(g * current_brightness)
        b_scaled = int(b * current_brightness)
        
        for channel in [r_scaled, g_scaled, b_scaled]:
            for i in range(7, -1, -1):
                raw_bytes.append(P1 if (channel >> i) & 0x01 else P0)
                
    try:
        spi.xfer2(raw_bytes)
    except Exception as e:
        logger.error(f"SPI Transfer failed: {e}")
    # minimal sleep
    time.sleep(0.0001)

def load_config():
    global config, last_config_mtime
    if not os.path.exists(CONFIG_FILE):
        return

    try:
        mtime = os.path.getmtime(CONFIG_FILE)
        if mtime > last_config_mtime:
            logger.info("Config file change detected. Reloading...")
            with open(CONFIG_FILE, 'r') as f:
                new_config = json.load(f)
                config.update(new_config)
            logger.info(f"Config loaded: {config}")
            last_config_mtime = mtime
    except Exception as e:
        logger.error(f"Config load failed: {e}")

def load_generated_anim():
    global generated_module, last_anim_mtime
    if not os.path.exists(GENERATED_FILE):
        return False

    try:
        mtime = os.path.getmtime(GENERATED_FILE)
        if mtime > last_anim_mtime:
            logger.info("New generated animation file detected. Reloading module...")
            # Modify sys.path to ensure we can import from current dir
            if os.getcwd() not in sys.path:
                sys.path.append(os.getcwd())
                
            if generated_module is None:
                try:
                    generated_module = importlib.import_module("generated_anim")
                    logger.info("Module 'generated_anim' imported successfully.")
                except ImportError as e:
                    logger.error(f"Failed to import generated_anim: {e}")
            else:
                try:
                    generated_module = importlib.reload(generated_module)
                    logger.info("Module 'generated_anim' reloaded successfully.")
                except Exception as e:
                    logger.error(f"Error reloading module: {e}")
            
            last_anim_mtime = mtime
            return True
    except Exception as e:
        logger.error(f"Hot-reload check failed: {e}")
    return False

def animation_loop():
    global keep_running
    led_state = [(0, 0, 0)] * NUM_LEDS
    state = {}
    step = 0
    
    logger.info("Starting animation loop...")
    
    while keep_running:
        # Check for updates
        load_config()
        anim_updated = load_generated_anim()
        
        current_mode = config.get("mode", "generated")
        logger.debug(f"Animation loop active. Step: {step}, Mode: {current_mode}")

        # Reset state if animation source changed
        if anim_updated and current_mode == "generated":
             logger.info("Resetting animation state due to module update.")
             state = {}
        
        if current_mode == "generated":
             if generated_module and hasattr(generated_module, 'anim_generated'):
                 try:
                     led_state = generated_module.anim_generated(led_state, state, step, NUM_LEDS)
                 except Exception as e:
                     logger.error(f"Animation Execution Error in 'anim_generated': {e}")
                     # Visual Error Indication (Red flash)
                     led_state = [(255, 0, 0)] * NUM_LEDS
             else:
                 if step % 100 == 0:
                     logger.warning("Mode is 'generated' but module not loaded or function missing. Using OFF.")
                 led_state = animations.anim_off(led_state, state, step, NUM_LEDS)
        else:
            calc_func = animations.ANIMATION_MAP.get(current_mode, animations.anim_off)
            try:
                led_state = calc_func(led_state, state, step, NUM_LEDS)
            except Exception as e:
                 logger.error(f"Animation Execution Error in '{current_mode}': {e}")
                 led_state = [(255, 0, 0)] * NUM_LEDS

        push_to_strip(led_state)
        step += 1
        time.sleep(0.03)

if __name__ == "__main__":
    try:
        animation_loop()
    except KeyboardInterrupt:
        logger.info("Stopping...")
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}", exc_info=True)
    finally:
        keep_running = False
        if spi:
            push_to_strip([(0, 0, 0)] * NUM_LEDS)
            spi.close()
        logger.info("Exited.")
