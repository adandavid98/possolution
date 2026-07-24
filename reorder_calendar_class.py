with open('app_gui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract CTkCalendarPopup definition from top
marker_end = "class CTkCalendarPopup(ctk.CTkToplevel):"
top_part, rest = content.split("class CTkCalendarPopup(ctk.CTkToplevel):", 1)

popup_code, remaining = rest.split("import os\nimport sys", 1)

popup_full_code = "class CTkCalendarPopup(ctk.CTkToplevel):" + popup_code

# Reconstruct cleanly with imports FIRST
new_content = "import os\nimport sys" + remaining
insert_pos = "from report_pdf import generate_pdf_report, print_pdf_file\n"

if insert_pos in new_content:
    new_content = new_content.replace(insert_pos, insert_pos + "\nimport calendar\n\n" + popup_full_code + "\n\n")

with open('app_gui.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Calendar class reordering complete.")
