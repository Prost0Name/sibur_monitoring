import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

SENDER_EMAIL = "bogodpav@gmail.com"  # константа, емаил с которого идут письма
PASSWORD = "nwyc fhwc wsvi krnm"  # константа, пароль емаила с которого идут письма


class Email:
    def __init__(self, priority, receiver_email, description=None, message=None, status=None, type=None, author=None, time=None):
        self.priority = priority  # приоритет
        self.description = description  # название
        self.message = message  # описание
        self.status = status  # статус
        self.type = type  # тип
        self.author = author  # автор
        self.receiver_email = receiver_email  # кому отправляем
        self.time = time  # время

    def send_new_email(self):
        subject = self.description if self.description else "ПРОБЛЕМА"  # заголовок письма

        # Устанавливаем цвет заголовка в зависимости от приоритета
        color = "#FFFFFF"  # по умолчанию белый
        if self.priority == "INFO":
            color = "#4285f4"  # синий
        elif self.priority == "CRIT":
            color = "#ea4335"  # красный
        elif self.priority == "WARN":
            color = "#f4b400"  # желтый

        # HTML-содержимое письма
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9;">
                    <h1 style="color: {color}; font-size: 24px; text-align: center;">{subject}</h1>
                    <hr style="border: none; height: 1px; background-color: #ccc; margin: 20px 0;">
        """
        if self.author:
            body += f"<p><strong>Отправитель:</strong> {self.author}</p>"
        if self.message:
            body += f"<p style='font-size: 18px;'><strong>Описание:</strong> {self.message}</p>"
        if self.type:
            body += f"<p style='font-size: 18px;'><strong>Тип:</strong> {self.type}</p>"
        body += f"<p style='font-size: 18px;'><strong>От:</strong> {self.time.strftime('%Y-%m-%d %H:%M:%S') if self.time else 'Не указано'}</p>"
        # print(f'{os.getenv("URL")}:{os.getenv("PORT")}')
        body += f'<p><strong>Подробнее на сайте: </strong>{os.getenv("URL")}:{os.getenv("PORT")}</p>'
        body += """
                    <p style="font-size: 14px; color: #666;">С уважением,<br>Critical Alert System</p>
                </div>
            </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = self.receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, PASSWORD)

            server.sendmail(SENDER_EMAIL, self.receiver_email, msg.as_string())
            logger.info(f"Письмо успешно отправлено: {self.receiver_email}, {self.type}")

        except Exception as e:
            logger.critical(f"Произошла ошибка: {e}")

        finally:
            server.quit()
