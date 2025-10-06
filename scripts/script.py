from dotenv import load_dotenv
import openai
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_motivational_text(prompt):
    try:
        response = openai.completions.create(
            model="gpt-4o-mini",
            prompt=f"You are a motivational speaker. Generate a 6-8 sentence inspiring speech on the theme: {prompt}. The speech should be direct, impactful, and without any greetings or pleasantries.",
            max_tokens=250,
            temperature=0.8,
        )

        return response.choices[0].text.strip()

    except Exception as e:
        print(f"❌ Error generating motivational text: {e}")
        return None
