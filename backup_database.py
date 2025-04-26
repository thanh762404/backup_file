import os
import shutil
import schedule
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình thông tin email từ file .env
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# Đường dẫn thư mục chứa database và thư mục backup
DB_FOLDER = "databases"
BACKUP_FOLDER = "backups"

# Hàm gửi email thông báo
def send_email(subject, body):
    try:
        # Cấu hình server SMTP của Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)

        # Tạo nội dung email
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        # Gửi email
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Gửi email thành công!")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")

# Hàm backup database
def backup_database():
    try:
        # Tạo thư mục backup nếu chưa có
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)

        # Lấy thời gian hiện tại để đặt tên file backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Duyệt qua tất cả file trong thư mục database
        for file_name in os.listdir(DB_FOLDER):
            # Kiểm tra file có đuôi .sql hoặc .sqlite3
            if file_name.endswith((".sql", ".sqlite3")):
                # Đường dẫn file gốc và file backup
                src_path = os.path.join(DB_FOLDER, file_name)
                backup_file = f"{file_name.split('.')[0]}_backup_{timestamp}.{file_name.split('.')[-1]}"
                dst_path = os.path.join(BACKUP_FOLDER, backup_file)
                
                # Copy file
                shutil.copy2(src_path, dst_path)
                print(f"Backup thành công: {file_name}")

        # Gửi email thông báo thành công
        send_email(
            "Backup Database Thành Công",
            f"Backup database đã hoàn tất lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."
        )
    except Exception as e:
        # Gửi email thông báo thất bại
        send_email(
            "Backup Database Thất Bại",
            f"Lỗi khi backup database: {str(e)}"
        )
        print(f"Lỗi khi backup: {e}")

# Lên lịch backup lúc 00:00 hàng ngày
# Giả sử bây giờ là 21:30, thì ghi:
schedule.every(1).minutes.do(backup_database)



# Vòng lặp chạy lịch
while True:
    schedule.run_pending()
    time.sleep(60)  # Chờ 1 phút trước khi kiểm tra lại