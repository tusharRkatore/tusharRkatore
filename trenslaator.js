// Translate recognized subject and body
document.getElementById('translateBtn').addEventListener('click', () => {
    const subjectText = document.getElementById('recognizedSubject').value;
    const bodyText = document.getElementById('recognizedBody').value;
    const outputLang = document.getElementById('outputLang').value;

    const translateText = (text, lang, callback) => {
        fetch('/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                outputLang: lang
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Translation failed');
            }
            return response.json();
        })
        .then(data => callback(data.translated))
        .catch(error => alert(`Error: ${error.message}`));
    };

    // Translate subject
    translateText(subjectText, outputLang, (translatedSubject) => {
        document.getElementById('translatedSubject').value = translatedSubject;
    });

    // Translate body
    translateText(bodyText, outputLang, (translatedBody) => {
        document.getElementById('translatedBody').value = translatedBody;
    });
});

// Recognize Email Subject
document.getElementById('speakSubjectBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: false,  // Start fresh for the subject
            isSubject: true
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('recognizedSubject').value = data.text;
    })
    .catch(error => alert(`Error: ${error.message}`));
});

// Continue Recognizing Email Subject (Append new speech)
document.getElementById('continueSubjectBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: true,  // Append new text to the existing subject
            isSubject: true
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('recognizedSubject').value = data.text;
    })
    .catch(error => alert(`Error: ${error.message}`));
});

// Recognize Email Body
document.getElementById('speakBodyBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: false,  // Start fresh for the body
            isSubject: false
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('recognizedBody').value = data.text;
    })
    .catch(error => alert(`Error: ${error.message}`));
});

// Continue Recognizing Email Body (Append new speech)
document.getElementById('continueBodyBtn').addEventListener('click', () => {
    fetch('/start_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            inputLang: document.getElementById('inputLang').value,
            append: true,  // Append new text to the existing body
            isSubject: false
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('recognizedBody').value = data.text;
    })
    .catch(error => alert(`Error: ${error.message}`));
});

// Stop recognition manually
document.getElementById('stopBtn').addEventListener('click', () => {
    fetch('/stop_recognition', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('recognizedSubject').value = data.recognizedSubject;
        document.getElementById('recognizedBody').value = data.recognizedBody;
    })
    .catch(error => alert(`Error: ${error.message}`));
});

// Send email
document.getElementById('sendEmailBtn').addEventListener('click', () => {
    const recipientEmail = document.getElementById('recipientEmail').value;

    fetch('/send_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            recipientEmail: recipientEmail
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to send email');
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => alert(`Error: ${error.message}`));
});
