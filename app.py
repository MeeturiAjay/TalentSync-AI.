from flask import Flask, render_template, request, redirect, url_for, flash
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import pandas as pd
from utils.jd_processing import summarize_jd, save_job_description
from utils.cv_processing import process_cv, evaluate_candidate
from utils.email_handler import send_email_result
import html

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# File paths
JD_FILE_PATH = r"C:\Users\meetu\Agentic AI - KrishNaik\AI_MULTIAGENT_JOBSCREENING_PLATFORM\uploads\job_description.csv"
CV_FOLDER = r"C:\Users\meetu\Agentic AI - KrishNaik\AI_MULTIAGENT_JOBSCREENING_PLATFORM\CVs1"
app.config['UPLOAD_FOLDER'] = CV_FOLDER

# Home Page → index.html
@app.route('/')
def index():
    return render_template('index.html')

# Upload JD and CV + Screen Candidate (single route/page)
@app.route('/screening', methods=['GET', 'POST'])
def screening():
    roles = []
    role_descriptions = {}
    cv_files = []

    # Load Job Descriptions
    if os.path.exists(JD_FILE_PATH):
        df = pd.read_csv(JD_FILE_PATH, encoding="ISO-8859-1")
        roles = df["Job Title"].tolist()
        role_descriptions = {
            str(title): html.escape(str(desc)).replace("\n", " ").replace("\r", "")
            for title, desc in zip(df["Job Title"], df["Job Description"])
        }

    # Load CVs
    if os.path.exists(CV_FOLDER):
        cv_files = [f for f in os.listdir(CV_FOLDER) if f.endswith(".pdf")]

    if request.method == 'POST':
        if 'job_title' in request.form and 'job_description' in request.form:
            job_title = request.form['job_title']
            job_description = request.form['job_description']
            uploaded_cv = request.files.get('cv_pdf')

            if job_title and job_description:
                save_job_description(job_title, job_description, JD_FILE_PATH)
                flash("✅ Job Description saved.")

            if uploaded_cv and uploaded_cv.filename != '':
                filename = secure_filename(uploaded_cv.filename)
                uploaded_cv.save(os.path.join(CV_FOLDER, filename))
                flash("✅ CV uploaded successfully.")

            return redirect(url_for('screening'))

        elif 'selected_role' in request.form and 'selected_cv' in request.form:
            selected_role = request.form['selected_role']
            selected_cv = request.form['selected_cv']

            jd_text = role_descriptions[selected_role]
            jd_summary = summarize_jd(jd_text)

            cv_path = os.path.join(CV_FOLDER, selected_cv)
            cv_chunks, full_cv_text, name, email = process_cv(cv_path)

            eligibility_result = evaluate_candidate(jd_summary, cv_chunks, name, selected_role)
            email_result = send_email_result(name, email, "Suitable" in eligibility_result)

            return render_template('result.html',
                                   name=name,
                                   role=selected_role,
                                   eligibility=eligibility_result,
                                   email_status=email_result)

    return render_template('screening.html', roles=roles, cv_files=cv_files, role_descriptions=role_descriptions)

@app.route('/cv_previews/<filename>')
def serve_cv_preview(filename):
    return send_from_directory(CV_FOLDER, filename)

if __name__ == '__main__':
    os.makedirs(CV_FOLDER, exist_ok=True)
    app.run(debug=True)