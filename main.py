from flask import Flask, render_template, request
import PyPDF2
from google import genai

app = Flask(__name__)

# Initialize Gemini client
client = genai.Client(api_key="your api key")


def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get inputs
        resume_file = request.files.get("resume")
        job_description = request.form.get("job_description")

        if not resume_file or not job_description:
            return "Error: Resume or Job Description missing", 400

        # Extract resume text
        resume_text = extract_text_from_pdf(resume_file)

        # Gemini Prompt (ATS-focused)
        prompt = f"""
You are an ATS (Applicant Tracking System) expert.

Resume:
{resume_text}

Job Description:
{job_description}

Tasks:
1. give Match percentage (out of 100)
2. Matching skills
3. Missing skills
4. Strengths
5. Improvement suggestions
Respond in clean readable text.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # IMPORTANT: Return plain text (your JS expects text)
        return response.text

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
