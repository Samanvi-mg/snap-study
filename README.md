
# 📚 Snap & Study

Snap & Study is an AI-based study assistant that helps students understand difficult study material easily.

Users can upload a photo of a question, diagram, textbook page, or handwritten notes. The app uses Gemini AI to understand the uploaded content and explain it in simple and easy-to-follow language.

The app also allows students to save the explanation by sending it to their email.

## Features

- Upload a study image such as a question, diagram, or notes
- Ask questions about the uploaded content
- Get simple explanations using Gemini AI
- Ask follow-up study questions
- Send the study explanation to email
- Simple and student-friendly interface

## Technologies Used

- Python
- Streamlit
- Google Gemini API
- Gmail SMTP
- HTML/Markdown through Streamlit

## How to Run Locally

### 1. Clone the repository

```bash
git clone <your-github-repository-link>
cd Snap-and-Study
````

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install the required packages

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Create a folder named `.streamlit` in the project folder.

Inside it, create a file named:

```text
secrets.toml
```

Add:

```toml
GEMINI_API_KEY = "your-gemini-api-key"

SMTP_EMAIL = "your-email@gmail.com"
SMTP_PASSWORD = "your-gmail-app-password"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
```

Do not upload `secrets.toml` to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## Note

A Gemini API key and Gmail App Password are required for the AI explanation and email features.

````

### One small thing before you put it on GitHub

In the README, change:

```text
<your-github-repository-link>
````

to your actual GitHub repository link.

Also make sure your `.gitignore` contains:

```text
.streamlit/secrets.toml
venv/
__pycache__/
```

That way,your Gemini API key and email password won't accidentally be uploaded to GitHub.
