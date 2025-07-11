import imaplib
import email
from email.header import decode_header
from datetime import datetime

def login_to_email(imap_host, email_user, email_pass):
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(email_user, email_pass)
    return mail

def fetch_all_emails(imap_host, email_user, email_pass, folder="INBOX"):
    mail = login_to_email(imap_host, email_user, email_pass)
    mail.select(folder)
    _, data = mail.search(None, "ALL")
    email_ids = data[0].split()

    emails = []
    for eid in reversed(email_ids):
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        emails.append(parse_email(msg, full_body=False))  # Use preview for listings
    mail.logout()
    return emails

def search_emails(imap_host, email_user, email_pass, keyword, folder="INBOX"):
    mail = login_to_email(imap_host, email_user, email_pass)
    mail.select(folder)
    _, data = mail.search(None, "ALL")
    email_ids = data[0].split()

    result = []
    for eid in reversed(email_ids):
        _, msg_data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        parsed = parse_email(msg, full_body=False)  # Use preview for search
        # Search in full body content for better results
        if (keyword.lower() in parsed["subject"].lower()
            or keyword.lower() in parsed["full_body"].lower()
            or keyword.lower() in parsed["from"].lower()
            or keyword.lower() in parsed["date"].lower()):
                    result.append(parsed)
    mail.logout()
    return result

def parse_email(msg, full_body=False):
    subject, encoding = decode_header(msg.get("Subject"))[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8", errors="ignore")

    from_ = msg.get("From")
    date_ = msg.get("Date")
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" and not part.get("Content-Disposition"):
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    # Store full body and truncated version
    full_body_content = body.strip()
    preview_body = full_body_content[:200] if not full_body else full_body_content

    return {
        "subject": subject or "(No Subject)",
        "from": from_,
        "date": date_,
        "body": preview_body,
        "full_body": full_body_content  # Always store full content
    }
