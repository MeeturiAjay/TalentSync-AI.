import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import random
from datetime import datetime

load_dotenv()
sender_email = os.getenv("USERNAME")
sender_password = os.getenv("GOOGLE_APP_PASSWORD")
try:
    df = pd.read_csv('uploads/job_description.csv', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('uploads/job_description.csv', encoding='ISO-8859-1')
job_title = df['Job Title'][0]

def send_email_result(candidate_name, candidate_email, is_selected):
    if is_selected:
        interview_date = datetime.today().strftime('%Y-%m-%d')
        hour = random.randint(9, 16)
        minute = random.choice([0, 15, 30, 45])
        interview_time = f"{hour:02d}:{minute:02d}"
        subject = f"Interview Invitation - {interview_date}"
        body = f"""
Dear {candidate_name},

We are pleased to inform you that you have been shortlisted for the next phase of our recruitment process for the **{job_title}** position.

Your in-person interview has been scheduled on {interview_date} at {interview_time} IST (24hrs) at our office. Please review the appointment details and confirm your availability at your earliest convenience. Should you have any questions or require further clarification, feel free to reach out.

We appreciate your interest in our organization and look forward to meeting you.

Best Regards,
TalenSyncAI Team
"""
    else:
        subject = "Update on Your Job Application"
        body = f"""
Hi {candidate_name},

Thank you for taking the time to apply and participate in our screening process.

After careful consideration, we regret to inform you that we won't be moving forward with your application at this time.

We appreciate your interest and encourage you to apply for future opportunities with us.

Best Wishes,\nTalenSyncAI Team
        """

    try:
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = candidate_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, candidate_email, message.as_string())
        server.quit()

        return f"✅ Email sent to {candidate_email}."
    except Exception as e:
        return f"❌ Failed to send email: {e}"
