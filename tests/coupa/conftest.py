import pytest

@pytest.fixture(autouse=True)
def load_env():
    from dotenv import load_dotenv
    load_dotenv()