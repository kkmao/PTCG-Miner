import requests
import os
import time


class DiscordMsg:
    def __init__(self, webhook_url, user_id):
        self.webhook_url = webhook_url
        self.user_id = user_id

    def log_to_discord(self, message, screenshot_file=None, ping=False, xml_file=None):
        send_xml = 1  # Set this to your desired value

        if self.webhook_url:
            max_retries = 10
            retry_count = 0

            while retry_count < max_retries:
                try:
                    # Prepare the message data
                    if ping and self.user_id:
                        data = {"content": f"<@{self.user_id}> {message}"}
                    else:
                        data = {"content": message}

                    # Send the message
                    response = requests.post(self.webhook_url, json=data)
                    response.raise_for_status()

                    # If an image file is provided, send it
                    if screenshot_file and os.path.isfile(screenshot_file):
                        with open(screenshot_file, "rb") as f:
                            files = {"file": f}
                            response = requests.post(self.webhook_url, files=files)
                            response.raise_for_status()

                    # If an XML file is provided and sendXML is greater than 0, send it
                    if xml_file and send_xml > 0 and os.path.isfile(xml_file):
                        with open(xml_file, "rb") as f:
                            files = {"file": f}
                            response = requests.post(self.webhook_url, files=files)
                            response.raise_for_status()

                    break
                except requests.RequestException as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print("Failed to send discord message.")
                        break
                    time.sleep(0.25)
                time.sleep(0.25)
