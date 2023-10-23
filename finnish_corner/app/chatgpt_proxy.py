import json
import logging
import os

import openai
from dotenv import load_dotenv

from . import gpt_prompt
from .models import Audio, Chat, Scenario

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def text_chat(user_message, user_id, chat_id, gpt_version):
    gpt_model = Chat.GPT3  # Default to GPT3
    if gpt_version == "GPT4":
        gpt_model = Chat.GPT4

    # Query chat record
    chat_record = None  # Initialize chat_record to None
    try:
        chat_record = Chat.objects.get(chat_id=chat_id, user_id=user_id)
        chat_history = json.loads(chat_record.chat_history)
    except Chat.DoesNotExist:
        chat_history = []

    # Request OpenAI
    ai_message, chat_history = requestOpenai(user_message, chat_history, gpt_model)

    chat_history_json = json.dumps(chat_history)

    # Update database
    if chat_record:  # If chat_record exists, then update it
        chat_record.chat_history = chat_history_json
        chat_record.save()
        logging.info(f"Update chat record->{str(chat_record)}")
    else:  # If not, create a new record
        chat_record = Chat(user_id=user_id, chat_id=chat_id, chat_history=chat_history_json)
        chat_record.save()
        logging.info(f"Add chat record->{str(chat_record)}")

    return ai_message, chat_history


def requestOpenai(chat_context, chat_history, model):
    if not chat_history:
        chat_history.append({"role": "system", "content": gpt_prompt.english_teacher_prompt})
    chat_history.append({"role": "user", "content": chat_context})
    print(f"openai chat request->{chat_history}")

    response = openai.ChatCompletion.create(model=model, messages=chat_history, temperature=0)

    print(f"openai chat response->{str(response)}")
    content_ = response.choices[0]["message"]["content"]
    chat_history.append({"role": "assistant", "content": content_})
    return content_, chat_history
