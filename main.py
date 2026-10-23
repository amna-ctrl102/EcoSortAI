
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY .env file mein nahi mili.")

client = genai.Client(api_key=api_key)

try:
    print("Step 1: Uploading image...")

    uploaded_image = client.files.upload(
        file="test_waste.jpg"
    )

    print("Image upload successful!")
    print("Step 2: Sending image to Gemma 4...")

    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it",
        contents=[
            uploaded_image,
            "Identify the waste in this image. "
            "For each item, state its material, whether it is "
            "recyclable, and one safe disposal tip. "
            "Use simple English."
        ]
    )

    print("\nEcoSort AI Recycling Guide:\n")
    print(response.text)

except Exception as e:
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {e}")
