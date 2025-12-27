# AI Holiday Lights Controller 🎄✨

This project implements an AI-driven holiday light controller that generates procedural animations from natural language prompts. Users describe an effect (e.g., "sparkling blue rain"), and Google Gemini (Vertex AI) generates the corresponding Python code, which is immediately deployed to a connected LED controller (Raspberry Pi/Orange Pi).

## 🏗️ Architecture

The system consists of two main components:

1.  **Web Application (Google Cloud Run):**
    -   **Frontend:** Simple jQuery-based UI for entering prompts and viewing history.
    -   **Backend:** FastAPI app that calls Vertex AI (Gemini 2.5 Flash) to generate Python code.
    -   **Storage:** Saves generation history to **Firestore** and uploads the generated animation module (`current_anim.py`) to a public **Google Cloud Storage (GCS)** bucket.

2.  **Device Controller (Orange Pi / Raspberry Pi):**
    -   **`xmas-lights` Service:** A Python daemon that drives the LED strip (SPI) using `spidev`. It supports **hot-reloading**, allowing it to switch animations without restarting the process.
    -   **`xmas-updater` Service:** A background poller that checks the GCS bucket for new animation files. When a change is detected, it downloads the new code, triggering the main controller to reload.

## 🚀 Deployment Guide

### Prerequisites
*   Google Cloud Platform (GCP) Project.
*   `gcloud` CLI installed and authenticated (`gcloud auth login`).
*   Orange Pi or Raspberry Pi with SPI enabled and internet access.

### 1. Cloud Infrastructure Setup
Use the provided scripts to set up everything in one go.

**One-Click Deployment:**
Run this from your workstation to set up GCP resources, deploy the web app, and publish the device code.
```bash
./scripts/deploy_all.sh <PROJECT_ID> [REGION]
# Example: ./scripts/deploy_all.sh my-lights-project us-central1
```

**Individual Scripts (for manual control):**
*   `scripts/setup_gcp.sh <PROJECT_ID>`: Enables APIs (Vertex AI, Run, Build), creates Firestore DB, and public GCS bucket.
*   `scripts/deploy_webapp.sh <PROJECT_ID>`: Deploys the FastAPI app to Cloud Run with a dedicated Service Account.
*   `scripts/publish_device_code.sh <PROJECT_ID>`: Packages the `controller/` code and uploads it to the GCS bucket for the device to fetch.

### 2. Device Installation
On your Orange Pi or Raspberry Pi, run the bootstrap command printed at the end of the deployment script. This command downloads the installer from your cloud bucket and sets up the systemd services.

```bash
curl -sL https://storage.googleapis.com/<PROJECT_ID>-animations/install.sh | sudo bash -s <PROJECT_ID>
```

This will:
1.  Install dependencies (`python3`, `spidev`, `build-essential`).
2.  Create a virtual environment in `/opt/xmas-lights`.
3.  Install and start `xmas-lights` and `xmas-updater` services.

## 🎮 Usage

1.  Open the Web App URL (provided by `deploy_all.sh` output).
2.  Type a prompt (e.g., *"Matrix digital rain effect with green trails"*).
3.  Click **"Make it shine!"**.
4.  Wait ~10-20 seconds. The code is generated, uploaded, and the device will automatically pick it up and apply the new effect.

## 📂 Project Structure

```text
.
├── controller/          # Code running on the physical device
│   ├── main.py          # LED driver & animation loop (hot-reloads modules)
│   ├── updater.py       # Polls GCS for new animation code
│   ├── animations.py    # Library of standard animations
│   ├── install.sh       # Device bootstrap script
│   └── config.json      # Local configuration (brightness, mode)
├── webapp/              # Cloud Run application
│   ├── main.py          # FastAPI backend & Vertex AI integration
│   ├── Dockerfile       # Container definition
│   └── static/          # Frontend assets
└── scripts/             # Deployment automation
    ├── setup_gcp.sh     # Infrastructure provisioning
    ├── deploy_webapp.sh # Cloud Run deployment
    └── publish_device_code.sh # Uploads controller code to GCS
```

## 🛠️ Troubleshooting

**Device Logs:**
Check the status of the services on the Pi:
```bash
sudo systemctl status xmas-lights
sudo systemctl status xmas-updater
```
View real-time logs:
```bash
journalctl -u xmas-lights -f
journalctl -u xmas-updater -f
```

**Common Issues:**
*   **404 Fetch Error:** Ensure the GCS bucket is public and the `updater.py` URL is correct.
*   **Model Not Found:** Ensure Vertex AI API is enabled and the region in `deploy_webapp.sh` matches available Gemini models.
