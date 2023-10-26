from django.urls import path

from . import views

app_name = "app"


urlpatterns = [
    path("", views.index, name="index"),
    path('select_scenario/', views.select_scenario, name='select_scenario'),
    path("text_chat/", views.text_chat, name="text_chat"),
    path("get_audio/", views.receive_audio, name="receive_audio"),
    path("speech_chat/", views.speech_chat, name="speech_chat"),
    path("clear_history/", views.clear_history, name="clear_history"),
    # path('scenario_text_chat/', views.scenario_text_chat, name='scenario_text_chat'),
]
