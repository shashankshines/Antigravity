import smtplib
import argparse
from email.mime.text import MIMEText

def test_smtp(server, port, email, password, to_email):
    print(f"Testing SMTP connection to {server}:{port}...")
    try:
        # Try connecting
        smtp_server = smtplib.SMTP(server, port)
        smtp_server.set_debuglevel(1) # Show communication
        print("Connected. Starting TLS...")
        smtp_server.starttls()
        print("TLS started. Logging in...")
        smtp_server.login(email, password)
        print("Logged in successfully!")
        
        # Try sending
        msg = MIMEText("This is a test email from the diagnostic script.")
        msg['Subject'] = "SMTP Test"
        msg['From'] = email
        msg['To'] = to_email
        
        print("Sending test email...")
        smtp_server.sendmail(email, to_email, msg.as_string())
        smtp_server.quit()
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test SMTP Settings")
    parser.add_argument("--server", default="smtp.gmail.com", help="SMTP Server")
    parser.add_argument("--port", type=int, default=587, help="SMTP Port")
    parser.add_argument("--email", required=True, help="Your Email")
    parser.add_argument("--password", required=True, help="App Password")
    parser.add_argument("--to", required=True, help="Recipient Email")
    
    args = parser.parse_args()
    
    test_smtp(args.server, args.port, args.email, args.password, args.to)
