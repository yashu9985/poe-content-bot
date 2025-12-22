from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
import google.generativeai as genai

class ContentGeneratorBot(PoeBot):
    
    def __init__(self):
        super().__init__()
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def get_response(self, request: QueryRequest):
        user_message = request.query[-1].content
        content_type = self.detect_content_type(user_message)
        
        yield self.text_event(f"Generating your {content_type}...\n\n")
        
        if not self.model:
            yield self.error_event("API not configured")
            return
        
        prompt = self.build_prompt(content_type, user_message)
        
        try:
            response = self.model.generate_content(prompt)
            yield self.text_event(response.text)
        except Exception as e:
            yield self.error_event(f"Error: {str(e)}")
    
    def detect_content_type(self, message):
        message_lower = message.lower()
        if "linkedin" in message_lower:
            return "LinkedIn Post"
        elif "instagram" in message_lower:
            return "Instagram Caption"
        elif "email" in message_lower:
            return "Email Copy"
        elif "product" in message_lower:
            return "Product Description"
        else:
            return "Content"
    
    def build_prompt(self, content_type, user_input):
        prompts = {
            "LinkedIn Post": f"Create a professional LinkedIn post about: {user_input}. Include hashtags.",
            "Instagram Caption": f"Write an Instagram caption for: {user_input}. Include emojis and hashtags.",
            "Email Copy": f"Write email copy about: {user_input}. Include subject line.",
            "Product Description": f"Write a product description for: {user_input}."
        }
        return prompts.get(content_type, f"Create content about: {user_input}")
    
    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            server_bot_dependencies={},
            allow_attachments=False,
            introduction_message="Welcome to Content Studio AI! I create LinkedIn Posts, Instagram Captions, Email Copy, and Product Descriptions.",
        )

if __name__ == "__main__":
    access_key = os.environ.get("POE_ACCESS_KEY", "")
    run(ContentGeneratorBot(), access_key=access_key)
