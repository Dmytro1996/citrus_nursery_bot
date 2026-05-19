# -*- coding: utf-8 -*-
"""
Created on Wed May 13 17:24:30 2026

@author: Dmytro
"""
import smtplib
from email.message import EmailMessage
from langchain_core.tools import Tool
import os

def send_email(receiver: str, subject: str, content: str):
    message = EmailMessage()
    message['To'] = receiver
    message['Subject'] = subject
    message.set_content(content)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.environ['SMTP_EMAIL_ADDRESS'], 
                   os.environ['SMTP_EMAIL_PASS'])
        smtp.send_message(message)
        
email_tool = Tool(name = 'email_sender', func = send_email, 
                  description = 'Sends an email.')