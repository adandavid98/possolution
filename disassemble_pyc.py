import marshal, dis

pyc_path = r"c:\Users\Adan\Documents\Anti-POS_Project\__pycache__\models.cpython-312.pyc"
with open(pyc_path, "rb") as f:
    f.seek(16) # Skip header in Python 3.12 (16 bytes)
    code_obj = marshal.load(f)

print("Code object loaded successfully! Name:", code_obj.co_name)
print("Consts in models.py:")
for const in code_obj.co_consts:
    if hasattr(const, "co_name"):
        print("  Class/Func:", const.co_name)
