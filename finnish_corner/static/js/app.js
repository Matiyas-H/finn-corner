document.addEventListener("DOMContentLoaded", function () {
    
    // ------------ Global Variables ------------
    let chatId = "";
    let chatHistory = "";
    const User = "User";
    const AI = "AI";
    const userId = "jdh082312382992";
    let simpleMediaRecorder;
    let isSimpleRecording = false;
    
 // ------------ Event Listeners ------------

    document.getElementById('simpleRecordButton').addEventListener('click', toggleSimpleRecording);
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    

    // ------------ Messaging Functions ------------
    function sendMessage() {
        console.log("sendMessage() is called");
        const userMessage = document.getElementById('userMessage').value;
        const gptVersion = document.getElementById('gptVersion').value;
        const csrfToken = document.getElementById('csrfToken').value; 
        const scenarioId = getParameterByName('scenario_id'); 
    
        if (userMessage.trim() !== '') {
            displayMessage(User, userMessage);
            document.getElementById('userMessage').value = '';
    
            fetch('/app/text_chat/', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken // Sending CSRF token in the request headers
                },
                body: new URLSearchParams({
                    user_id: userId,
                    user_message: userMessage,
                    chat_id: chatId,
                    gpt_version: gptVersion,
                    scenario_id: scenarioId // Sending the scenario_id
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                chatHistory = data.chat_history;
                chatId = data.chat_id;
                displayMessage(AI, data.ai_message);
                fetchAudioFile(data.audio_id);
            })
            .catch(error => {
                console.error('Error sending message:', error);
            });
        }
    }

    function displayMessage(role, message) {
        const chatBox = document.getElementById('chatBox');
        chatBox.innerHTML += `<p>${role}: ${message}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }



// ------------ Recording Functions ------------

    function fetchAudioFile(audioId) {
        fetch('/app/get_audio/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                audio_id: audioId
            })
        })
        .then(response => response.blob())
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.src = audioUrl;
            audioPlayer.play();
        })
        .catch(error => {
            console.error('Error fetching audio file:', error);
        });
    }
    
    // ------------ Recording Functions ------------
    function toggleSimpleRecording() {
        console.log("simpleRecordButton() is called");
        if (!isSimpleRecording) {
            startSimpleRecording();
            document.getElementById('simpleRecordButton').textContent = 'Stop Recording';
        } else {
            stopSimpleRecording();
            document.getElementById('simpleRecordButton').textContent = 'Start Recording';
        }
        isSimpleRecording = !isSimpleRecording;
    }

    function startSimpleRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                simpleMediaRecorder = new MediaRecorder(stream);
                const chunks = [];
                simpleMediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        chunks.push(event.data);
                    }
                };

                simpleMediaRecorder.onstop = () => {
                    const audioBlob = new Blob(chunks, { type: 'audio/wav' });
                    sendSimpleAudio(audioBlob);
                };

                simpleMediaRecorder.start();
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
            });
    }

    function stopSimpleRecording() {
        if (simpleMediaRecorder && simpleMediaRecorder.state === 'recording') {
            simpleMediaRecorder.stop();
        }
    }
    

    // ------------ Audio Handling Functions ------------

    function sendSimpleAudio(audioBlob) {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('audio', audioBlob, 'audio.wav');
        formData.append('chat_id', chatId);
        formData.append('gpt_version', document.getElementById('gptVersion').value);
    
        // Adding scenario_id to the FormData
        const scenarioId = getParameterByName('scenario_id');
        if (scenarioId) {
            formData.append('scenario_id', scenarioId);
        }
    
        fetch('/app/speech_chat/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayMessage(User, data.user_message);
            displayMessage(AI, data.ai_message);
            fetchAudioFile(data.audio_id);
        })
        .catch(error => {
            console.error('Error uploading audio:', error);
        });
    }
    

    function playAudio(audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioPlayer = document.getElementById('audioPlayer');
        audioPlayer.src = audioUrl;
        audioPlayer.play();
    }

    
    // ------------ Utility Functions ------------
    
    function getParameterByName(name, url = window.location.href) {
        name = name.replace(/[\[\]]/g, '\\$&');
        var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, ' '));
    }
});