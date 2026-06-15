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
intents.members = True

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

    response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
    print("Réponse Google Sheets :", response.text)


def get_embed_text(message):
    text = message.content or ""

    for embed in message.embeds:
        if embed.title:
            text += "\n" + embed.title
        if embed.description:
            text += "\n" + embed.description

    return text


async def get_member_info(message, text):
    user_id = ""
    user_name = "Inconnu"

    match = re.search(r"<@!?(\d+)>", text)

    if match:
        user_id = match.group(1)

        member = message.guild.get_member(int(user_id))

        if member is None:
            try:
                member = await message.guild.fetch_member(int(user_id))
            except Exception:
                member = None

        if member:
            user_name = member.display_name
        else:
            user_name = user_id

    return user_name, user_id


@client.event
async def on_ready():
    print(f"Bot connecté : {client.user}")


@client.event
async def on_message(message):
    if message.channel.id != LOG_CHANNEL_ID:
        return

    if not message.author.bot:
        return

    text = get_embed_text(message)
    text_lower = text.lower()

    if "pointé de sortie" in text_lower:
        action = "Fin"
    elif "pointé" in text_lower:
        action = "Début"
    else:
        return

    user, user_id = await get_member_info(message, text)

    duration = ""
    duration_match = re.search(
        r"ajoutant (.+?) au temps total",
        text,
        re.IGNORECASE
    )

    if duration_match:
        duration = duration_match.group(1).strip()

    clean_message = text.replace("\n", " ")

    send_to_sheets(user, user_id, action, duration, clean_message)

    print(f"Envoyé : {user} | {user_id} | {action} | {duration}")


client.run(DISCORD_TOKEN)
