import json

# Đọc tệp JSON chứa thông tin nhạy cảm
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Sử dụng thông tin từ tệp JSON
db_user = config['db_user']
db_pass = config['db_pass']
api_key = config['api_key']

print(f"Connecting with user: {db_user}")
