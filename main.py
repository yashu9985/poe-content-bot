from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
import google.generativeai as genai


class ContentGeneratorBot(PoeBot):

    def __init__(self):
        super().__init__()

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def get_response(self, request: QueryRequest):
        yield self.text_event("✨ Generating content...\n\n")

        if not request.query:
            yield self.error_event("No input received")
            return

        user_message = request.query[-1].content.strip()
        content_type = self.detect_content_type(user_message)
        prompt = self.build_prompt(content_type, user_message)

        try:
            response = self.model.generate_content(prompt)
            yield self.text_event(response.text)
            yield self.text_event("\n\n💡 Want another version? Just ask!")

        except Exception as e:
            yield self.error_event(f"Gemini Error: {str(e)}")

    def detect_content_type(self, message: str):
        message = message.lower()
        if "linkedin" in message:
            return "LinkedIn Post"
        if "instagram" in message:
            return "Instagram Caption"
        if "email" in message:
            return "Email Copy"
        if "product" in message:
            return "Product Description"
        return "General Content"

    def build_prompt(self, content_type, user_input):
        return {
            "LinkedIn Post":
                f"Create a professional LinkedIn post about:\n{user_input}\nInclude hashtags.",
            "Instagram Caption":
                f"Write an Instagram caption with emojis and 10 hashtags for:\n{user_input}",
            "Email Copy":
                f"Write a professional email with subject line about:\n{user_input}",
            "Product Description":
                f"Write a persuasive product description for:\n{user_input}",
            "General Content":
                f"Create engaging content about:\n{user_input}",
        }[content_type]

    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            allow_attachments=False,
            introduction_message=(
                "👋 Welcome to Content Studio AI!\n\n"
                "I can generate:\n"
                "📱 LinkedIn Posts\n"
                "📸 Instagram Captions\n"
                "📧 Email Copy\n"
                "🛍️ Product Descriptions\n\n"
                "Just tell me what you need!"
            ),
        )


if __name__ == "__main__":
    run(
        ContentGeneratorBot(),
        access_key=os.environ["POE_ACCESS_KEY"]
    )
