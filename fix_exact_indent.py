with open('app_gui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if line.strip() == 'DeptSubdeptManagerModal(self)' and not line.startswith('        '):
        new_lines.append('        DeptSubdeptManagerModal(self)\n')
    else:
        new_lines.append(line)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Line indentation fixed!")
