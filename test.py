import requests
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cấu hình GitHub API và email
GITHUB_TOKEN = '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'  # Thay bằng token của bạn
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}
SEARCH_API_URL = 'https://api.github.com/search/code'
KEYWORDS_FILE = 'keywords.txt'  # Tệp chứa các từ khóa
OUTPUT_CSV = 'search_results.csv'  # Tệp đầu ra

# Cấu hình email
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USER = 'scansensitivein4ontgithub@gmail.com'
EMAIL_PASSWORD = 'Sc@n_in4'
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
    try:
        with open(OUTPUT_CSV, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Tạo một khóa duy nhất kết hợp từ khóa và URL
                key = (row['keyword'], row['html_url'])
                processed.add(key)
    except FileNotFoundError:
        # Nếu file chưa tồn tại, bỏ qua
        pass
    return processed

def get_search_results(keyword):
    """Tìm kiếm từ khóa trên GitHub và trả về kết quả."""
    query = f'"{keyword}"'
    params = {'q': query}
    response = requests.get(SEARCH_API_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Lỗi {response.status_code}: {response.text}")
        return []

def main():
    processed_results = load_processed_results()
    new_results = []

    with open(KEYWORDS_FILE, 'r') as f:
        keywords = [line.strip() for line in f if line.strip()]

    with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['keyword', 'html_url', 'repository_full_name', 'repository_id', 'score']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # Chỉ ghi header nếu file chưa có
        if csv_file.tell() == 0:
            writer.writeheader()

        for keyword in keywords:
            print(f"Tìm kiếm từ khóa: {keyword}")
            results = get_search_results(keyword)
            
            for item in results:
                result_key = (keyword, item['html_url'])  # Sử dụng từ khóa và URL làm khóa duy nhất
                if result_key not in processed_results:
                    # Nếu là kết quả mới, lưu vào CSV và thêm vào danh sách gửi email
                    writer.writerow({
                        'keyword': keyword,
                        'html_url': item['html_url'],
                        'repository_full_name': item['repository']['full_name'],
                        'repository_id': item['repository']['id'],
                        'score': item['score']
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
    main()
