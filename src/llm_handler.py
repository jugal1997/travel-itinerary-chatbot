"""
LLM handler for generating responses using open-source models
"""
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

class LLMHandler:
    """Handles LLM API calls"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "huggingface")
        self.model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3.1-8B-Instruct")
        
        if self.provider == "huggingface":
            api_key = os.getenv("HUGGINGFACE_API_KEY")
            if not api_key:
                raise ValueError("HUGGINGFACE_API_KEY not found in .env file")
            self.client = InferenceClient(token=api_key)
        elif self.provider == "ollama":
            try:
                import ollama
                self.client = ollama
            except ImportError:
                raise ImportError("Ollama not installed. Run: pip install ollama")
    
    def generate_response(self, prompt, max_tokens=1000, temperature=0.7):
        """Generate response from LLM"""
        try:
            if self.provider == "huggingface":
                # Use chat_completion for conversational models like Llama
                messages = [{"role": "user", "content": prompt}]
                
                response = self.client.chat_completion(
                    messages=messages,
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                # Extract the response text
                return response.choices[0].message.content
                
            elif self.provider == "ollama":
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                )
                return response['response']
                
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def test_connection(self):
        """Test LLM connection"""
        test_prompt = "Say 'Hello, I am working!' in one short sentence."
        try:
            response = self.generate_response(test_prompt, max_tokens=50)
            
            # Check if response contains an error message
            if "Error generating response" in response:
                return False, response
            
            return True, response
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
