import os
import re
import requests
import discord
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_SCRIPT_URL = os.getenv("GOOGLE_SCRIPT_URL")
SECRET = os.getenv("SECRET")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)


def send_to_sheets(user, user_id, action, duration, message_text):
    payload = {
        "secret": SECRET,
        "user": user,
        "userId": user_id,
        "action": action,
        "service": "Service",
        "duration": duration,
        "message": message_text
    }

    response = requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=10)
    print("Réponse Google Sheets :", response.text)


def get_message_text(message):
    text = message.content or ""

    for embed in message.embeds:
        if embed.title:
            text += "\n" + embed.title

        if embed.description:
            text += "\n" + embed.description

        for field in embed.fields:
            text += f"\n{field.name}\n{field.value}"

        if embed.footer and embed.footer.text:
            text += "\n" + embed.footer.text

        if embed.author and embed.author.name:
            text += "\n" + embed.author.name

    return text


async def get_user_info(message, text):
    user = "Inconnu"
    user_id = ""

    match = re.search(r"<@!?(\d+)>", text)

    if not match:
        return user, user_id

    user_id = match.group(1)
    member = None

    if message.guild:
        member = message.guild.get_member(int(user_id))

        if member is None:
            try:
                member = await message.guild.fetch_member(int(user_id))
            except Exception:
                member = None

    if member:
        user = member.display_name
    else:
        user = user_id

    return user, user_id


def get_action(text):
    text_lower = text.lower()

    if "pointé de sortie" in text_lower:
        return "Fin"

    if "pointé" in text_lower:
        return "Début"

    return None


def get_duration(text):
    match = re.search(
        r"ajoutant (.+?) au temps total",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return ""


@client.event
async def on_ready():
    print(f"Bot connecté : {client.user}")


@client.event
async def on_message(message):
    if message.channel.id != LOG_CHANNEL_ID:
        return

    if not message.author.bot:
        return

    text = get_message_text(message)
    action = get_action(text)

    if action is None:
        return

    user, user_id = await get_user_info(message, text)
    duration = get_duration(text)
    clean_message = text.replace("\n", " ")

    send_to_sheets(user, user_id, action, duration, clean_message)

    print(f"Envoyé : {user} | {user_id} | {action} | {duration}")


client.run(DISCORD_TOKEN)
