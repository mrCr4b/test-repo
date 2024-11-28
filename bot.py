import requests
import csv
import smtplib
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cấu hình GitHub API và email
GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}
SEARCH_API_URL = 'https://api.github.com/search/code'
KEYWORDS_FILE = 'keywords.txt'  # Tệp chứa các từ khóa
USER_FILE = 'user.txt'  # Tệp chứa các user (chủ sở hữu)
OUTPUT_CSV = 'search_results.csv'  # Tệp đầu ra

# Cấu hình email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'scansensitivein4ontgithub@gmail.com'
EMAIL_PASSWORD = 'ssxn nhre mirh lztn'
RECIPIENT_EMAIL = 'icefish.t.2021@gmail.com'

# Hàm gửi email
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email thông báo đã được gửi!")

def load_processed_results():
    processed = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Tạo một khóa duy nhất kết hợp từ khóa và URL
                key = (row['keyword'], row['html_url'])
                processed.add(key)
    return processed

def get_search_results(keyword, user):
    """Tìm kiếm từ khóa trên GitHub cho một user cụ thể và trả về kết quả."""
    query = f'"{keyword}"'  # Bao quanh từ khóa bằng dấu ngoặc kép
    params = {'q': f'{query} user:{user}'}  # Không sử dụng dấu cộng (+) ở đây
    print(f"Truy vấn API: {params['q']}")  # In ra truy vấn để kiểm tra cú pháp
    response = requests.get(SEARCH_API_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Lỗi {response.status_code}: {response.text}")
        return []

def main():
    processed_results = load_processed_results()
    new_results = []

    # Đọc danh sách các chủ sở hữu từ user.txt
    with open(USER_FILE, 'r') as f:
        users = [line.strip() for line in f if line.strip()]

    # Đọc từ khóa từ keywords.txt
    with open(KEYWORDS_FILE, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]

    # Kiểm tra xem tệp CSV có tồn tại không
    if not os.path.exists(OUTPUT_CSV):
        print(f"Tệp '{OUTPUT_CSV}' không tồn tại. Đang tạo mới...")
    
    # Mở tệp CSV để lưu kết quả
    with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['keyword', 'html_url', 'repository_full_name', 'repository_id', 'score', 'sha']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Nếu tệp CSV trống, thêm header
        if csv_file.tell() == 0:
            writer.writeheader()

        # Lặp qua danh sách các chủ sở hữu và từ khóa
        for user in users:
            for keyword in keywords:
                print(f"Tìm kiếm từ khóa: '{keyword}' cho user: {user}")
                results = get_search_results(keyword, user)

                # Kiểm tra nếu có kết quả từ API
                if not results:
                    print(f"Không có kết quả tìm kiếm cho '{keyword}' trong repo của '{user}'.")
                
                for item in results:
                    result_key = (keyword, item['html_url'])  # Sử dụng từ khóa và URL làm khóa duy nhất
                    if result_key not in processed_results:
                        # Lấy sha từ response và lưu vào CSV
                        sha = item.get('sha', 'N/A')  # Nếu không có sha, ghi 'N/A'
                        
                        # Nếu là kết quả mới, lưu vào CSV và thêm vào danh sách gửi email
                        print(f"Ghi kết quả: {item['html_url']}, SHA: {sha}")
                        writer.writerow({
                            'keyword': keyword,
                            'html_url': item['html_url'],
                            'repository_full_name': item['repository']['full_name'],
                            'repository_id': item['repository']['id'],
                            'score': item['score'],
                            'sha': sha  # Lưu sha vào CSV
                        })
                        new_results.append(result_key)
                        processed_results.add(result_key)

    # Gửi email nếu có kết quả mới
    if new_results:
        body = "Đã phát hiện thông tin nhạy cảm mới:\n\n" + "\n".join([f"Keyword: {key[0]}, URL: {key[1]}" for key in new_results])
        send_email("Thông báo phát hiện thông tin nhạy cảm", body)
    else:
        print("Không có kết quả mới.")

if __name__ == "__main__":
    # Chạy mã trong một vòng lặp vô tận, quét mỗi 30 phút
    while True:
        main()
        print("Chờ 30 phút trước khi quét lại...")
        time.sleep(1800)  # 1800 giây = 30 phút
