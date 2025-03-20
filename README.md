# SafePrompt AI

**SafePrompt AI** is a prompt refinement solution designed to filter harmful language, enhance clarity, and ensure safe AI interactions. It leverages Azure AI services to detect and sanitize personally identifiable information (PII), moderate content, and improve user-generated prompts before they are processed by AI models.

The project integrates **Azure AI Content Moderator**, **Azure Text Analytics**, and **Azure Speech Services** to analyze and refine user input. Harmful or inappropriate content is detected and replaced with cleaner alternatives, ensuring compliance with ethical AI usage without changing the core of user intent and sentiment. This project helps ensure that AI-generated content remains safe, inclusive, and free from harmful biases.

## Features

- **PII Detection**: Uses Azure AI Text Analytics to detect personally identifiable information (PII) in user input. Users are prompted to either proceed or revise their prompt, ensuring PII is neither stored nor shared.
- **Content Moderation**: Azure AI Content Moderator detects harmful or inappropriate language.
- **Harmful Terms Replacement**: OpenAI finds suitable terms and replaces harmful terms.
- **Prompt Refinement**: OpenAI enhances the clarity of user prompts without changing the core intent of the original prompt and corrects grammar before submission to an AI model.
- **React and Flask Web Application**: Provides an interactive interface for seamless backend and frontend communication.
- **Audio Accessibility**: Allows users to play AI responses using Azure Cognitive Speech Services.

## Tech Stack

- **Azure AI Text Analytics**
- **Azure AI Content Moderator**
- **Azure AI Speech Services**
- **OpenAI API (GPT-4)**
- **CSS for UI Styling**
- **React**
- **Flask**

## Environment Variables

To run this project, add the following environment variables to your `.env` file. Ensure these resources are created in Azure before running the application:

```bash
AZURE_KEY=<Your Azure API Key>
AZURE_ENDPOINT=<Your Azure API Endpoint>
OPENAI_API_KEY=<Your OpenAI API Key>
SPEECH_KEY=<Your Azure Speech API Key>
SPEECH_REGION=<Your Azure Speech Region>
```
## Run Locally (You will need to set up the Azure Resources)

1. **Clone the project**
    ```bash
    git clone https://github.com/selvicim45/SafePromptAI.git
    ```

2. **Install dependencies**

    - **Install Python dependencies:**
      ```bash
      pip install -r requirements.txt
      pip install flask
      pip install flask-cors
      pip install azure-cognitiveservices-vision-contentmoderator
      pip install openai
      pip install python-dotenv
      pip install msrest
      pip install azure-cognitiveservices-speech
      pip install azure-ai-textanalytics
      pip install azure-core
      ```

    - **Install Node.js dependencies:**
      ```bash
      npm install
      ```

3. **Start the frontend server**
    ```bash
    npm run start
    ```

4. **Go to the project directory for the backend**
    ```bash
    cd backend
    ```

5. **Start the backend server**
    ```bash
    flask run
    ```

## Future Improvements

- **Multi-Language Support**: To provide multi-language support.
- **Scalability & Real-Time Processing**: Deploying in cloud environments for high-speed prompt moderation.
- **Integration with AI Chatbots & Virtual Assistants**: Seamless adoption across AI-driven applications.
