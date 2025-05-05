from mistral import prompts
from unittest.mock import patch

@patch("mistral.prompts.client.chat.complete")
def test_ask_pdf_questions(mock_complete):
    mock_complete.return_value.choices = [
        type("MockChoice", (), {"message": type("MockMsg", (), {"content": "mocked response"})})()
    ]
    response = prompts.ask_pdf_questions("What is this?", "https://fake.url")
    assert response == "mocked response"
