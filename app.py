
import os
import re

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemma-4-26b-a4b-it"


# ---------- Page Configuration ----------
st.set_page_config(
    page_title="EcoSort AI | Smart Recycling",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Custom Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0fdf4, #ffffff 55%, #ecfdf5);
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem 1rem;
        text-align: center;
        background: linear-gradient(135deg, #14532d, #15803d);
        border-radius: 24px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        color: white;
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .hero p {
        color: #dcfce7;
        font-size: 1.1rem;
    }

    .feature-card {
        background: rgba(255,255,255,0.9);
        border: 1px solid #d1fae5;
        border-radius: 16px;
        padding: 1.2rem;
        min-height: 145px;
        margin-bottom: 1rem;
    }

    .feature-card h3 {
        color: #166534;
        margin-top: 0.4rem;
        font-size: 1.1rem;
    }

    .feature-card p {
        color: #475569;
        font-size: 0.92rem;
    }

    .section-heading {
        color: #166534;
        font-weight: 750;
    }

    .stButton > button[kind="primary"] {
        background: #15803d;
        border: none;
        border-radius: 12px;
        min-height: 3rem;
        font-weight: 700;
    }

    .stButton > button[kind="primary"]:hover {
        background: #166534;
        border: none;
    }

    [data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #86efac;
        border-radius: 14px;
        padding: 0.5rem;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ♻️ EcoSort AI")
    st.caption("Smart waste. Smarter planet.")

    st.divider()

    st.markdown("### How it works")
    st.markdown(
        """
        1. 📸 Upload a waste image.
        2. 🤖 Let Gemma 4 analyze it.
        3. 🌱 Read your recycling guide.
        """
    )

    st.divider()

    st.markdown("### Supported images")
    st.write("JPG, JPEG and PNG")

    st.info(
        "Recycling rules differ by location. "
        "Always follow your local waste collection guidelines."
    )


# ---------- Hero Section ----------
st.markdown(
    """
    <div class="hero">
        <h1>♻️ EcoSort AI</h1>
        <p>Your smart companion for waste identification
        and responsible recycling.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Feature Cards ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div style="font-size: 2rem;">📷</div>
            <h3>Image Recognition</h3>
            <p>Upload a photo to identify visible waste materials.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div style="font-size: 2rem;">🤖</div>
            <h3>AI-Powered Guide</h3>
            <p>Get recycling suggestions powered by Gemma 4.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div style="font-size: 2rem;">🌍</div>
            <h3>Greener Choices</h3>
            <p>Learn practical ways to dispose of waste responsibly.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()


# ---------- Image Upload ----------
st.markdown(
    '<h2 class="section-heading">🔍 Analyze Your Waste</h2>',
    unsafe_allow_html=True,
)

st.write(
    "Choose an image containing waste items and get a personalized "
    "recycling guide."
)

uploaded_file = st.file_uploader(
    "Upload your waste image",
    type=["jpg", "jpeg", "png"],
    help="For best results, use a clear image with visible waste items.",
)


if uploaded_file is not None:

    # Clear old results when a different file is selected
    current_file_key = (
        uploaded_file.name,
        uploaded_file.size,
        uploaded_file.getvalue(),
    )

    # Use filename and size to identify the selected file
    current_file_key = (
        uploaded_file.name,
        uploaded_file.size,
    )

    if st.session_state.get("file_key") != current_file_key:
        st.session_state["file_key"] = current_file_key
        st.session_state.pop("analysis_result", None)
        st.session_state.pop("analysis_error", None)

    preview_col, info_col = st.columns([1.1, 1])

    with preview_col:
        st.image(
            uploaded_file,
            caption="Image selected for analysis",
            use_container_width=True,
        )

    with info_col:
        st.markdown("### 📋 Image Details")
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        st.success("Your image is ready for analysis.")

    # ---------- Analyze Button ----------
    if st.button(
        "🌱 Analyze Waste",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.pop("analysis_result", None)
        st.session_state.pop("analysis_error", None)

        if not API_KEY:
            st.session_state["analysis_error"] = (
                "GEMINI_API_KEY nahi mili. Apni .env file check karein."
            )

        else:
            try:
                client = genai.Client(api_key=API_KEY)

                image_part = types.Part.from_bytes(
                    data=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type,
                )

                # ---------- AI Prompt ----------
                prompt = (
                    "You are EcoSort AI, an assistant that identifies visible waste "
                    "and provides safe recycling guidance. "

                    "FIRST, assess the image quality and whether its contents "
                    "can be identified confidently. "

                    "Start your response with exactly one status line: "
                    "IMAGE_STATUS: WASTE, "
                    "IMAGE_STATUS: NOT_WASTE, or "
                    "IMAGE_STATUS: UNCLEAR. "

                    "CLASSIFICATION RULES — follow these in order: "

                    "1. If the image is too blurry, out of focus, too dark, "
                    "obstructed, or too low-quality to determine confidently "
                    "whether waste is present, use IMAGE_STATUS: UNCLEAR. "
                    "Do not classify an unclear image as NOT_WASTE merely "
                    "because you cannot identify any waste. "

                    "2. If at least one clearly identifiable discarded or waste "
                    "item is visible, use IMAGE_STATUS: WASTE, even if people, "
                    "flowers, animals, or useful objects are also present. "

                    "3. If the image is sufficiently clear and shows people, "
                    "flowers, plants, animals, landscapes, or other non-waste "
                    "subjects with no visible waste, use IMAGE_STATUS: NOT_WASTE. "

                    "For NOT_WASTE, briefly explain that no visible waste was "
                    "identified and ask the user to upload a waste image. "

                    "For UNCLEAR, explain that the image is too unclear to assess "
                    "reliably and ask the user to upload a sharper, clearer image. "
                    "Do not provide recycling advice for NOT_WASTE or UNCLEAR. "

                    "For WASTE, use simple English and Markdown headings. "
                    "Discuss only waste items clearly visible in the image. "

                    "For each clearly visible waste item, include its name, "
                    "material, usual recyclability, and one safe disposal tip. "

                    "Do not list possible, hidden, or assumed items. "
                    "Do not treat an object as waste simply because it is old, "
                    "damaged, or visible near a person. It must be identifiable "
                    "as discarded waste. "

                    "Describe only what can actually be seen. Do not invent "
                    "details or claim certainty when an item is unclear. "
                    "Local recycling rules may vary. Add a short overall "
                    "recommendation for WASTE images."
                )

                with st.spinner(
                    "Gemma 4 is examining your image... ♻️"
                ):
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[image_part, prompt],
                    )

                # ---------- Save AI Response ----------
                response_text = response.text

                if response_text and response_text.strip():
                    st.session_state["analysis_result"] = (
                        response_text.strip()
                    )
                else:
                    st.session_state["analysis_error"] = (
                        "The model returned an empty response. "
                        "Please try again."
                    )

            except Exception as error:
                st.session_state["analysis_error"] = (
                    f"{type(error).__name__}: {error}"
                )

    # ---------- Display Results ----------
    if st.session_state.get("analysis_result"):

        result_text = st.session_state["analysis_result"]

        # Validate the status on the first line only
        lines = result_text.splitlines()
        first_line = lines[0].strip() if lines else ""

        status_match = re.fullmatch(
            r"IMAGE_STATUS:\s*(WASTE|NOT_WASTE|UNCLEAR)",
            first_line,
            flags=re.IGNORECASE,
        )

        if status_match:
            image_status = status_match.group(1).upper()
        else:
            image_status = "UNKNOWN"

        # Remove the first line only when it contains a valid status
        if status_match:
            display_text = "\n".join(lines[1:]).strip()
        else:
            display_text = result_text.strip()

        st.divider()
        st.markdown("## 🌍 Your Recycling Guide")

        # ---------- Status-Specific UI ----------
        if image_status == "NOT_WASTE":

            st.info(
                "This image does not appear to contain waste. "
                "Upload a waste image to get recycling guidance."
            )

            if display_text:
                with st.container(border=True):
                    st.markdown(display_text)

        elif image_status == "UNCLEAR":

            st.warning(
                "The image is unclear. Please upload a clearer image "
                "with visible waste items."
            )

            if display_text:
                with st.container(border=True):
                    st.markdown(display_text)

        elif image_status == "WASTE":

            with st.container(border=True):
                st.markdown(display_text)

            st.success("Waste analysis complete!")

            # ---------- Category Badges ----------
            text_to_check = display_text.lower()

            st.markdown("### 🏷️ Waste Categories")

            categories = {
                "🥤 Plastic": [
                    "plastic",
                    "bottle",
                    "container",
                ],
                "📦 Paper & Cardboard": [
                    "paper",
                    "cardboard",
                    "carton",
                ],
                "🥫 Metal": [
                    "metal",
                    "aluminum",
                    "aluminium",
                    "can",
                ],
                "🍃 Organic": [
                    "organic",
                    "food waste",
                    "compost",
                ],
                "🍾 Glass": [
                    "glass",
                    "jar",
                ],
                "🔋 E-waste": [
                    "electronic",
                    "battery",
                    "e-waste",
                ],
            }

            found_categories = [
                category
                for category, keywords in categories.items()
                if any(
                    re.search(
                        rf"\b{re.escape(keyword)}\b",
                        text_to_check,
                    )
                    for keyword in keywords
                )
            ]

            if found_categories:
                badge_cols = st.columns(
                    min(len(found_categories), 3)
                )

                for index, category in enumerate(found_categories):
                    with badge_cols[index % len(badge_cols)]:
                        st.markdown(
                            f"""
                            <div style="
                                background:#dcfce7;
                                border:1px solid #86efac;
                                border-radius:12px;
                                padding:12px 8px;
                                text-align:center;
                                color:#166534;
                                font-weight:600;
                                margin-bottom:10px;
                            ">
                                {category}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.info(
                    "No specific waste category could be identified."
                )

            # ---------- Recycling Impact ----------
            st.markdown("### 🌱 Recycling Impact")

            impact_cols = st.columns(3)

            with impact_cols[0]:
                st.metric(
                    "Categories detected",
                    len(found_categories),
                )

            with impact_cols[1]:
                st.metric(
                    "Recycling guidance",
                    "Available",
                )

            with impact_cols[2]:
                st.metric(
                    "Next step",
                    "Sort & check",
                )

            st.caption(
                "Categories are identified from AI-generated guidance. "
                "Individual objects and environmental savings are not measured."
            )

        else:
            st.warning(
                "The AI response did not begin with a recognized image status. "
                "Please analyze the image again."
            )

    # ---------- Error Display ----------
    if st.session_state.get("analysis_error"):

        st.error(
            "Analysis could not be completed. Please try again."
        )

        with st.expander("View technical details"):
            st.code(st.session_state["analysis_error"])


# ---------- Footer ----------
st.divider()

st.markdown(
    """
    <div style="text-align:center; padding:1rem; color:#64748b;">
        <strong style="color:#166534;">EcoSort AI ♻️</strong>
        <br>
        Built for a cleaner, more sustainable future.
    </div>
    """,
    unsafe_allow_html=True,
)
