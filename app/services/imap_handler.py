import imaplib
import email
import os
from app.dmarc.processor import decompress_gz_file, process_dmarc_report
from config.settings import *

def connect_mailbox():
    if IMAP_SSL:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    else:
        mail = imaplib.IMAP4(IMAP_SERVER, IMAP_PORT)
    mail.login(IMAP_EMAIL, IMAP_PASSWORD)
    mail.select('inbox')
    return mail

def fetch_dmarc_attachments(mail):
    typ, data = mail.search(None, 'ALL')
    mail_ids = data[0].split()
    attachments = []
    if not os.path.exists(IMAP_DOWNLOAD_DIR):
        print(f"📁 Folder {IMAP_DOWNLOAD_DIR} not found, creating it now...")
        os.makedirs(IMAP_DOWNLOAD_DIR)

    for num in mail_ids:
        typ, data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = part.get("Content-Disposition")
                if content_disposition and 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename and filename.endswith('.xml.gz'):
                        filepath = os.path.join(IMAP_DOWNLOAD_DIR, filename)
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        attachments.append(filepath)
    return attachments

def check_incoming_emails():
    mail = connect_mailbox()
    try:
        gz_files = fetch_dmarc_attachments(mail)
        for gz_file in gz_files:
            xml_file = decompress_gz_file(gz_file)
            process_dmarc_report(xml_file)
    except Exception as e:
        if debug_level("ERROR"):
            print(f"❌ Error while fetching IMAP emails : {e}")
