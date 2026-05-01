from services.chroma_client import ChromaClient

client = ChromaClient()

# Add sample data
client.add_data([
    "Unauthorized credit card transaction",
    "Phishing email asking for password",
    "Identity theft case reported"
])

# Query similar data
result = client.query("credit card fraud")

print("\nRESULT:\n", result)