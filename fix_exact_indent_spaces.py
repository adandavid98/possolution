with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_def = "        def _open_dept_manager_modal(self):\n        DeptSubdeptManagerModal(self)"
good_def = "    def _open_dept_manager_modal(self):\n        DeptSubdeptManagerModal(self)"

if bad_def in content:
    content = content.replace(bad_def, good_def)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Def replaced correctly!")
