with open('app_gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

clean_lines = [l for l in lines if 'POSApp._load_bo_backup_restore = FlipChartModal._load_bo_backup_restore' not in l]

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print("Offending line removed from app_gui.py!")
