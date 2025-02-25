import requests
import json
from bs4 import BeautifulSoup

# List of URLs for each category to pre-scrape
about_urls = [
    "https://www.depts.ttu.edu/k12/about/",
    "https://www.depts.ttu.edu/k12/about/staff/",
    "https://www.depts.ttu.edu/k12/advisory-board/",
    "https://www.depts.ttu.edu/k12/faq/",
    "https://www.depts.ttu.edu/k12/contact/"
]

programs_urls = [
    "https://www.depts.ttu.edu/k12/fulltime/",
    "https://www.depts.ttu.edu/k12/freetuition/",
    "https://www.depts.ttu.edu/k12/paid-tuition/",
    "https://www.depts.ttu.edu/k12/grade-levels/",
    "https://www.depts.ttu.edu/k12/courses/",
    "https://www.depts.ttu.edu/k12/dual-credit/",
    "https://www.depts.ttu.edu/k12/cbe/",
    "https://www.depts.ttu.edu/k12/schools/",
    "https://www.depts.ttu.edu/k12/international/",
]

admissions_urls = [
    "https://www.depts.ttu.edu/k12/enroll/",
    "https://www.depts.ttu.edu/k12/about/fees/",
    "https://ttu.focusschoolsoftware.com/focus/catalog/?_gl=1*1wpzfjd*_gcl_au*Mjg0ODc0OTI4LjE3MzkzNzQyMzQ.*_ga*NjA4ODc2MTM3LjE3MzkzNzQyMzU.*_ga_TSPQSJQPQF*MTczOTM3NDIzNC4xLjEuMTczOTM3NDkzNS4wLjAuMA.."
]

student_resources_urls = [
    "https://www.depts.ttu.edu/k12/support/handbook.php",
    "https://www.depts.ttu.edu/k12/testing/",
    "https://www.depts.ttu.edu/k12/resources/proctor/",
    "https://www.depts.ttu.edu/k12/support/coursedescriptions.php",
    "https://www.depts.ttu.edu/k12/military-families/",
    "https://www.depts.ttu.edu/k12/about/disabilities/",
    "https://www.depts.ttu.edu/k12/graduation/",
    "https://www.depts.ttu.edu/k12/resources/studentOrganizations/",
    "https://www.depts.ttu.edu/online/DFW/iOS/"
]

# Function to scrape webpage content
def scrape_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return ""

# Function to scrape content from all specified URLs for each category
def scrape_category_pages(urls):
    category_content = ""
    for url in urls:
        page_text = scrape_webpage(url)
        if page_text:
            category_content += f"\n\n---Content from {url}---\n{page_text}"
    return category_content

# Scraping function that scrapes all the categories and saves the data to a file
def scrape_and_save_content():
    print("Scraping content for all categories...")

    # Scrape content for each category
    about_content = scrape_category_pages(about_urls)
    programs_content = scrape_category_pages(programs_urls)
    admissions_content = scrape_category_pages(admissions_urls)
    student_resources_content = scrape_category_pages(student_resources_urls)

    # Saving scraped content to a JSON file
    scraped_data = {
        "About": about_content,
        "Programs": programs_content,
        "Admissions": admissions_content,
        "Student Resources": student_resources_content
    }

    with open("scraped_content.json", "w") as file:
        json.dump(scraped_data, file)

    print("Content scraped and saved to 'scraped_content.json'.")

# Run this to scrape and save data
if __name__ == "__main__":
    scrape_and_save_content()

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
