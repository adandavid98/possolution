import json, re

with open("recovered_models.py", "r", encoding="utf-8", errors="ignore") as f:
    raw = f.read()

# Find from import database import execute_query to the end of ReportModel
match = re.search(r'(from database import execute_query.*?class ReportModel:.*?def get_dashboard_metrics.*?\n\n)', raw, re.DOTALL)
if match:
    clean_code = match.group(1)
    # Remove escaped quotes / json escape sequences if any
    clean_code = clean_code.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
    with open("models.py", "w", encoding="utf-8") as out:
        out.write(clean_code)
    print("models.py cleaned and restored successfully!")
else:
    print("Match not found, searching class definitions...")
    # Alternative regex search
    classes = re.findall(r'class \w+:.*?(?=class \w+:|\Z)', raw, re.DOTALL)
    print("Found classes count:", len(classes))
