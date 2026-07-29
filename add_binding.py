with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

binding = "POSApp._load_bo_backup_restore = FlipChartModal._load_bo_backup_restore\n"
if "POSApp._load_bo_backup_restore" not in content:
    content += binding
    with open('app_gui.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Method binding added for POSApp._load_bo_backup_restore!")
