import requests
import time
import os
import sys
import argparse
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s UTC - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="URL of the animation file to poll")
    parser.add_argument("--dest", required=True, help="Local destination path")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    args = parser.parse_args()

    logger.info(f"Starting Updater Service...")
    logger.info(f"Polling URL: {args.url}")
    logger.info(f"Target Destination: {args.dest}")
    logger.info(f"Polling Interval: {args.interval} seconds")

    last_content = None

    # Load initial content if exists
    if os.path.exists(args.dest):
        try:
            with open(args.dest, 'rb') as f:
                last_content = f.read()
            logger.info("Loaded existing local file.")
        except Exception as e:
            logger.error(f"Error reading local file {args.dest}: {e}")

    while True:
        timestamp_utc = datetime.datetime.utcnow().isoformat()
        
        # Cache busting
        poll_url = f"{args.url}?t={int(time.time())}"
        
        logger.info(f"[{timestamp_utc}] Fetching from: {poll_url}")
        try:
            response = requests.get(poll_url, timeout=10)
            if response.status_code == 200:
                new_content = response.content
                if new_content != last_content:
                    logger.info("New animation detected! Updating file...")
                    with open(args.dest, 'wb') as f:
                        f.write(new_content)
                    last_content = new_content
                    logger.info("Update complete.")
                else:
                    logger.debug("No change in animation content.")
            else:
                logger.warning(f"Failed to fetch {args.url}: HTTP Status {response.status_code}")
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error to {args.url}: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout fetching from {args.url}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching {args.url}: {e}")

        time.sleep(args.interval)

if __name__ == "__main__":
    main()
