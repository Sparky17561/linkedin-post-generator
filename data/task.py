import requests
import json
import os

class LinkedinCarousel:
    def __init__(self, access_token, file_path, image_folder):
        self.access_token = access_token
        self.file_path = file_path
        self.image_folder = image_folder
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.content = self.extract_content_from_file()
        self.image_paths = self.get_image_paths()
        self.user_id = self.get_user_id()

    def extract_content_from_file(self):
        """Read and return content from the file."""
        try:
            with open(self.file_path, 'r', encoding="utf-8") as file:
                return "\n".join([line.strip() for line in file.readlines()])
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def get_image_paths(self):
        """Get all image paths in the specified folder."""
        return [os.path.join(self.image_folder, file) for file in os.listdir(self.image_folder) if file.endswith(('.png', '.jpg', '.jpeg'))]

    def get_user_id(self):
        """Fetch LinkedIn user ID."""
        url = "https://api.linkedin.com/v2/userinfo"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("sub")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching user ID: {e}")
            return None

    def initialize_upload(self):
        """Initialize image upload to LinkedIn using the correct endpoint."""
        url = "https://api.linkedin.com/v2/assets?action=registerUpload"
        payload = {
            "registerUploadRequest": {
                "owner": f"urn:li:person:{self.user_id}",
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]
            }
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            upload_data = response.json()
            
            # Debugging response
            print(f"Upload Initialization Response: {json.dumps(upload_data, indent=2)}")

            if "value" not in upload_data or "uploadMechanism" not in upload_data["value"]:
                print("Error: Upload URL not received from LinkedIn.")
                return None, None

            return upload_data["value"]["asset"], upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
        except requests.exceptions.RequestException as e:
            print(f"Error initializing image upload: {e} | Response: {response.text}")
            return None, None

    def upload_image(self, upload_url, image_path):
        """Upload image file to LinkedIn."""
        try:
            with open(image_path, "rb") as file:
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "image/png" if image_path.endswith(".png") else "image/jpeg"
                }
                response = requests.put(upload_url, headers=upload_headers, data=file.read())  # Send raw binary data
                response.raise_for_status()

                # Debugging response
                print(f"Image Upload Response for {image_path}: {response.status_code}, {response.text}")

                return response.status_code in [200, 201]
        except requests.exceptions.RequestException as e:
            print(f"Error uploading image {image_path}: {e}")
            return False

    def upload_all_images(self):
        """Upload all images in the folder and return their LinkedIn asset IDs."""
        image_ids = []
        for image_path in self.image_paths:
            print(f"Processing Image: {image_path}")  # Debugging: See if image paths are correct
            asset_id, upload_url = self.initialize_upload()
            if asset_id and upload_url and self.upload_image(upload_url, image_path):
                image_ids.append(asset_id)
            else:
                print(f"Failed to upload: {image_path}")
        return image_ids

    def create_carousel_post(self, image_ids):
        """Create a carousel post with uploaded images."""
        url = "https://api.linkedin.com/v2/ugcPosts"
        payload = {
            "author": f"urn:li:person:{self.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": self.content},
                    "shareMediaCategory": "IMAGE",
                    "media": [{"status": "READY", "media": img_id} for img_id in image_ids]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print("Carousel Post Created Successfully!")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error creating carousel post: {e}")
            return None

    def main_func(self):
        """Main function to execute all steps."""
        if not self.user_id:
            print("Error: Could not fetch user ID.")
            return

        if not self.content:
            print("Error: No content extracted from file.")
            return

        if not self.image_paths:
            print("Error: No images found in the specified folder.")
            return

        print(f"Uploading {len(self.image_paths)} images...")
        image_ids = self.upload_all_images()
        
        if image_ids:
            print(f"Uploaded {len(image_ids)} images. Creating carousel post...")
            post_response = self.create_carousel_post(image_ids)
            if post_response:
                print(f"Carousel Post Response: {post_response}")
            else:
                print("Error posting carousel.")
        else:
            print("Error: No images uploaded successfully.")

# Usage
ACCESS_TOKEN = "AQUxd7Bk5WNEz9kQbhUy9wwgsCrAE6Hipi_qY8rgep0yu1VSVKPaNpWsK9fPHAKJfdoaNUc-O7X_kZ-INdfEb_sfT5yCtBngig4_wDyIS-NIKOtixYMqy-S8WssVAqonyQsguyn-_F06mvk6Lk2X8zZKKpI_KyI11v7hpP-N7YQVPJj40l2zFI4Ku6OruapoNpYoS768gMH9Q1qoxj7grYCipLp3A0y-c6NSRbdgPTMGPuu_oHx09SbNvAz1_j-TwTyb55Umsp3D86tLb7Z93iYfZZc1_B8n4ChC7CDdyZ09ZPPIbCYOK7oDKtcZh6IMxL0QekDGNMTKeNmcR1aG0thAoPMGxA"
FILE_PATH = "post.txt"
IMAGE_FOLDER = "images"  # Folder containing images

LinkedinCarousel(ACCESS_TOKEN, FILE_PATH, IMAGE_FOLDER).main_func()
