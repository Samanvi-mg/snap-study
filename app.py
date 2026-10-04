
import smtplib
import ssl
import time

from email.message import EmailMessage

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE
)

MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚",
    layout="centered"
)

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]
SMTP_SERVER = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(st.secrets.get("SMTP_PORT", 465))


@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)


def add_message(role, kind, content):
    message = {
        "role": role,
        "kind": kind,
        "content": content
    }
    st.session_state.messages.append(message)
    render_message(message)


def ask_gemini(parts):
    try:
        formatted_parts = []

        for part in parts:
            if isinstance(part, str):
                formatted_parts.append(
                    types.Part.from_text(text=part)
                )
            else:
                formatted_parts.append(part)

        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=formatted_parts,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        return response.text or "No response received."

    except Exception as error:
        st.error(f"Full Gemini error: {repr(error)}")
        return "Gemini request failed. See the error above."


# Collect actual study content from the displayed chat
def get_study_transcript():
    transcript = []

    for msg in st.session_state.messages:
        role = msg.get("role")
        kind = msg.get("kind")
        content = msg.get("content", "")

        if role == "user":
            if kind == "text" and content.strip():
                transcript.append(
                    f"Student's question:\n{content.strip()}"
                )
            elif kind == "image":
                transcript.append(
                    "[Student uploaded a study image]"
                )

        elif role == "assistant" and kind == "text":
            content = content.strip()

            # Skip the welcome message and failed responses
            if (
                not content
                or content.startswith("👋 **Hey")
                or content.startswith("Gemini request failed")
                or content.startswith("Sorry, something went wrong")
            ):
                continue

            transcript.append(
                f"Snap & Study explanation:\n{content}"
            )

    return "\n\n".join(transcript)


def clean_email_text(text):
    if not text:
        return "No study explanation is available."
    return text.strip()


def send_email(to_email, user_name, summary):
    try:
        message = EmailMessage()
        message["Subject"] = "Your Snap & Study Explanation"
        message["From"] = SMTP_EMAIL
        message["To"] = to_email

        message.set_content(
            f"""Hello {user_name},

Here is your saved study explanation from Snap & Study.

{clean_email_text(summary)}

Keep learning!

Snap & Study AI
"""
        )

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT,
            context=context,
            timeout=30
        ) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(message)

        return True, "Email sent successfully"

    except Exception as error:
        return False, str(error)


# Step 1: Onboarding
if "onboarded" not in st.session_state:
    st.title("📚 Snap & Study")
    st.caption("Snap it. Understand it. Learn it.")

    st.markdown(
        "👋 Welcome! Upload a photo of a question, "
        "diagram, textbook page, or notes. "
        "I'll explain it in simple steps."
    )

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email = st.text_input(
            "Your email address",
            placeholder="you@example.com",
            help="Your study explanations can be sent to this address."
        )

        submitted = st.form_submit_button(
            "Let's get started 🚀",
            use_container_width=True
        )

    if submitted:
        if not name.strip() or not email.strip():
            st.warning("Please enter both your name and email.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.warning("Please enter a valid email address.")
        else:
            st.session_state.name = name.strip()
            st.session_state.email = email.strip()

            st.session_state.api_history = []
            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()

    st.stop()


# Step 2: Chat interface
header_col, button_col = st.columns(
    [5, 2], vertical_alignment="center"
)

with header_col:
    st.title("📚 Snap & Study")

with button_col:
    study_transcript = get_study_transcript()

    send_disabled = not study_transcript.strip()

    if st.button(
        "📧 Send to Email",
        disabled=send_disabled,
        use_container_width=True
    ):
        with st.spinner("Preparing your study notes..."):
            summary = ask_gemini([
                SUMMARY_REQUEST_PROMPT,
                "Summarize the following actual conversation. "
                "Use only the study content provided below:\n\n"
                + study_transcript
            ])

        if (
            summary
            and not summary.startswith("Gemini request failed")
            and not summary.startswith("Sorry,")
        ):
            success, info = send_email(
                st.session_state.email,
                st.session_state.name,
                summary
            )

            if success:
                st.success("Sent! Check your email 📧")
            else:
                st.error(f"Couldn't send the email: {info}")
        else:
            st.error(
                "Couldn't prepare the study summary. "
                "Please try again later."
            )


st.caption(
    f"Student: {st.session_state.name} | "
    f"Email: {st.session_state.email}"
)


# Display welcome message or chat history
if not st.session_state.messages:
    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )
else:
    for message in st.session_state.messages:
        render_message(message)


# Step 3: Image and text input
user_input = st.chat_input(
    "Ask a question or upload a study image...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"]
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text.strip() if user_input.text else ""
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()

        add_message("user", "image", photo_bytes)

        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append(
            "Analyze this image and explain the academic "
            "content in simple, step-by-step language."
        )

    if parts:
        with st.spinner("Understanding your image... 🧠"):
            answer = ask_gemini(parts)

        add_message("assistant", "text", answer)
        st.rerun()