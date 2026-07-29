with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

bad_block = """    def _open_dept_manager_modal(self):
    DeptSubdeptManagerModal(self)"""

good_block = """    def _open_dept_manager_modal(self):
        DeptSubdeptManagerModal(self)"""

if bad_block in content:
    content = content.replace(bad_block, good_block)

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Indentation fixed in app_gui.py!")
