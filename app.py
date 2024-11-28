import requests
import csv
import smtplib
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Cấu hình GitHub API và email
GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}'
}
SEARCH_API_URL = 'https://api.github.com/search/code'
OUTPUT_CSV = 'search_results.csv'  # Tệp đầu ra

# Cấu hình email cố định
EMAIL_USER = 'scansensitivein4ontgithub@gmail.com'  # Email gửi cố định
EMAIL_PASSWORD = 'ssxn nhre mirh lztn'  # Mật khẩu email gửi cố định
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Hàm gửi email
def send_email(subject, body, recipient_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = recipient_email  # Email nhận thông báo
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email thông báo đã được gửi!")
    except Exception as e:
        messagebox.showerror("Error", f"Không thể gửi email: {e}")

# Hàm tải kết quả đã xử lý để tránh ghi trùng
def load_processed_results():
    processed = set()
    if os.path.exists(OUTPUT_CSV):
        with open(OUTPUT_CSV, mode='r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                key = (row['keyword'], row['html_url'])
                processed.add(key)
    return processed

# Hàm tìm kiếm API GitHub
def get_search_results(keyword, user):
    query = f'"{keyword}"'  # Bao quanh từ khóa bằng dấu ngoặc kép
    params = {'q': f'{query} user:{user}'}  # Truy vấn tìm kiếm theo người dùng
    print(f"Truy vấn API: {params['q']}")
    response = requests.get(SEARCH_API_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print(f"Lỗi {response.status_code}: {response.text}")
        return []

# Hàm lưu kết quả vào CSV
def save_results_to_csv(results, processed_results, writer, keyword):
    new_results = []
    for item in results:
        result_key = (keyword, item['html_url'])  # Sử dụng 'keyword' và 'html_url' làm khóa duy nhất
        if result_key not in processed_results:
            sha = item.get('sha', 'N/A')  # Lấy sha hoặc 'N/A' nếu không có
            writer.writerow({
                'keyword': keyword,  # Lưu từ khóa vào CSV
                'html_url': item['html_url'],
                'repository_full_name': item['repository']['full_name'],
                'repository_id': item['repository']['id'],
                'score': item['score'],
                'sha': sha  # Lưu sha vào CSV
            })
            new_results.append(result_key)
            processed_results.add(result_key)
    return new_results

# Hàm quét một lần
def scan_once(user_file, keyword_file, log_text_widget, recipient_email):
    users = []
    keywords = []

    # Đọc danh sách người dùng
    try:
        with open(user_file, 'r') as f:
            users = [line.strip() for line in f if line.strip()]
    except Exception as e:
        messagebox.showerror("Error", f"Không thể đọc tệp người dùng: {e}")
        return

    # Đọc danh sách từ khóa
    try:
        with open(keyword_file, 'r') as f:
            keywords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        messagebox.showerror("Error", f"Không thể đọc tệp từ khóa: {e}")
        return

    processed_results = load_processed_results()

    # Mở tệp CSV để lưu kết quả
    with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['keyword', 'html_url', 'repository_full_name', 'repository_id', 'score', 'sha']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Nếu tệp CSV trống, thêm header
        if csv_file.tell() == 0:
            writer.writeheader()

        new_results = []

        # Lặp qua danh sách các chủ sở hữu và từ khóa
        for user in users:
            for keyword in keywords:
                log_text_widget.insert(tk.END, f"Tìm kiếm từ khóa: '{keyword}' cho user: {user}\n")
                log_text_widget.yview(tk.END)
                results = get_search_results(keyword, user)

                if not results:
                    log_text_widget.insert(tk.END, f"Không có kết quả tìm kiếm cho '{keyword}' trong repo của '{user}'.\n")
                    continue

                new_results += save_results_to_csv(results, processed_results, writer, keyword)

                # In kết quả ra log_text_widget
                for item in results:
                    log_text_widget.insert(tk.END, f"Found: {item['html_url']} in repository: {item['repository']['full_name']}\n")
                    log_text_widget.insert(tk.END, f"Score: {item['score']}, SHA: {item.get('sha', 'N/A')}\n")
                    log_text_widget.yview(tk.END)

    # Gửi email nếu có kết quả mới
    if new_results:
        body = "Đã phát hiện thông tin nhạy cảm mới:\n\n" + "\n".join([f"Keyword: {key[0]}, URL: {key[1]}" for key in new_results])
        send_email("Thông báo phát hiện thông tin nhạy cảm", body, recipient_email)
    else:
        log_text_widget.insert(tk.END, "Không có kết quả mới.\n")
        log_text_widget.yview(tk.END)

# Hàm lưu nội dung từ Text widget vào file
def save_to_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except Exception as e:
        messagebox.showerror("Error", f"Không thể lưu tệp: {e}")

# Hàm tải nội dung tệp vào Text widget
def load_file_content(file_path, text_widget):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        text_widget.delete(1.0, tk.END)  # Xóa nội dung cũ
        text_widget.insert(tk.END, content)  # Hiển thị nội dung mới
    except Exception as e:
        messagebox.showerror("Error", f"Không thể tải nội dung tệp: {e}")

# Giao diện đồ họa
def run_app():
    root = tk.Tk()
    root.title("Quét GitHub - Tìm kiếm thông tin nhạy cảm")

    # Tạo frame chính
    frame = tk.Frame(root)
    frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Khung 1: Tệp người dùng
    frame_user = tk.Frame(frame)
    frame_user.grid(row=0, column=0, padx=5, pady=5, sticky="w")

    tk.Label(frame_user, text="Chọn tệp user.txt").grid(row=0, column=0, sticky="w", padx=5)
    user_file = tk.Entry(frame_user, width=50)
    user_file.grid(row=0, column=1, padx=5)

    def browse_user_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            user_file.delete(0, tk.END)
            user_file.insert(tk.END, file_path)
            load_file_content(file_path, user_text_widget)

    tk.Button(frame_user, text="Chọn tệp người dùng", command=browse_user_file).grid(row=0, column=2, padx=5)

    user_text_widget = tk.Text(frame_user, width=50, height=5)
    user_text_widget.grid(row=1, column=0, columnspan=3, pady=10)

    def save_user_file():
        save_to_file(user_file.get(), user_text_widget.get("1.0", tk.END))

    tk.Button(frame_user, text="Lưu tệp người dùng", command=save_user_file).grid(row=2, column=0, columnspan=3, pady=5)

    # Khung 2: Tệp từ khóa
    frame_keyword = tk.Frame(frame)
    frame_keyword.grid(row=1, column=0, padx=5, pady=5, sticky="w")

    tk.Label(frame_keyword, text="Chọn tệp keyword.txt").grid(row=0, column=0, sticky="w", padx=5)
    keyword_file = tk.Entry(frame_keyword, width=50)
    keyword_file.grid(row=0, column=1, padx=5)

    def browse_keyword_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            keyword_file.delete(0, tk.END)
            keyword_file.insert(tk.END, file_path)
            load_file_content(file_path, keyword_text_widget)

    tk.Button(frame_keyword, text="Chọn tệp từ khóa", command=browse_keyword_file).grid(row=0, column=2, padx=5)

    keyword_text_widget = tk.Text(frame_keyword, width=50, height=5)
    keyword_text_widget.grid(row=1, column=0, columnspan=3, pady=10)

    def save_keyword_file():
        save_to_file(keyword_file.get(), keyword_text_widget.get("1.0", tk.END))

    tk.Button(frame_keyword, text="Lưu tệp từ khóa", command=save_keyword_file).grid(row=2, column=0, columnspan=3, pady=5)

    # Khung 3: Nhập email
    frame_email = tk.Frame(frame)
    frame_email.grid(row=2, column=0, padx=5, pady=5, sticky="w")

    tk.Label(frame_email, text="Nhập email nhận thông báo").grid(row=0, column=0, pady=5, sticky="w")
    recipient_email = tk.Entry(frame_email, width=50)
    recipient_email.grid(row=0, column=1, pady=5)

    # Khung 4: Nút quét và kết quả
    frame_scan = tk.Frame(frame)
    frame_scan.grid(row=3, column=0, padx=5, pady=5, sticky="w")

    tk.Button(frame_scan, text="Quét 1 lần", command=lambda: scan_once(user_file.get(), keyword_file.get(), log_text_widget, recipient_email.get())).grid(row=0, column=0, columnspan=3, pady=10)

    log_text_widget = tk.Text(frame_scan, width=80, height=20)
    log_text_widget.grid(row=1, column=0, columnspan=3, pady=10)

    root.mainloop()

if __name__ == "__main__":
    run_app()
