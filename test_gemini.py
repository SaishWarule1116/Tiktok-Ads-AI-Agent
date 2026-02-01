import os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')
client = genai.Client(api_key=API_KEY)

try:
    print("Listing models...")
    for m in client.models.list():
        print(f"Model name: {m.name}")
except Exception as e:
    print(f"Failed to list models: {e}")

try:
    print("\nTesting with simple prompt and model='gemini-1.5-flash'...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )
    print(f"Success! Response: {response.text}")
except Exception as e:
    print(f"Failed with gemini-1.5-flash: {e}")

