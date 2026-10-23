
# EcoSort AI — Skills

## Project Overview
EcoSort AI is an AI-powered recycling assistant that analyzes uploaded images and provides disposal guidance for clearly visible waste items.

## AI Model
- **Model:** Google Gemma 4
- **Model ID:** `gemma-4-26b-a4b-it`
- **Model Type:** Open-weight multimodal AI model
- **Integration:** Google Gen AI SDK
- **Purpose:** Identify visible waste and generate recycling guidance.

## Skills Used

### 1. Python Development
- Python programming
- Exception handling
- Environment variable management

### 2. AI and Prompt Engineering
- Multimodal image analysis
- Google Gemma 4 API integration
- Structured prompt design
- AI response interpretation

### 3. Frontend Development
- Streamlit application development
- Image upload and preview
- Interactive buttons and status messages
- Custom CSS styling and responsive layouts

### 4. Model Harness / Orchestration
The application coordinates these steps:

1. Receive an image from the user.
2. Prepare the image and prompt.
3. Send the request to the Gemma 4 model.
4. Receive the model's response.
5. Interpret the image status: `WASTE`, `NOT_WASTE`, or `UNCLEAR`.
6. Display the appropriate result or request a clearer image.
7. Display an error message if analysis fails.

### 5. Image Classification Rules
- **WASTE:** Clearly identifiable waste is visible.
- **NOT_WASTE:** The image is clear and no waste is identified.
- **UNCLEAR:** The image cannot be assessed confidently.

The application should not invent objects or provide recycling guidance for unclear or non-waste images.

### 6. API and Security
- Google Gen AI SDK
- API key configuration through `.env`
- Keeping API credentials out of source control
- API error handling

## Technology Stack
- Python
- Streamlit
- Google Gemma 4
- Google Gen AI SDK
- python-dotenv

## Run Locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Limitations
AI predictions may be inaccurate. Recycling recommendations can vary by location, so users should follow local waste collection guidelines.
