import os
import time
from pathlib import Path

from gtts import gTTS

from .models import Audio, Chat


def convert_to_audio(user_id, chat_id, text_content, lang="fi"):
    tts = gTTS(text_content, lang=lang)

    # Ensure the directory exists
    directory = Path("media/output")
    directory_absolute = directory.absolute()
    if not os.path.exists(directory_absolute):
        os.makedirs(directory_absolute)

    audio_filename = str(directory_absolute / f"{user_id}_{chat_id}_{int(time.time())}.wav")

    tts.save(audio_filename)

    with open(audio_filename, "rb") as f:
        audio_data = f.read()

    # Fetch the chat instance for the given user_id and chat_id
    try:
        chat_instance = Chat.objects.get(user_id=user_id, chat_id=chat_id)
    except Chat.DoesNotExist:
        # Handle exception if needed
        return

    audio = Audio(chat=chat_instance, type="INPUT", audio_data=audio_data)
    audio.save()

    return audio.id
