from mistral.uploader import client

def ask_pdf_questions(prompt_text: str, document_url: str, model_name: str = "mistral-small-latest") -> str:
    """
    Submit a prompt and a document URL to Mistral and return the response text.
    """
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "document_url", "document_url": document_url}
            ],
        }
    ]

    chat_response = client.chat.complete(
        model=model_name,
        messages=messages,
    )

    return chat_response.choices[0].message.content
