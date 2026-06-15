import os
import re
import requests
import discord
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
SECRET = os.getenv("SECRET")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def send_to_sheets(user, user_id, action, duration, message):
    payload = {
        "secret": SECRET,
        "user": user,
        "userId": user_id,
        "action": action,
        "service": "Service",
        "duration": duration,
        "message": message
    }

    requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)

@client.event
async def on_ready():
    print(f"Connecté en tant que {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != LOG_CHANNEL_ID:
        return

    if message.author.bot is False:
        return

    text = message.content or ""

    for embed in message.embeds:
        if embed.title:
            text += "\n" + embed.title
        if embed.description:
            text += "\n" + embed.description

    if "pointé de sortie" in text.lower():
        action = "Fin"
    elif "pointé" in text.lower():
        action = "Début"
    else:
        return
  user = "Inconnu"
user_id = ""

if message.mentions:
    member = message.mentions[0]
    user = member.display_name
    user_id = str(member.id)

duration_match = re.search(r"ajoutant (.+?) au temps total", text)
duration = duration_match.group(1).strip() if duration_match else ""

    send_to_sheets(user, user_id, action, duration, text)
    print(f"Envoyé : {user} - {action} - {duration}")

client.run(DISCORD_TOKEN)
