from django.db import models


class Scenario(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starter_prompt = models.TextField()

    def __str__(self):
        return self.title


class Chat(models.Model):
    GPT4 = "gpt-4-0613"
    GPT3 = "gpt-3.5-turbo-0613"
    CHAT_GPT_MODELS = [
        (GPT4, "GPT-4 Model"),
        (GPT3, "GPT-3.5 Turbo Model"),
    ]
    user_id = models.CharField(max_length=80)
    chat_id = models.CharField(max_length=80)
    chat_history = models.TextField()
    model_type = models.CharField(max_length=20, choices=CHAT_GPT_MODELS, default=GPT3)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="chats", null=True, blank=True)

    def __str__(self):
        return self.chat_id


class Audio(models.Model):
    INPUT = "input"
    OUTPUT = "output"
    AUDIO_TYPES = [
        (INPUT, "Input"),
        (OUTPUT, "Output"),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="audios")
    type = models.CharField(max_length=6, choices=AUDIO_TYPES, default=INPUT)
    audio_data = models.BinaryField()
