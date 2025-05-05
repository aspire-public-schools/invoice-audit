from coupa.auth import get_access_token, update_env_file
import os

def test_update_env_file():
    test_token = "test_token_123"
    test_lifetime = "1234567890000"
    update_env_file(test_token, test_lifetime)
    with open('.env', 'r') as f:
        content = f.read()
        assert f"access_token={test_token}" in content
        assert f"token_life_time={test_lifetime}" in content

def test_get_access_token():
    token = get_access_token()
    assert token is not None and isinstance(token, str)