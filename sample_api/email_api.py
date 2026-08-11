import os
import smtplib
from email.mime.text import MIMEText

sender_email = os.environ.get("OUTLOOK_EMAIL")
sender_password = os.environ.get("OUTLOOK_PASSWORD")

print("sender_email", sender_email)
print("sender_password", sender_password)

def send_outlook_email(subject, body, to_email):
    # 1. 아웃룩(Office 365) 공식 SMTP 설정
    smtp_server = "smtp.office365.com"  # 또는 "smtp-mail.outlook.com"
    port = 587                          # TLS 포트
    
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        # 2. 아웃룩 서버는 반드시 STARTTLS 연결이 필요합니다.
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()
        server.starttls()  # TLS 보안 연결 활성화
        server.ehlo()
        
        # 3. 로그인 및 발송
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.close()
        print("아웃룩 메일 발송 성공!")
    except Exception as e:
        print(f"아웃룩 메일 발송 실패: {e}")