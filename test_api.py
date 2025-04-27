import openai
from dotenv import load_dotenv
import os
import pathlib

# Debug: Print current directory
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for .env in: {pathlib.Path().absolute()}")

# Load environment variables
load_dotenv(verbose=True)  # Added verbose=True for debugging

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ No API key found in environment!")
else:
    print(f"Found API key starting with: {api_key[:7]}...")

# Set API key
openai.api_key = api_key

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=10
    )
    print("✅ API test successful!")
    print("Response:", response.choices[0].message.content)
except openai.error.AuthenticationError:
    print("❌ Authentication Error: Your API key is invalid")
except openai.error.RateLimitError:
    print("❌ Rate Limit Error: You've hit your rate limit")
except Exception as e:
    print(f"❌ Other Error: {str(e)}")
