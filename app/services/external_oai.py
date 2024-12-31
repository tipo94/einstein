import requests

def send_audio_for_processing(audio_file_path: str) -> dict:
    """
    Example function to send audio to an external service.
    Adapt this to match the actual external API you're calling.
    """
    url = "https://api.example.com/v1/transcribe"

    # If the external API requires specific headers, tokens, etc., provide them here:
    headers = {
        "Authorization": "Bearer <your_token_here>",
    }

    # Some services accept multipart/form-data
    files = {
        'file': open(audio_file_path, 'rb')
    }

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        # Raise exception or handle error
        raise Exception(f"Error from external service: {response.text}")
