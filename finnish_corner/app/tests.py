from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Audio, Chat


@pytest.mark.django_db
def test_index(client):
    response = client.get(reverse("index"))
    assert response.status_code == 200


@pytest.mark.django_db
@patch("myapp.views.chatgpt_proxy.text_chat")
@patch("myapp.views.gtts_proxy.convert_to_audio")
def test_text_chat(mock_convert_to_audio, mock_text_chat, client):
    mock_text_chat.return_value = ("Mocked AI Message", [])
    mock_convert_to_audio.return_value = 1

    response = client.post(
        reverse("text_chat"),
        {
            "user_message": "hello",
            "user_id": "1",
            "chat_id": "",
            "gpt_version": "4",
        },
    )
    assert response.status_code == 200


@pytest.mark.django_db
@patch("myapp.views.Audio.objects.get")
def test_receive_audio(mock_get, client):
    mock_audio = Audio()
    mock_audio.audio_data = b"mock_audio_data"
    mock_get.return_value = mock_audio

    response = client.post(reverse("receive_audio"), {"audio_id": 1})
    assert response.status_code == 200


@pytest.mark.django_db
@patch("myapp.views.openai.Audio.transcribe")
@patch("myapp.views.chatgpt_proxy.text_chat")
@patch("myapp.views.gtts_proxy.convert_to_audio")
def test_speech_chat(mock_convert_to_audio, mock_text_chat, mock_transcribe, client):
    mock_transcribe.return_value = {"text": "transcribed text"}
    mock_text_chat.return_value = ("Mocked AI Message", [])
    mock_convert_to_audio.return_value = 1

    audio_file = SimpleUploadedFile("file.wav", b"file_content", content_type="audio/wav")

    response = client.post(
        reverse("speech_chat"),
        {
            "user_id": "1",
            "chat_id": "",
            "gpt_version": "4",
            "audio": audio_file,
        },
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_clear_history(client):
    response = client.post(reverse("clear_history"), {"user_id": "1"})
    assert response.status_code == 200
