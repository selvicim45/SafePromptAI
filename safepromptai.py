#*****************************************************************************************
# __________________________________SafePromptAI_________________________________________
#  Microsoft Hackathon March 2025
#  Programmars: Arulselvi Amirrthalingam(Selvi) and Selvamani Ramasamy
#  Challenge: Auto Correct and Prompt Validation Before AI Execution
#  Backend (Python,Flask,Azure AI Services)
#*****************************************************************************************
from azure.cognitiveservices.vision.contentmoderator import ContentModeratorClient
from dotenv import load_dotenv
import os
import io
import re
from flask_cors import CORS
from flask import Flask, request, jsonify
import openai
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials
import azure.cognitiveservices.speech as speechsdk
import tempfile

# Load the .env file
load_dotenv()

# Access the environment variables
azure_key = os.getenv("AZURE_KEY")
azure_endpoint = os.getenv("AZURE_ENDPOINT")
openai_api_key = os.getenv("OPENAI_API_KEY")
speech_key = os.getenv("SPEECH_KEY")  # Azure Speech API Key
speech_region = os.getenv("SPEECH_REGION")  # Azure Speech Region

#client = OpenAI(api_key=openai_api_key)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for the app
CORS(app)

# Initialize Azure Text Analytics Client
text_analytics_client = TextAnalyticsClient(endpoint=azure_endpoint,
                                            credential=AzureKeyCredential(azure_key))

# Initialize Content Moderator Client with CognitiveServicesCredentials
content_moderator_client = ContentModeratorClient(endpoint=azure_endpoint, credentials=CognitiveServicesCredentials(azure_key))

#To receive user approval from frontend
@app.route('/check_pii', methods=['POST'])
def check_pii():
    data = request.json
    input_text = data.get("input", "")

    # Call the function to check for PII
    contains_pii, pii_categories, pii_entities = check_for_pii(input_text)

    # Send back the result to the frontend
    return jsonify({
        "contains_pii": contains_pii,
        "pii_categories": pii_categories,
        "pii_entities": pii_entities  # Send specific PII entities
    })
#Step 1 PII detection
# Function to check for PII using Azure's Language AI service
def check_for_pii(text):
    try:
        # Call Azure's PII detection service to recognize PII entities
        pii_result = text_analytics_client.recognize_pii_entities([text], language="en")

        pii_categories = []
        pii_entities = []

        # Loop through the detected entities and categorize them
        for doc in pii_result:
            if doc.is_error:
                print(f"Error processing document: {doc.error}")
                continue

            for entity in doc.entities:
                # Check for PII entities and their categories
                print(f"Detected PII Entity: {entity.text}, Category: {entity.category}")
                if entity.category not in pii_categories:
                    pii_categories.append(entity.category)
                pii_entities.append(entity.text)  # Add the entity itself to the list

        if pii_entities:
            # Return True if PII is found along with the categories and entities
            return True, pii_categories, pii_entities
        else:
            # No PII detected
            return False, [], []

    except Exception as e:
        print(f"Error: {e}")
        return False, [], []


@app.route('/process', methods=['POST'])
def process_input():
    try:
        user_input = request.json.get('input')
        #print("Received user input:", user_input)

        if not user_input:
            return jsonify({"error": "No input provided"}), 400


        # Step 2: Analyze Sentiment (this is based on user entered original prompt)
        sentiment = analyze_sentiment(user_input)

        # Step 3: Check for harmful language using Azure Content Moderator
        is_safe, safe_input, harmful_terms = check_harmful_language(user_input )

        # Always return the safe_input regardless of harmful content
        response_data = {
            "safe_input": safe_input,
            "is_safe": is_safe
        }

        # If harmful content is detected, return a message and suggested clean prompt
        if not is_safe:
            harmful_terms_message = ", ".join(harmful_terms) if harmful_terms else "No specific harmful terms detected."
            response_data["message"] = f"Inappropriate content detected. Please revise your input. Harmful terms: {harmful_terms_message}"


        # Step 4: Enhance clarity using GPT (OpenAI or Azure OpenAI)
        clarified_input = enhance_clarity(safe_input)

        # Step 5: Send the final prompt to the AI model (Optional - this is where you can integrate GPT)
        ai_response = get_ai_response(clarified_input, sentiment)

        # Add AI response and clarified input to the response
        response_data.update({
            "clarified_input": clarified_input,
            "ai_response": ai_response,
            "sentiment": sentiment
        })

        # Do NOT generate audio here anymore.
        response_data["audio_url"] = None  # Placeholder for audio URL; no audio generation at this point.

        return jsonify(response_data)

    except Exception as e:
        print(f"error in process input{e}")
        return jsonify({"error": str(e)}), 400


# Function for Sentiment Analysis
def analyze_sentiment(text):
    try:
        # Call Azure Text Analytics API for sentiment analysis
        response = text_analytics_client.analyze_sentiment([text])
        sentiment = response[0].sentiment  # 'positive', 'neutral', or 'negative'
        return sentiment
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return "unknown"

# Content Moderator Function with Sanitization
def check_harmful_language(text):
    harmful_terms = []  # List to collect harmful terms

    # Convert the string into a file-like object (StringIO)
    file_like_text = io.StringIO(text)

    # Using Azure Content Moderator to check for harmful content
    response = content_moderator_client.text_moderation.screen_text(
        text_content_type="text/plain",  # or whatever content type is relevant
        text_content=file_like_text,  # pass the file-like object here
        language="eng"  # language code for English
    )

    # If harmful terms are detected, store them in the harmful_terms list
    if response.terms:
        for term in response.terms:
            harmful_terms.append(term.term)
    clean_terms= get_clean_terms_from_gpt(harmful_terms)
    # If harmful terms are detected, sanitize the text
    if harmful_terms:
        safe_text= replace_harmful_terms_with_clean_input(text, harmful_terms, clean_terms)
        #safe_text = sanitize_text(text, harmful_terms)  # Redact the harmful terms
        return False, safe_text, harmful_terms  # Return False with sanitized text

    return True, text, harmful_terms  # Return True if no harmful terms are detected


# Function to send harmful terms to GPT for cleaner alternatives
def get_clean_terms_from_gpt(harmful_terms):
    clean_terms = []
    for harmful_term in harmful_terms:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant that helps make language safer."},
                {"role": "user", "content": f"Please suggest a cleaner word for: {harmful_term}"}
            ]
        )
        clean_term = response.choices[0].message.content.strip()
        clean_terms.append(clean_term)

    return clean_terms

# Function to replace harmful terms with clean alternatives in the text
def replace_harmful_terms_with_clean_input(text, harmful_terms, clean_terms):
    for harmful, clean in zip(harmful_terms, clean_terms):
        text = re.sub(rf'\b{re.escape(harmful)}\b', clean, text, flags=re.IGNORECASE)
    return text

# Clarity Enhancement (Optional: GPT or OpenAI Model)
def enhance_clarity(text):
    # Using the new OpenAI API method to rephrase the text to make it clearer
    response = openai.chat.completions.create(model="gpt-4",  # Or use "gpt-3.5-turbo" depending on the model you want
        messages=[
            {"role": "system", "content": "You are an assistant that helps improve clarity."},
            {"role": "user", "content": f"Rewrite the following to make it clearer: {text}"}
        ])
    clarified_text = response.choices[0].message.content.strip()
    return clarified_text

# AI Response Generation based on sentiment
def get_ai_response(prompt, sentiment):
    response_message = ""
    if sentiment == "negative":
        response_message = "I'm sorry to hear that you're upset."
    elif sentiment == "positive":
        response_message = "I'm happy to hear you're feeling good!"
    else:
        response_message = "I see you're feeling ok "

    # Using OpenAI API to generate a more context-aware AI response
    response =openai.chat.completions.create(
        model="gpt-4",  # Or use "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )

    ai_response = response.choices[0].message.content.strip()
    return f"{response_message}: {ai_response}"

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        first_text = data.get('first_text')
        second_text = data.get('second_text')

        if not first_text:
            return jsonify({"error": "Text for audio generation is required."}), 400

        # Call read_aloud to generate the audio
        audio_url = read_aloud(first_text, second_text)

        if audio_url:
            return jsonify({"audio_url": audio_url})
        else:
            return jsonify({"error": "Failed to generate audio."}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Assuming the backend is already generating the audio correctly and returning the audio URL
def read_aloud(first_text, second_text=None):
    # Initialize speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

    # Set the voice language and type
    speech_config.speech_synthesis_voice_name = "en-US-JessaNeural"

    # Initialize the synthesizer with the speech configuration
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Prepare the final text to be spoken
    text_to_read = first_text + (f" {second_text}" if second_text else "")

    # Create a temporary file to store the audio output
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        audio_filename = temp_audio_file.name

        # Use the synchronous function to generate audio
        result = synthesizer.speak_text(text_to_read)

        # Ensure the result is successful before proceeding
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Return the path to the audio file
            return f"http://127.0.0.1:5000/audio/{os.path.basename(audio_filename)}"
        else:
            print(f"Audio synthesis failed: {result.reason}")
            return None  # Return None if the synthesis failed

if __name__ == "__main__":
    app.run(debug=True)








