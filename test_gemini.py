from backend.answer_generator import client, MODEL_NAME

response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Explain what a contract is in two sentences."
)

print(response.text)