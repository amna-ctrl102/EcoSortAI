
# ♻️ EcoSort AI — Smart Recycling Assistant

EcoSort AI is an AI-powered recycling assistant that analyzes uploaded images and helps users understand how to sort and dispose of clearly visible waste items.

The application uses Google Gemma 4 through the Google Gen AI SDK to generate image-based recycling guidance.

## ✨ Features

- Upload waste images in JPG, JPEG, or PNG format.
- Analyze images using a multimodal AI model.
- Classify images as `WASTE`, `NOT_WASTE`, or `UNCLEAR`.
- Identify clearly visible waste items.
- Provide material information, usual recyclability, and safe disposal tips.
- Ask users to upload a clearer image when the contents cannot be assessed confidently.
- Display recycling categories and useful next steps.
- Handle missing API keys and model errors.

## 🤖 AI Model

- **Model family:** Google Gemma 4
- **Model ID:** `gemma-4-26b-a4b-it`
- **Model type:** Open-weight multimodal model
- **Access method:** Google Gen AI SDK
- **Task:** Image analysis and recycling guidance

## 🧰 Technology Stack

- Python
- Streamlit
- Google Gemma 4
- Google Gen AI SDK
- python-dotenv
- Custom CSS

## 🔄 Model Harness / Orchestrator

The Streamlit application coordinates the AI analysis workflow:

1. Accept an image uploaded by the user.
2. Prepare the image and classification prompt.
3. Send the image and prompt to Gemma 4.
4. Receive the model response.
5. Read and validate the response's status line.
6. Display the appropriate recycling guide or request a clearer image.
7. Display an error message if the request fails.

## 🚀 Getting Started

### Prerequisites

- Python installed on your system.
- A Google Gen AI API key with access to the selected model.

### Installation

1. Clone or download this repository.
2. Open the project directory in your terminal.
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

   Replace the placeholder with your own API key. Never publish your actual key.

5. Start the application:

   ```bash
   python -m streamlit run app.py
   ```

6. Open the local URL shown in the terminal.

## 🧪 How to Use

1. Open EcoSort AI in your browser.
2. Upload a clear image.
3. Click **Analyze Waste**.
4. Review the generated classification and disposal guidance.
5. Follow local recycling rules for the final disposal decision.

## 🔐 Security

- Store API credentials in `.env`.
- Never commit `.env` to version control.
- Add `.env` to `.gitignore`.

## ⚠️ Limitations

AI-generated results may be inaccurate. The application does not guarantee material identification or local recyclability. Recycling rules vary by location; follow local waste collection guidelines and appropriate safety precautions.

## 🌱 Project Goal

EcoSort AI aims to make waste identification and responsible recycling easier through accessible multimodal AI.
