with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the tail assignment with a function definition and assignment to both classes
old_tail = """POSApp._load_bo_backup_restore = FlipChartModal._load_bo_backup_restore"""

new_tail = """
# Bind backup & restore subtab method to FlipChartModal and POSApp
FlipChartModal._load_bo_backup_restore = _load_bo_backup_restore
POSApp._load_bo_backup_restore = _load_bo_backup_restore
"""

if "def _load_bo_backup_restore(self, parent):" in content:
    content = content.replace("def _load_bo_backup_restore(self, parent):", "def _load_bo_backup_restore(self, parent):")

if old_tail in content:
    content = content.replace(old_tail, new_tail)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app_gui.py updated with standalone _load_bo_backup_restore method binding!")
