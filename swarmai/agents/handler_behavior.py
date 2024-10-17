# agents/handler_behavior.py
import base64
from AgentBase import BaseAgent
import requests

class HandlerAgent(BaseAgent):
    def run(self):
        input_files = self.get_shared_resource('input_files')
        instructions, supporting_docs = self.process_documents(input_files)
        self.share_resource('instructions', instructions)
        self.share_resource('supporting_docs', supporting_docs)
        self.log_info("Handler has extracted instructions and supporting documents.")

    def process_documents(self, files):
        combined_instructions = ''
        combined_supporting = ''
        for file in files:
            file_content = self.load_file(file)
            instruction, supporting = self.analyze_with_gpt4_vision(file_content)
            combined_instructions += instruction + '\n'
            combined_supporting += supporting + '\n'
        return combined_instructions.strip(), combined_supporting.strip()

    def load_file(self, file_path):
        with open(file_path, 'rb') as file:
            return file.read()

    def analyze_with_gpt4_vision(self, file_content):
        # Encode the file content in base64
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        # Construct the payload for the API
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            "model": "gpt-4-vision",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Please analyze the attached document and separate the content into two sections: "
                        "'---Instructions---' and '---Supporting Documents---'. "
                        "Ensure the instructions are clear and concise, and include any relevant details."
                    )
                },
            ],
            "file": encoded_content,
        }
        # Send the request to the API
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response_data = response.json()
        if response.status_code != 200:
            self.log_error(f"API Error: {response_data.get('error', {}).get('message', 'Unknown error')}")
            return '', ''
        # Parse the response
        full_text = response_data['choices'][0]['message']['content']
        # Separate instructions and supporting documents
        instruction, supporting = self.separate_content(full_text)
        return instruction, supporting

    def separate_content(self, text):
        # Separate content based on predefined delimiters
        if '---Instructions---' in text and '---Supporting Documents---' in text:
            parts = text.split('---Instructions---')[1].split('---Supporting Documents---')
            instructions = parts[0].strip()
            supporting_docs = parts[1].strip()
        else:
            # If the format is unexpected, treat the entire text as instructions
            instructions = text.strip()
            supporting_docs = ''
        return instructions, supporting_docs