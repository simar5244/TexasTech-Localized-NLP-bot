

import ipywidgets as widgets
from IPython.display import display
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from IPython.display import FileLink

# Global conversation history
conversation_history = []

# Function to send an email
def send_email(conversation_log):
    sender_email = "your_email@gmail.com"  # Replace with your email
    receiver_email = "simar5244@gmail.com"
    password = "your_email_password"  # Use app passwords for security
    
    subject = "TTU K-12 Chatbot Conversation Log"
    body = "\n".join(conversation_log)
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Conversation log sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to download conversation log
def download_log():
    filename = "conversation_log.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        for entry in conversation_history:
            q, a = entry.split("\nA: ")
            q = q.replace("Q: ", "")
            writer.writerow([q, a])
    display(FileLink(filename))

# Function to ask Gemini API
def ask_question(api_key, webpage_content, exception_content, question):
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    combined_content = f"{exception_content}\n\n{webpage_content}"
    
    data = {
        "contents": [{"parts": [{"text": f"Previous conversation:\n{' '.join(conversation_history)}\n\nContext:\n{combined_content}\n\nQuestion: {question}"}]}],
    }
        
    
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        try:
            return response.json()["candidates"][0]["content"]
        except (KeyError, IndexError):
            print("Unexpected response format from Gemini API.")
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

# Load content files
with open("scraped_content.json", "r") as file:
    scraped_data = json.load(file)

with open("scraped_content.json", "r") as file:
    exception_data = json.load(file)

api_key = "AIzaSyCHcavN8CMNDIy_DNWbtZ69_XmIN37BMgI"

greeting = widgets.HTML(value="<h2>Welcome to the TTU K-12 Chatbot!</h2>")
display(greeting)

category_dropdown = widgets.Dropdown(
    options=['About', 'Programs', 'Admissions', 'Student Resources'],
    description='Category:',
    disabled=False
)
question_input = widgets.Text(description="Question:", disabled=False)
submit_button = widgets.Button(description="Submit Question")
email_button = widgets.Button(description="Email Log")
download_button = widgets.Button(description="Download Log")
output = widgets.Output()

display(category_dropdown, question_input, submit_button, email_button, download_button, output)

# Handle question submission
def on_submit_button_clicked(b):
    question = question_input.value
    category = category_dropdown.value
    
    if not question:
        with output:
            print("Please enter a question.")
        return
    
    content = scraped_data.get(category, "")
    exception_content = exception_data.get(category, "")
    answer = ask_question(api_key, content, exception_content, question)
    
    if answer:
        conversation_history.append(f"Q: {question}\nA: {answer}")
        with output:
            print(f"Answer: {answer}")
    else:
        with output:
            print("I couldn't find the information. Try another question or contact support.")

# Handle email log submission
def on_email_button_clicked(b):
    send_email(conversation_history)

# Handle log download
def on_download_button_clicked(b):
    download_log()

submit_button.on_click(on_submit_button_clicked)
email_button.on_click(on_email_button_clicked)
download_button.on_click(on_download_button_clicked)
