import praw
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import psycopg2
import os

# Reddit API credentials
CLIENT_ID = "4ytnaDhpvELitgpwmGJfOA"
CLIENT_SECRET = "LfIE11OtSdMy7Zg0gSmexv9VXzqs3g"
USER_AGENT = "Data Extractor"

# Email credentials and settings
EMAIL_ADDRESS = "ardagumus03@gmail.com"  # Replace with your email address
EMAIL_PASSWORD = "twslsqacdxyxgefm"  # Replace with your email password
RECIPIENT_EMAILS = ["l2022705036@isparta.edu.tr"]  # Replace with recipient emails

# Keywords to search for
KEYWORDS = ["Defensx", "Secure Browser", "DNS"]

# Subreddit to monitor
SUBREDDIT_NAME = "MSP"

# PostgreSQL database URL from Heroku environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Setup Reddit API client
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

# Initialize PostgreSQL database
def initialize_db():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS processed_urls (
            url TEXT PRIMARY KEY
        );
    """)
    conn.commit()
    conn.close()

# Check if a URL is processed
def is_url_processed(url):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute("SELECT 1 FROM processed_urls WHERE url = %s", (url,))
    result = c.fetchone()
    conn.close()
    return result is not None

# Mark a URL as processed
def mark_url_processed(url):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    c = conn.cursor()
    c.execute("INSERT INTO processed_urls (url) VALUES (%s) ON CONFLICT DO NOTHING", (url,))
    conn.commit()
    conn.close()

# Initialize the database
initialize_db()

def send_email(subject, body):
    """Send an email with the given subject and body."""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ", ".join(RECIPIENT_EMAILS)  # Join all recipient emails with a comma
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to: {', '.join(RECIPIENT_EMAILS)}")
    except Exception as email_err:
        print(f"Failed to send email: {email_err}")

def monitor_subreddit():
    """Monitor the subreddit for the keywords and send a summary email."""
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    print(f"Monitoring subreddit: {SUBREDDIT_NAME} for keywords: {', '.join(KEYWORDS)}")

    while True:
        try:
            matches = {keyword: [] for keyword in KEYWORDS}  # Store URLs by keyword

            for submission in subreddit.new(limit=100):
                for keyword in KEYWORDS:
                    url = f"https://www.reddit.com{submission.permalink}"
                    if not is_url_processed(url) and (keyword.lower() in submission.title.lower() or keyword.lower() in submission.selftext.lower()):
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc))
                        if len(matches[keyword]) < 15:  # Limit to the first 15 URLs per keyword
                            matches[keyword].append((timestamp, url))
                            mark_url_processed(url)

                submission.comments.replace_more(limit=None)  # Ensure all comments are expanded
                for comment in submission.comments.list():
                    if hasattr(comment, 'body'):
                        url = f"https://www.reddit.com{comment.permalink}"
                        if not is_url_processed(url) and any(keyword.lower() in comment.body.lower() for keyword in KEYWORDS):
                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(comment.created_utc))
                            keyword = next(k for k in KEYWORDS if k.lower() in comment.body.lower())
                            if len(matches[keyword]) < 15:
                                matches[keyword].append((timestamp, url))
                                mark_url_processed(url)

                time.sleep(10)  # Increase pause between submissions

            # Prepare email content
            email_body = "<html><body>"
            email_body += f"<h2>Keyword Matches in Subreddit: {SUBREDDIT_NAME}</h2>"

            for keyword, urls in matches.items():
                if urls:
                    email_body += f"<h3>Keyword: {keyword}</h3><ul>"
                    sorted_urls = sorted(urls, key=lambda x: x[0])
                    for timestamp, url in sorted_urls:
                        email_body += f"<li>[{timestamp}] <a href='{url}'>{url}</a></li>"
                    email_body += "</ul>"

            email_body += "</body></html>"

            if any(matches.values()):  # Send email only if there are matches
                send_email("Reddit Keyword Alert Summary", email_body)

            print("Waiting 12 hours before next scan...")
            time.sleep(43200)
        except praw.exceptions.APIException as api_err:
            print(f"API error occurred: {api_err}")
            time.sleep(60)  # Wait a minute before retrying
        except AttributeError as attr_err:
            print(f"Attribute error occurred: {attr_err}")
            time.sleep(60)
        except Exception as generic_err:
            print(f"An error occurred: {generic_err}")
            time.sleep(600)  # Wait 10 minutes before retrying

if __name__ == "__main__":
    try:
        monitor_subreddit()
    except KeyboardInterrupt:
        print("Program terminated by user.")
    except Exception as main_err:
        print(f"An error occurred in the main block: {main_err}")