import os
import smtplib
from email.mime.text import MIMEText

sender_email = os.environ.get("OUTLOOK_EMAIL")
sender_password = os.environ.get("OUTLOOK_PASSWORD")

google_sender_email = os.environ.get("GOOGLE_EMAIL")
google_sender_password = os.environ.get("GOOGLE_PASSWORD")

def send_outlook_email(subject, body, to_email):

    print("sender_email", sender_email)
    print("sender_password", sender_password)

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
        return "아웃룩 메일 발송 성공!"
    except Exception as e:
        print(f"아웃룩 메일 발송 실패: {e}")
        return f"아웃룩 메일 발송 실패: {e}"


def send_google_email(subject, body, to_email):

    print("google_sender_email", google_sender_email)
    print("google_sender_password", google_sender_password)
    print("to_email", to_email)
        
    # SMTP 설정 (예: Gmail 기준)
    smtp_server = "smtp.gmail.com"
    port = 587

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = google_sender_email
    msg["To"] = to_email
    try:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # 보안 연결 시작
            server.login(google_sender_email, google_sender_password)
            server.sendmail(google_sender_email, to_email, msg.as_string())
        print("이메일 발송 성공!")
        return "이메일 발송 성공!"
    except Exception as e:
        print(f"이메일 발송 실패: {e}")
        return f"이메일 발송 실패: {e}"