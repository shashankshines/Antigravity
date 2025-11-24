import os
import argparse
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class EmailAgent:
    def __init__(self, api_key=None, mock_mode=True):
        self.mock_mode = mock_mode
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Email generation will fail unless provided.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    def validate_email(self, body):
        """Checks the email body for missing information placeholders."""
        import re
        # Look for patterns like [Date], [Name], [Insert ...], etc.
        # This regex looks for square brackets containing text
        placeholders = re.findall(r'\[(.*?)\]', body)
        
        # Filter out common non-error placeholders if any (e.g., if we used [Signature] internally, but we don't)
        # We want to catch things like [Date], [Time], [Your Name], [Client Name]
        
        missing_info = []
        for p in placeholders:
            # Simple heuristic: if it looks like a placeholder instruction
            if any(keyword in p.lower() for keyword in ['date', 'time', 'name', 'insert', 'attach', 'agenda', 'link', 'here']):
                missing_info.append(f"[{p}]")
        
        return missing_info

    def generate_email(self, subject, attachment_names=None):
        """Generates an email body based on the subject using Gemini."""
        if not self.api_key:
            return "Error: API Key missing. Cannot generate email."
        
        # Construct context about attachments
        attachment_context = ""
        if attachment_names:
            file_list = ", ".join(attachment_names)
            attachment_context = f"The following files are attached to this email: {file_list}. Please explicitly mention them in the email body (e.g., 'Please find attached...')."

        # Updated prompt for clarity, grammar, and official formatting
        prompt = f"""
        Analyze the subject '{subject}' to determine the appropriate tone (Professional vs Personal).
        
        - If the subject suggests a business, work, or formal context (e.g., "Invoice", "Application", "Meeting", "Resignation"), use a **Professional** tone (Formal, polite, concise).
        - If the subject suggests a friends, family, or casual context (e.g., "Party", "Catch up", "Hello", "Trip"), use a **Personal** tone (Friendly, warm, casual).
        
        Write the email body accordingly.
        
        Context:
        {attachment_context}
        
        Guidelines:
        - Structure: Start directly with a salutation. Use single spacing between paragraphs. Do NOT use excessive newlines.
        - Exclusions: Do NOT include the subject line, closing (Sincerely), signature placeholders (like [Your Name]), or the detected tone label (e.g., "Tone: Professional").
        - Missing Info: If details (dates, names, attachments) are needed, use clear placeholders like [Date], [Name], [Insert Attachment].
        
        Return ONLY the email body text. Do not include any introductory or concluding remarks about the generation.
        """
        try:
            response = self.model.generate_content(prompt)
            email_text = response.text
            # Post-processing
            if email_text.lower().startswith("subject:"):
                email_text = email_text.split("\n", 1)[1].strip()
            return email_text
        except Exception as e:
            return f"Error generating email: {e}"

    def optimize_subject(self, content):
        """Generates a concise, professional subject line based on content/purpose."""
        if not self.api_key:
            return "Error: API Key missing."
        
        prompt = f"Generate a concise, professional, and attention-grabbing email subject line for the following email content/purpose:\n\n'{content}'\n\nReturn ONLY the subject line, nothing else."
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace("Subject:", "").strip()
        except Exception as e:
            return f"Error: {e}"

    def send_email(self, to_email, subject, body, smtp_settings=None, attachments=None):
        """Sends the email with optional attachments."""
        if self.mock_mode:
            print("\n" + "="*30)
            print(f" [MOCK SEND] Sending Email...")
            print(f" To: {to_email}")
            print(f" Subject: {subject}")
            print(f" Attachments: {len(attachments) if attachments else 0} files")
            print(f" Body:\n{body}")
            print("="*30 + "\n")
            return True
        else:
            if not smtp_settings:
                print("Error: SMTP settings required for real sending.")
                return False
            
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.base import MIMEBase
            from email import encoders

            try:
                msg = MIMEMultipart()
                msg['From'] = smtp_settings['email']
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))

                # Process Attachments
                if attachments:
                    for file in attachments:
                        try:
                            part = MIMEBase('application', "octet-stream")
                            part.set_payload(file.getvalue())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', f'attachment; filename="{file.name}"')
                            msg.attach(part)
                        except Exception as e:
                            print(f"Error attaching file {file.name}: {e}")

                server = smtplib.SMTP(smtp_settings['server'], smtp_settings['port'])
                server.starttls()
                server.login(smtp_settings['email'], smtp_settings['password'])
                text = msg.as_string()
                server.sendmail(smtp_settings['email'], to_email, text)
                server.quit()
                print(f"Email sent successfully to {to_email}")
                return True
            except Exception as e:
                print(f"Error sending email: {e}")
                return False

def main():
    parser = argparse.ArgumentParser(description="AI Email Agent")
    parser.add_argument("--subject", required=True, help="Subject of the email")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--mock", action="store_true", default=True, help="Force mock mode (default)")
    parser.add_argument("--real", action="store_false", dest="mock", help="Enable real email sending")
    
    args = parser.parse_args()

    agent = EmailAgent(mock_mode=args.mock)
    
    print(f"Generating email for subject: '{args.subject}'...")
    body = agent.generate_email(args.subject)
    
    if "Error" in body:
        print(body)
    else:
        agent.send_email(args.to, args.subject, body)

if __name__ == "__main__":
    main()
