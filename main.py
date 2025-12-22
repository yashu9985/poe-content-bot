from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest, SettingsRequest, SettingsResponse
import os
import google.generativeai as genai


class ContentGeneratorBot(PoeBot):

    def __init__(self):
        super().__init__()

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing")

        genai.configure(api_key=api_key)

        # ✅ THIS IS THE FIX
        self.model = genai.GenerativeModel("gemini-1.0-pro")

    async def get_response(self, request: QueryRequest):
        yield self.text_event("✨ Generating content...\n\n")

        if not request.query:
            yield self.error_event("No input received")
            return

        user_message = request.query[-1].content.strip()
        prompt = self.build_prompt(user_message)

        try:
            response = self.model.generate_content(prompt)
            yield self.text_event(response.text)
        except Exception as e:
            yield self.error_event(f"Gemini Error: {str(e)}")

    def build_prompt(self, user_input):
        return f"Create high-quality content for the following request:\n{user_input}"

    async def get_settings(self, setting: SettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            allow_attachments=False,
            introduction_message="👋 Content Studio AI ready!"
        )


if __name__ == "__main__":
    run(ContentGeneratorBot(), access_key=os.environ["POE_ACCESS_KEY"])
