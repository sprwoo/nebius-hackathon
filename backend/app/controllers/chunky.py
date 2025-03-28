import os
from openai import OpenAI
from dotenv import load_dotenv
import base64

load_dotenv()

class Chunky():
    def __init__(self):
        self.client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=os.getenv("LLM_KEY")
        )
        self.temperature = 0.1
        self.max_tokens = 100
        
    def basic_response(self, prompt):
        response = self.client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}",
                }
            ],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
    
    def basic_image_handling_stored_image(self, prompt, image_path):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            
        response = self.client.chat.completions.create(
            model="google/gemma-3-27b-it",
            max_tokens=100,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ]
        )
        
        return response.choices[0].message.content