import os
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import datetime

# Discord bot token
TOKEN = os.getenv("TOKEN")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# Load the credentials from the environment variable (as a JSON string)
import json
creds_data = json.loads(os.getenv("GCP_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_data, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("McCoords").sheet1

# Regex pattern to extract place and coordinates
COORD_PATTERN = re.compile(r"^(.*?) \((-?\d+), (-?\d+)(?:, (-?\d+))?\)$", re.IGNORECASE)

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    content = message.content.strip()
    
    # Handle coordinate logging
    match = COORD_PATTERN.match(content)
    if match:
        try:
            place_name = match.group(1).strip()
            x = int(match.group(2))
            z = int(match.group(3))
            y = match.group(4)
            y = int(y) if y is not None else ""
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            await message.channel.send("This doesn't seem legit, my dude.🤔 Quickly double check those coords.\n or send \"CoordsGuy\" for help.")
            return

        # Write data to Google Sheets
        sheet.append_row([place_name, x, z, y, timestamp])
        await message.channel.send(f"Got you, fam. 😎\n{place_name} at ({x}, {z}, {y})")

    # Handle "gib" command
    if content.lower().startswith("gib"):
        place_name = content[3:].strip().lower()
        records = sheet.get_all_records()
        matches = [r for r in records if r['Place'].lower() == place_name]
        
        if not matches:
            await message.channel.send("I don't know where that is, bro. ¯\\_(ツ)_/¯")
        else:
            coords_list = [f"({m['x']}, {m['z']}, {m['y']})" for m in matches]
            response = f"{content[7:].strip()} can be found at " + " or ".join(coords_list)
            await message.channel.send(response)

    # Handle bot help command
    if content.lower() in ["coordsguy", "mccoords"]:
        help_message = (
            "📌 **How to Use CoordsGuy** 📌\n"
            "- Log a place: `Place Name (x, z, y)` or `Place Name (x, z)`\n"
            "- Retrieve coordinates: `gib Place Name`\n"
            "- The bot is case-insensitive and stores multiple locations for the same name."
        )
        await message.channel.send(help_message)


# Run the bot
client.run(TOKEN)
