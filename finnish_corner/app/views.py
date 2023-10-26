import io
import json
import os.path
import time
from pathlib import Path

import openai
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from dotenv import load_dotenv
from . import chatgpt_proxy, gtts_proxy
from .models import Audio, Chat, Scenario

from django.views.decorators.csrf import csrf_exempt
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def index(request):
    return render(request, "app/index.html")


def select_scenario(request):
    scenarios = Scenario.objects.all()
    return render(request, 'app/scenario.html', {'scenarios': scenarios})



@require_POST
def text_chat(request):
    user_message = request.POST["user_message"]
    user_id = request.POST["user_id"]
    chat_id = request.POST["chat_id"]
    scenario_id = request.POST.get("scenario_id")  # Get the scenario_id from the POST request
    print(scenario_id)
    if not chat_id:
        chat_id = str(abs(hash(user_message)))
    
    gpt_version = request.POST["gpt_version"]

    # Ensure chat record exists at the start
    chat_record, created = Chat.objects.get_or_create(user_id=user_id, chat_id=chat_id)
    
    if created:
        chat_record.chat_history = json.dumps([])  
        if scenario_id:  # Check if a scenario_id exists
            try:
                scenario = Scenario.objects.get(id=scenario_id)
                starter_message = {"role": "system", "content": scenario.starter_prompt}
                
                if created:
                    chat_record.chat_history = json.dumps([starter_message])
                else:
                    chat_history = json.loads(chat_record.chat_history)
                    chat_history.append(starter_message)
                    chat_record.chat_history = json.dumps(chat_history)
                
                chat_record.save()
                
            except Scenario.DoesNotExist:
                return JsonResponse({"error": "Invalid scenario ID."}, status=400)


    ai_message, chat_history = chatgpt_proxy.text_chat(user_message, user_id, chat_id, gpt_version)
    audio_id = gtts_proxy.convert_to_audio(user_id, chat_id, ai_message, "en")

    return JsonResponse(
        {
            "ai_message": ai_message,
            "chat_history": chat_history,
            "audio_id": audio_id,
            "chat_id": chat_id,
        }
    )





@csrf_exempt
@require_POST
def receive_audio(request):
    audio_id = request.POST["audio_id"]

    try:
        audio = Audio.objects.get(pk=audio_id)
    except Audio.DoesNotExist:
        raise Http404("Audio not found.")

    audio_data = io.BytesIO(audio.audio_data)

    # Send audio data as a response
    response = FileResponse(audio_data, content_type="audio/wav")
    response["Content-Disposition"] = f"attachment; filename={audio_id}.wav"

    return response


@csrf_exempt
@require_POST
def speech_chat(request):
    try:
        user_id = request.POST.get("user_id")
        chat_id = request.POST.get("chat_id")
        gpt_version = request.POST.get("gpt_version")
        scenario_id = request.POST.get("scenario_id")  # Fetching the scenario ID from POST data
        
        directory = Path("media/input")
        directory_absolute = directory.absolute()
        if not os.path.exists(directory_absolute):
            os.makedirs(directory_absolute)
        audio_file = request.FILES["audio"]

        # Save the audio file to a specific directory
        fs = FileSystemStorage()
        filename = fs.save("input/" + user_id + "_" + chat_id + "_" + str(time.time()) + ".wav", audio_file)

        # Get the absolute path to the saved audio file
        audio_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Transcribe the audio
        with open(audio_path, "rb") as audio_to_transcribe:
            res = openai.Audio.transcribe(file=audio_to_transcribe, model="whisper-1")
        chat_text = res["text"]

        if not chat_id:
            chat_id = str(abs(hash(chat_text)))
        
        chat_record, created = Chat.objects.get_or_create(user_id=user_id, chat_id=chat_id)

        # Inject the scenario starter message if a scenario is selected and the chat is newly created
        if created and scenario_id:
            try:
                scenario = Scenario.objects.get(id=scenario_id)
                starter_message = {"role": "system", "content": scenario.starter_prompt}
                chat_history = json.loads(chat_record.chat_history) if chat_record.chat_history else []
                chat_history.append(starter_message)
                chat_record.chat_history = json.dumps(chat_history)
                chat_record.save()
            except Scenario.DoesNotExist:
                return JsonResponse({"error": "Invalid scenario ID."}, status=400)
            
        # Request chat response
        ai_message, chat_history = chatgpt_proxy.text_chat(chat_text, user_id, chat_id, gpt_version)

        # Convert the AI's response to audio
        audio_id = gtts_proxy.convert_to_audio(user_id, chat_id, ai_message, "en")

        return JsonResponse(
            {
                "user_message": chat_text,
                "ai_message": ai_message,
                "audio_id": audio_id,
                "chat_id": chat_id,
            }
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

def clear_history(request):
    user_id = request.POST.get("user_id")

    # Clear chat history for the given user ID
    Chat.objects.filter(user_id=user_id).delete()

    return JsonResponse({"message": "History cleared successfully"})