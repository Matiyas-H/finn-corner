import json
from .models import Chat


def get_user_chat(request, chat_id):
    if request.user.is_authenticated:
        try:
            chat_record = Chat.objects.get(chat_id=chat_id, auth_user=request.user)
            return json.loads(chat_record.chat_history)
        except Chat.DoesNotExist:
            return []
    else:
        return json.loads(request.session.get(chat_id, json.dumps([])))

def save_user_chat(request, chat_id, chat_data):
    if request.user.is_authenticated:
        chat_record, created = Chat.objects.get_or_create(chat_id=chat_id, auth_user=request.user)
        chat_record.chat_history = json.dumps(chat_data)
        chat_record.save()
    else:
        request.session[chat_id] = json.dumps(chat_data)
