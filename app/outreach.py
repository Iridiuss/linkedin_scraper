import os, json
import openai
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
load_dotenv(".env")

openai.api_key = os.getenv("OPENAI_API_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")

PORTFOLIO_SNIPPETS = (
    "We've shipped 200+ projects across fintech, health, and gov with React, Node, and XR tech.",
    "Battle-tested dev-ops on AWS/GCP – 99.99% uptime.",
)

MODEL = os.getenv("MODEL", "gpt-4o")


def craigslists_email_prompt(lead):
    body = f"\n\n".join(PORTFOLIO_SNIPPETS)
    prompt = (
        f"You are a business development assistant at Sumeru Digital. Craft an email replying to the following Craigslist post.\n"
        f"\nPOST TITLE: {lead['title']}\nPOST BODY: {lead['body'][:1500]}\n\n"
        f"The email should be concise, reference their need, and propose a short call. Sign off as 'Team Sumeru'."
    )
    return prompt


def salesnav_inmail_prompt(persona):
    prompt = (
        f"Write a 600-character LinkedIn InMail to {persona['name']} (headline: {persona['headline']}) at {persona['company']}.\n"
        f"Hook onto this post excerpt: '{persona['recent_post']}'.\n"
        f"Offer a 15-min call to discuss accelerating {persona['role']} goals with Sumeru's dev team."
    )
    return prompt


def generate_text(prompt: str):
    resp = openai.ChatCompletion.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content.strip(), MODEL


def send_gmail(to_addr: str, subject: str, content: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_addr
    msg.set_content(content)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg) 