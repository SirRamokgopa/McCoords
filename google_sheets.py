import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Authenticate using the service account key JSON
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("GcpKeys.json", scope)
client = gspread.authorize(creds)

# Open the spreadsheet by name
sheet = client.open("McCoords").sheet1

# Test writing a row
test_data = ["Test Place", 100, 200, 50, "2025-02-09 12:00:00"]
sheet.append_row(test_data)

print("You did it, dawg! Test data added successfully.")