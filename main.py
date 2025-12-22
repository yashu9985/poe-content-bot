"""
Content Generator Bot for Poe - 100% FREE VERSION
Uses Google Gemini (No credit card needed!)
"""

from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
import google.generativeai as genai

class ContentGeneratorBot(PoeBot):
    
    def __init__(self):
        super().__init__()
        # Get FREE Gemini API key
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def get_response(self, request: QueryRequest):
        """Handle incoming messages and generate content"""
        
        user_message = request.query[-1].content
        content_type = self.detect_content_type(user_message)
        
        yield self.text_event(f"✨ Generating your {content_type}...\n\n")
        
        if not self.model:
            yield self.error_event("API not configured. Please contact bot owner.")
            return
        
        prompt = self.build_prompt(content_type, user_message)
        
        try:
            response = self.model.generate_content(prompt)
            yield self.text_event(response.text)
            
            yield self.text_event("\n\n---\n")
            yield self.text_event("💡 Made with FREE AI • Subscribe for premium features!\n")
            yield self.text_event("🔄 Want another version? Just ask!")
            
        except Exception as e:
            yield self.error_event(f"Error: {str(e)}")
    
    def detect_content_type(self, message):
        """Detect what type of content user wants"""
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
        """Build appropriate prompt based on content type"""
        
        prompts = {
            "LinkedIn Post": f"""Create a professional, engaging LinkedIn post about: {user_input}

Requirements:
- Hook readers in the first line
- Include valuable insights or tips
- Add relevant hashtags (5-7)
- Encourage engagement with a question
- Keep it authentic and professional
- Use line breaks for readability""",

            "Instagram Caption": f"""Write a captivating Instagram caption for: {user_input}

Requirements:
- Start with a hook that stops scrolling
- Include emojis naturally
- Add 15-20 relevant hashtags
- Create a call-to-action
- Match Instagram's casual, visual tone""",

            "Email Copy": f"""Write compelling email copy about: {user_input}

Requirements:
- Catchy subject line
- Personalized opening
- Clear value proposition
- Scannable format
- Strong call-to-action""",

            "Product Description": f"""Write a persuasive product description for: {user_input}

Requirements:
- Attention-grabbing headline
- Focus on benefits
- Address customer pain points
- Use sensory language
- Clear CTA"""
        }
        
        return prompts.get(content_type, f"Create engaging content about: {user_input}")
    
    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        """Bot settings"""
        return SettingsResponse(
            server_bot_dependencies={},
            allow_attachments=False,
            introduction_message="👋 **Welcome to Content Studio AI!**\n\nI create professional content for:\n\n📱 LinkedIn Posts\n📸 Instagram Captions\n📧 Email Copy\n🛍️ Product Descriptions\n\nJust tell me what you need!",
        )


if __name__ == "__main__":
    access_key = os.environ.get("POE_ACCESS_KEY", "")
    run(ContentGeneratorBot(), access_key=access_key)
```

---

## 2. Complete `requirements.txt` (Copy these 2 lines):
```
fastapi-poe==0.0.36
google-generativeai
