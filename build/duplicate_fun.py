from auth import get_services

with open("spreadsheet_id.txt") as f:
    SPREADSHEET_ID = f.read().strip()

sheets, drive = get_services()

body = {"name": "Monthly Budget Tracker (Fun)"}
result = drive.files().copy(fileId=SPREADSHEET_ID, body=body, fields="id,name,webViewLink").execute()
print(result)

with open("spreadsheet_id_fun.txt", "w") as f:
    f.write(result["id"])
