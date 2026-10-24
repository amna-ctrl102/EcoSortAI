
import os
import re
import time

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ServerError
from google.genai import types


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Gemma 4 model
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
        background: linear-gradient(
            135deg, #f0fdf4, #ffffff 55%, #ecfdf5
        );
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
        3. ♻️ Get recycling guidance.
        4. 🪴 Discover creative reuse ideas.
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
        <p>
            Identify waste, recycle responsibly,
            and turn waste into something useful.
        </p>
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
            <p>Identify visible waste materials from an image.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div style="font-size: 2rem;">🤖</div>
            <h3>AI Recycling Guide</h3>
            <p>Get material identification and disposal guidance.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div style="font-size: 2rem;">🪴</div>
            <h3>Creative Reuse Ideas</h3>
            <p>Discover useful DIY projects made from waste items.</p>
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
    "Upload an image to identify waste, get recycling guidance, "
    "and discover creative ways to reuse the materials."
)

uploaded_file = st.file_uploader(
    "Upload your waste image",
    type=["jpg", "jpeg", "png"],
    help="For best results, upload a clear image with visible items.",
)


if uploaded_file is not None:

    # Identify the selected file and clear old results if it changes
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
                "GEMINI_API_KEY was not found. "
                "Check your local .env file or Streamlit Cloud secrets."
            )

        else:
            try:
                client = genai.Client(
                    api_key=API_KEY,
                    http_options=types.HttpOptions(timeout=60_000),
                )

                image_part = types.Part.from_bytes(
                    data=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type,
                )

                # ---------- AI Prompt ----------
                prompt = """
You are EcoSort AI, an assistant that identifies visible waste,
provides responsible recycling guidance, and suggests safe creative
reuse projects.

IMAGE CLASSIFICATION:

Your response MUST begin with exactly one of these status lines:
IMAGE_STATUS: WASTE
IMAGE_STATUS: NOT_WASTE
IMAGE_STATUS: UNCLEAR

The status line must be the very first line of your response.

Follow these classification rules:

1. If the image is blurry, too dark, obstructed, or too unclear
   to assess reliably, use IMAGE_STATUS: UNCLEAR.

2. If at least one clearly identifiable discarded waste item is
   visible, use IMAGE_STATUS: WASTE.

3. If the image is clear and shows no visible waste, use
   IMAGE_STATUS: NOT_WASTE.

4. Do not assume that an object is waste just because it is old,
   damaged, or near a person. Only classify it as waste when
   the image provides reasonable visual evidence.

FOR NOT_WASTE:
Briefly explain that no visible waste was identified and ask the
user to upload an image containing waste. Do not give recycling
or DIY advice.

FOR UNCLEAR:
Explain that the image cannot be assessed reliably and ask the
user to upload a clearer image. Do not give recycling or DIY advice.

FOR WASTE:
Use simple English and Markdown headings. Discuss only items
that are clearly visible in the image.

Include these sections in this exact order:

## Identified Waste Items

For each clearly visible waste item, include:
- Name
- Material
- Usual recyclability
- One safe disposal tip

Do not invent hidden items, materials, or visual details.
Explain that local recycling rules may vary.

## Creative Reuse Ideas

This is an important feature. Suggest practical DIY projects
that give the identified waste items a useful second life.

For each suitable waste item, provide:

### Project: [Creative project name]

- **Waste Material:** The item being reused.
- **Difficulty:** Easy, Medium, or Hard.
- **Materials Needed:** List the additional materials.
- **Steps:** Give clear, numbered instructions.
- **Final Use:** Explain what the finished project is useful for.
- **Safety:** Give relevant safety precautions.

Choose ideas based on the actual visible items, not on assumed
objects. Prefer affordable, beginner-friendly projects.

Examples of suitable ideas:
- Clean plastic bottle: planter, bird-free garden water container,
  or desk organizer.
- Plastic bottle caps: mosaic decoration or craft material.
- Safe, smooth-edged aluminium can: pencil holder.
- Cardboard: desk organizer, storage box, or drawer divider.
- Clean glass jar: decorative storage container or flower vase.

These examples are suggestions, not claims that these items
are present in the image. Only recommend a project if it fits
the visible material and item.

DIY SAFETY RULES:
- Never suggest burning, melting, or heating plastic.
- Never suggest melting cans or other materials at home.
- Do not recommend handling sharp metal edges or broken glass.
- For projects involving cutting, recommend adult supervision
  and appropriate protective equipment.
- Avoid hazardous waste, batteries, chemical containers,
  and electronic components for ordinary DIY crafts.
- Do not use containers that held hazardous chemicals for crafts.
- Do not recommend food-contact uses for materials that may be
  contaminated or unsafe.
- If a project cannot be made safely, suggest recycling or
  responsible disposal instead.
- Do not claim that all materials are recyclable everywhere.

## Overall Recommendation

Give one short recommendation on how to reuse, recycle, or
responsibly dispose of the visible waste.

Keep the answer organized and useful. Do not omit the required
first-line image status. Do not provide recycling or DIY sections
for NOT_WASTE or UNCLEAR images.
"""

                with st.spinner(
                    "Gemma 4 is examining your image. "
                    "This may take up to a minute... ♻️"
                ):
                    for attempt in range(2):
                        try:
                            response = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=[image_part, prompt],
                            )
                            break
                        except ServerError:
                            if attempt == 1:
                                raise
                            time.sleep(1)

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

        # Validate the first line only
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

        # Remove the status line from the displayed response
        if status_match:
            display_text = "\n".join(lines[1:]).strip()
        else:
            display_text = result_text.strip()

        st.divider()
        st.markdown("## 🌍 Your EcoSort Results")

        # ---------- NOT WASTE ----------
        if image_status == "NOT_WASTE":

            st.info(
                "This image does not appear to contain visible waste. "
                "Please upload a waste image for recycling and reuse ideas."
            )

            if display_text:
                with st.container(border=True):
                    st.markdown(display_text)

        # ---------- UNCLEAR ----------
        elif image_status == "UNCLEAR":

            st.warning(
                "The image is unclear. Please upload a sharper image "
                "with clearly visible items."
            )

            if display_text:
                with st.container(border=True):
                    st.markdown(display_text)

        # ---------- WASTE ----------
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
                    "Reuse ideas",
                    "Included",
                )

            st.caption(
                "Categories are inferred from AI-generated guidance. "
                "Actual recycling eligibility depends on local facilities. "
                "Environmental savings are not measured."
            )

        # ---------- Invalid Status ----------
        else:
            st.warning(
                "The AI response did not begin with a recognized image "
                "status. Please analyze the image again."
            )

            with st.expander("View model response"):
                st.text(result_text)

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
        Identify. Reuse. Recycle. Build a greener future.
    </div>
    """,
    unsafe_allow_html=True,
)
