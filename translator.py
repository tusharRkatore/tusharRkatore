import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import speech_recognition as sr
from flask import Flask, jsonify, render_template, request
from googletrans import Translator

app = Flask(__name__)

recognizer = sr.Recognizer()
translator = Translator()

# Email configuration (use environment variables for sensitive data)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('SENDER_EMAIL')  # Set your email in environment variables
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # Set your password in environment variables

# Function to translate text
def translate_text(text, output_lang):
    try:
        translation = translator.translate(text, dest=output_lang)
        return translation.text
    except Exception as e:
        return f"Error: Failed to translate text. {str(e)}"

# Global variables to store recognized text
recognized_subject = ""
recognized_body = ""

# Function to convert speech to text
def speech_to_text(input_lang, append=False, is_subject=True):
    global recognized_subject, recognized_body

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Listening... (will stop after 5 seconds of silence)")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language=input_lang)

            if is_subject:  # If recognizing subject
                if append:  # Append to existing subject
                    recognized_subject += " " + text
                else:
                    recognized_subject = text
                print(f"Recognized Subject: {recognized_subject}")
                return recognized_subject
            else:  # If recognizing body
                if append:  # Append to existing body
                    recognized_body += " " + text
                else:
                    recognized_body = text
                print(f"Recognized Body: {recognized_body}")
                return recognized_body
        except sr.UnknownValueError:
            return "Error: Could not understand the audio."
        except sr.WaitTimeoutError:
            return "Error: No speech detected, stopping."
        except sr.RequestError as e:
            return f"Error: Could not request results from Google Speech Recognition service; {e}"

# Function to send email
def send_email(recipient_email, subject, body_text):
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach the body text
    message.attach(MIMEText(body_text, 'plain'))

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        # Connect to the server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Main API routes
@app.route('/')
def home():
    return render_template('index.html')

# Start speech recognition route
@app.route('/start_recognition', methods=['POST'])
def start_recognition():
    data = request.get_json()  # Use get_json() to properly parse JSON
    input_lang = data.get('inputLang', 'en')
    append = data.get('append', False)  # Check if we want to append the new text to previous one
    is_subject = data.get('isSubject', True)  # Determine if recognizing subject or body

    recognized_text_result = speech_to_text(input_lang, append, is_subject)

    if "Error" in recognized_text_result:
        return jsonify({'error': recognized_text_result}), 400
    else:
        return jsonify({'text': recognized_text_result})

# Stop recognition route
@app.route('/stop_recognition', methods=['POST'])
def stop_recognition():
    return jsonify({'message': 'Recognition stopped', 'recognizedSubject': recognized_subject, 'recognizedBody': recognized_body}), 200

# Translation route
@app.route('/translate', methods=['POST'])
def translate_text_route():
    data = request.get_json()  # Use get_json() to properly parse JSON
    text = data.get('text', '')
    output_lang = data.get('outputLang', 'en')

    translated_text = translate_text(text, output_lang)

    if "Error" in translated_text:
        return jsonify({'error': translated_text}), 500
    else:
        return jsonify({'translated': translated_text})

# Route to handle sending email
@app.route('/send_email', methods=['POST'])
def send_email_route():
    data = request.get_json()  # Use get_json() to properly parse JSON
    recipient_email = data.get('recipientEmail')

    # Translate subject and body before sending
    translated_subject = translate_text(recognized_subject, 'en')  
    translated_body = translate_text(recognized_body, 'en')  

    # Send email with the translated subject and body
    send_email(recipient_email, translated_subject, translated_body)
    return jsonify({'message': 'Email sent successfully!'})

if __name__ == '__main__':
    app.run(debug=True, port=5500)
