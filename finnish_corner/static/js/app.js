document.addEventListener("DOMContentLoaded", function() {

    // Global Variables
    let chatId = "";
    let chatHistory = "";
    const User = "User";
    const AI = "AI";
    const userId = "jdh082312382992";
    let simpleMediaRecorder;
    let isSimpleRecording = false;

    // Event Listener for the record button
    document.getElementById('simpleRecordButton').addEventListener('click', toggleSimpleRecording);

    function displayMessage(role, message) {
        const chatBox = document.getElementById('chatBox');
        chatBox.innerHTML += `<p>${role}: ${message}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    document.getElementById('sendButton').addEventListener('click', sendMessage);
    function sendMessage() {
        console.log("sendMessage() is called");
        const userMessage = document.getElementById('userMessage').value;
        const gptVersion = document.getElementById('gptVersion').value;
        const csrfToken = document.getElementById('csrfToken').value; // Fetching CSRF token

        if (userMessage.trim() !== '') {
            displayMessage(User, userMessage);
            document.getElementById('userMessage').value = '';

            fetch('/app/text_chat/', { // Make sure the endpoint is correct
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken // Sending CSRF token in the request headers
                },
                body: new URLSearchParams({
                    user_id: userId,
                    user_message: userMessage,
                    chat_id: chatId,
                    gpt_version: gptVersion
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
    document.getElementById('simpleRecordButton').addEventListener('click', toggleSimpleRecording);
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

    function sendSimpleAudio(audioBlob) {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('audio', audioBlob, 'audio.wav');
        formData.append('chat_id', chatId);
        formData.append('gpt_version', document.getElementById('gptVersion').value);

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

    function sendAudio(formData) {
        fetch('/app/speech_chat/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            chatHistory = data.chat_history;
            chatId = data.chat_id;
            displayMessage(User, data.user_message);
            displayMessage(AI, data.ai_message);
            fetchAudioFile(data.audio_id);
        })
        .catch(error => {
            console.error('Error uploading audio:', error);
        });
    }

    function fetchAudioFile(audioId) {
        fetch('/app/get_audio/', { // Make sure the endpoint is correct
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

});
