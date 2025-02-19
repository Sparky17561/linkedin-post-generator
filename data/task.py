import requests
import json

class LinkedinAutomate:
    def __init__(self, access_token, file_path):
        self.access_token = access_token
        self.file_path = file_path
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        self.content = self.extract_content_from_file()

    def extract_content_from_file(self):
        try:
            with open(self.file_path, 'r') as file:
                content = "\n".join([line.strip() for line in file.readlines()])  # Read all lines as a single string
            return content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def get_user_id(self):
        url = "https://api.linkedin.com/v2/userinfo"  # Corrected endpoint
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raises exception for 4xx/5xx status codes
            jsonData = response.json()
            print(f"API Response: {jsonData}")  # Print the response to see the exact structure
            return jsonData.get("sub")  # Correct to fetch the 'sub' field for the user ID
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user ID: {e}")
            return None

    def common_api_call_part(self):
        # Prepare payload for sharing post
        payload_dict = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": self.content  # Use the entire content from the file
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        print(f"Payload to be sent: {json.dumps(payload_dict, indent=4)}")  # Print payload for debugging
        return json.dumps(payload_dict)

    def feed_post(self):
        url = "https://api.linkedin.com/v2/ugcPosts"  # Correct endpoint for feed post
        payload = self.common_api_call_part()
        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response.raise_for_status()  # Raise an error for bad status codes
            print(f"Feed Post Success: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            print(f"Feed Post Error: {e}")
            return None

    def main_func(self):
        if not self.content:
            print("Error: Content could not be extracted from the file.")
            return

        if not self.access_token:
            print("Error: Access token not available.")
            return

        self.user_id = self.get_user_id()
        if not self.user_id:
            print("Error: Could not fetch user ID.")
            return

        print(f"User ID: {self.user_id}")

        feed_post = self.feed_post()
        if feed_post:
            print(f"Feed Post Response: {feed_post.status_code} - {feed_post.text}")
        else:
            print("Error posting to feed.")


# Usage
access_token = "AQVBcWRZPiO5JDEHQzk3XDevBHlw2KgSDE1JyG-8241a4KJPA3HpYllzUWfi6rdODdvvdI5ae_XNp3Jq3KVCEUlU6-2_5VSS7Jg-iFRVyv5B4g_Qmu_G-EcTaz4F4z__YxFzoNgdzkObsKevmcwdOGEg9-DGk3cNx62FGZHMZISLAJWuRoG5hK5jjalYiU-6BXxScxISbjN5IE78lm-_qSDd1wO7hBHpxLJBK4CXwUbgEfnLcdKcthAhcvoRKmqQQ_xNw-MU-HOc8K_v9LvaTkvtMltytnXhSF25eohHsq5fUTlJO6vXo4ui3plYekt041ie0XwRr-ghLn_ORTPzTNLIreQP9w"  # Replace with your actual Access Token
file_path = "post.txt"  # Replace with the actual file path containing the content

LinkedinAutomate(access_token, file_path).main_func()
