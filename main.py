from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
from google import genai

class ContentGeneratorBot(PoeBot):
    
    def __init__(self):
        super().__init__()
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
    
    async def get_response(self, request: QueryRequest):
        yield self.text_event("✨ ")
        
        user_message = request.query[-1].content
        content_type = self.detect_content_type(user_message)
        
        if not self.client:
            yield self.error_event("Bot not configured properly")
            return
        
        prompt = self.build_prompt(content_type, user_message)
        
        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            
            yield self.text_event(response.text)
            yield self.text_event("\n\n💡 Want another version? Just ask!")
            
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
            "Instagram Caption": f"Write an Instagram caption for: {user_input}. Include emojis and 10 hashtags.",
            "Email Copy": f"Write email copy about: {user_input}. Include subject line.",
            "Product Description": f"Write a compelling product description for: {user_input}."
        }
        return prompts.get(content_type, f"Create engaging content about: {user_input}")
    
    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            server_bot_dependencies={},
            allow_attachments=False,
            introduction_message="👋 Welcome to Content Studio AI!\n\nI create:\n📱 LinkedIn Posts\n📸 Instagram Captions\n📧 Email Copy\n🛍️ Product Descriptions\n\nJust tell me what you need!",
        )

if __name__ == "__main__":
    access_key = os.environ.get("POE_ACCESS_KEY", "")
    run(ContentGeneratorBot(), access_key=access_key)
```

---

## `requirements.txt`
```
fastapi-poe==0.0.36
google-genai
