import requests
import os

class VideoUploader:
    def __init__(self, server_url):
        self.server_url = server_url
        
    def upload_video(self, video_path):
        try:
            with open(video_path, 'rb') as video_file:
                files = {'video': video_file}
                response = requests.post(f"{self.server_url}/upload", files=files)
                
                if response.status_code == 200:
                    print(f"Successfully uploaded {video_path}")
                    os.remove(video_path)  # Clean up local file
                else:
                    print(f"Failed to upload {video_path}: {response.status_code}")
                    
        except Exception as e:
            print(f"Error uploading video: {str(e)}")
