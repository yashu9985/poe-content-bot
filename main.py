from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
from groq import Groq

class ContentGeneratorBot(PoeBot):
    
    def __init__(self):
        super().__init__()
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
        else:
            self.client = None
    
    async def get_response(self, request: QueryRequest):
        user_message = request.query[-1].content
        content_type = self.detect_content_type(user_message)
        
        if not self.client:
            yield self.error_event("Bot not configured properly")
            return
        
        prompt = self.build_prompt(content_type, user_message)
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional content writer who creates engaging social media posts, emails, and product descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024
            )
            
            yield self.text_event(completion.choices[0].message.content)
            yield self.text_event("\n\nWant another version? Just ask!")
            
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
            "LinkedIn Post": f"Create a professional, engaging LinkedIn post about: {user_input}\n\nRequirements:\n- Hook readers in first line\n- Include 5-7 relevant hashtags\n- Keep it professional yet conversational\n- Add a question to encourage engagement",
            
            "Instagram Caption": f"Write a captivating Instagram caption for: {user_input}\n\nRequirements:\n- Start with an attention-grabbing hook\n- Include emojis naturally\n- Add 15-20 relevant hashtags at the end\n- Include a call-to-action",
            
            "Email Copy": f"Write compelling email copy about: {user_input}\n\nRequirements:\n- Catchy subject line (start with 'Subject:')\n- Personalized opening\n- Clear value proposition\n- Strong call-to-action\n- Professional yet friendly tone",
            
            "Product Description": f"Write a persuasive product description for: {user_input}\n\nRequirements:\n- Attention-grabbing headline\n- Focus on benefits not just features\n- Address customer pain points\n- Use sensory, emotional language\n- Clear call-to-action"
        }
        
        return prompts.get(content_type, f"Create engaging, professional content about: {user_input}")
    
    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            server_bot_dependencies={},
            allow_attachments=False,
            introduction_message="Welcome to Content Studio AI!\n\nI create professional content for:\n\n- LinkedIn Posts\n- Instagram Captions\n- Email Copy\n- Product Descriptions\n\nJust tell me what you need! For example:\n'Create a LinkedIn post about AI in healthcare'\n'Write an Instagram caption for my coffee shop'",
        )

if __name__ == "__main__":
    access_key = os.environ.get("POE_ACCESS_KEY", "")
    run(ContentGeneratorBot(), access_key=access_key)
