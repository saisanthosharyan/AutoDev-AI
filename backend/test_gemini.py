from google import genai

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one sentence."
)

print("=" * 50)
print(response)
print("=" * 50)

print("TEXT:")
print(response.text)