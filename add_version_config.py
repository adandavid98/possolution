with open('config.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_config = """class Config:
    # App Version & Auto-Update URLs
    APP_VERSION = "1.0.0"
    UPDATE_CHECK_URL_GITHUB = "https://raw.githubusercontent.com/adanozoria/Anti-POS_Project/main/version.json"
    UPDATE_CHECK_URL_LOCAL = "http://10.0.0.101:5000/api/version"

    # SQL Server Connection Parameters"""

if "class Config:" in content and "APP_VERSION" not in content:
    content = content.replace("class Config:", new_config)
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("config.py updated with APP_VERSION and update check URLs!")
else:
    print("config.py already contains APP_VERSION or class Config missing")
