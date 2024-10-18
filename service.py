import logging
import imaplib
import openai
import email
from datetime import datetime
from dateutil import parser
import os
from dotenv import load_dotenv
import re
from db_schemas import EmailSentiments
from sqlalchemy.orm import Session
import re 
import html2text
from models import *
import os.path
import requests


load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class Emails:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
      
    def connect_to_gmail_imap(self,user, password):
        imap_url = 'imap.gmail.com'
        try:
           mail = imaplib.IMAP4_SSL(imap_url)
           mail.login(user, password)
           mail.select('inbox')  
           return mail
        except Exception as e:
           logging.error("Connection failed: {}".format(e))
           raise

    def get_last_10_emails(self,mail):

        result, data = mail.uid('search', None, 'UNSEEN')
        if result == 'OK':
            uids = data[0].split()
            last_10_uids = uids[-10:]

            emails = []
            for uid in last_10_uids:
                result, data = mail.uid('fetch', uid, '(RFC822)')
                if result == 'OK':
                    raw_email = data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    emails.append(email_message)
            return emails
        else:
            print('Error searching for emails.')
            return None

    def analyze_sentiment(self,emails, db, type_check):
        sentiments = []
        h = html2text.HTML2Text()
        h.ignore_links = True
        if type_check == "summary":
            prompt = f"You are a sentiment analyzer, give one word answer to the input that whether it's positive, negative, danger, warning or neutral. Be helpful. \n\n{emails}"
            response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0.7,
                    stop=["\n"]
            )
            sentiment = response.choices[0].message["content"].strip()
            self.create_email_data(db, Email(content=emails, sentiment=sentiment, created_date=datetime.now()))
        elif type_check =="email":
            for email in emails:
                email_body = ""
                if email.is_multipart():
                    for part in email.walk():
                        if part.get_content_type() == 'text/plain':
                            email_body = part.get_payload(decode=True).decode()  
                            break 
                else:
                    email_body = email.get_payload(decode=True).decode()
                    email_body = h.handle(email_body)  

                prompt = f"You are a sentiment analyzer, give one word answer to the input that whether it's positive, negative, danger, warning or neutral. Be helpful. \n\n{email_body}"
    
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=10,
                    temperature=0.7,
                    stop=["\n"]
            )
            sentiment = response.choices[0].message["content"].strip()
            self.create_email_data(db, Email(content=email_body, sentiment=sentiment, created_date=datetime.now()))
        return sentiments

    def create_email_data(self,db: Session, emailst: Email):
        db_emailst = EmailSentiments(content=emailst.content, sentiment=emailst.sentiment, created_date=emailst.created_date)
        db.add(db_emailst)
        db.commit()
        db.refresh(db_emailst)
        return db_emailst

    def get_emails_data(self,db: Session):
        return db.query(EmailSentiments).all()

    def get_emails_data_first(self,db: Session, email_id:int):
        return db.query(EmailSentiments).filter(EmailSentiments.id == email_id).first()

    def extract_time(self,text):
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s?(AM|PM|am|pm)?\b', 
            r'\b\d{1,2}\s?(AM|PM|am|pm)\b',         
        ]
        
        for pattern in time_patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def get_last_10_emails_with_keywords(self, mail, keywords, db):
        _, data = mail.search(None, 'UNSEEN')
        mail_ids = data[0].split()
        mail_ids.reverse()
        relevant_emails = []
        h = html2text.HTML2Text()
        h.ignore_links = True
        summaries = [] 
        
        for mail_id in mail_ids[:20]:
            _, data = mail.fetch(mail_id, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            subject = email_message['Subject']
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
                body = h.handle(body)
            
            if any(keyword in subject.lower() or keyword in body.lower() for keyword in keywords):
                if self.extract_time(subject) or self.extract_time(body):
                    relevant_emails.append((subject, body))
       
        for subject, body in relevant_emails: 
            prompt =  f"Summarize this appointment email: Subject: {subject}\nBody: {body}\nso that we get to only know the person name with whom we have to do meeting and where and when with start-date and end-date and with accurate timings. "

            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
                stop=["\n"]
        )
            summary = response.choices[0].message["content"].strip()
            self.analyze_sentiment(summary, db, "summary")
            summaries.append(summary)


            date = parser.parse(summary, fuzzy=True)
            print(str(date)[:10])
     
            time_pattern = r'(\d{1,2}:\d{2} (?:AM|PM|am|pm))'
            times = re.findall(time_pattern, summary)
            
            if len(times) == 2:
                start_time_str, end_time_str = times
    
            time_format = "%I:%M %p"

            start_time = datetime.strptime(start_time_str, time_format)
            end_time = datetime.strptime(end_time_str, time_format)

            meet_duration = end_time - start_time

            duration_in_minutes = meet_duration.total_seconds() / 60

            duration = int(duration_in_minutes)

            print(duration)

            parts = summary.split(". ")
            addinfo = parts[-1] if len(parts) > 1 else ""

            print(addinfo)

            url = "https://api.calendly.com/one_off_event_types"
            payload =  {
                "name": f"{subject}",
                "host": "your_user_url_obtained_from_calenldy",
                "duration": f"{duration}",
                "timezone": "Asia/Karachi",
                "date_setting": {
                    "type": "date_range",
                    "start_date": f"{date}",
                    "end_date": f"{date}",
                },
                "location": {
                    "kind": "physical",
                    "location": "Karachi",
                    "additonal_info": "string"
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer -your-calendly-access-token"
            }

            response = requests.request("POST", url, json=payload, headers=headers)

            return response.text
    
    
    def get_eventtype(self):
        url = "https://api.calendly.com/scheduled_events"

        querystring = {"user":"your_user_url_obtained_from_calenldy"}

        headers = {
            "Content-Type": "application/json",
            "Authorization":  "Bearer -your-calendly-access-token"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)

        jsonfile = response.json()

        for event in jsonfile.get('collection', []):
            keys_to_remove = ['calendar_event', 'created_at', 'event_guests', 'event_type', 
                            'invitees_counter', 'meeting_notes_html', 'meeting_notes_plain', 
                            'updated_at', 'uri']

            for key in keys_to_remove:
                event.pop(key, None)

        return jsonfile
            









    
    
