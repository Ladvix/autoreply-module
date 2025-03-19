import json
import requests


MODEL = 'google/gemini-2.0-flash-lite-preview-02-05:free'

class Subconscious:

    def __init__(self, api_key):
        self.api_key = api_key
        self.thoughts = []
    

    def add_thought(self, thought):
        if thought:
            self.thoughts.append(thought)
    

    def get_thoughts(self):
        return ' '.join(self.thoughts)


    def process_content(self, content):
        cleaned = content.translate(str.maketrans('', '', '*`'))
        
        thoughts = []
        
        while '<think>' in cleaned and '</think>' in cleaned:
            start = cleaned.index('<think>')
            end = cleaned.index('</think>') + 8
            thought = cleaned[start+7:end-8]
            thoughts.append(thought)
            cleaned = cleaned[:start] + cleaned[end:]
        
        return cleaned, thoughts


    def stream(self, prompt, subconscious):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': True
        }

        with requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=data,
            stream=True
        ) as response:
            if response.status_code != 200:
                return ''

            full_response = []
            
            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8').replace('data: ', '')

                    try:
                        chunk_json = json.loads(chunk_str)

                        if 'choices' in chunk_json:
                            content = chunk_json['choices'][0]['delta'].get('content', '')

                            if content:
                                cleaned, thoughts = self.process_content(content)
                                subconscious.add_thought(' '.join(thoughts))
                                
                                full_response.append(cleaned)
                    except:
                        pass

            return ''.join(full_response)