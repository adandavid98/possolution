with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'from config import Config' not in content:
    content = "from config import Config\n" + content
    with open('app_gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("from config import Config added to top of app_gui.py!")
else:
    print("from config import Config already present in app_gui.py")
