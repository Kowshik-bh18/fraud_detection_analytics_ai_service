from services.groq_client import GroqClient

client = GroqClient()

response = client.generate("Explain fraud detection in simple terms")

print("\n✅ Response:\n")
print(response)