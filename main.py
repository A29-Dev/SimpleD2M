import os
import json
import asyncio
import requests
from datetime import datetime
from threading import Thread
from flask import Flask, request, jsonify, render_template
import discord
from discord.ext import commands

# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
USER_FILE = os.path.join(BASE_DIR, "users.json")

# --- CONFIG LOADING ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    print("🔧 First-time setup:")
    token = input("Enter your Discord bot token: ").strip()
    guild_id = input("Enter your Discord server ID (Guild ID): ").strip()

    config = {
        "DISCORD_TOKEN": token,
        "GUILD_ID": int(guild_id)
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
        print("✅ Config saved to config.json")

    return config

config = load_config()
DISCORD_TOKEN = config["DISCORD_TOKEN"]
GUILD_ID = config["GUILD_ID"]
PORT = 5000
VERIFIED_ROLE_NAME = "Verified"

# --- FLASK SETUP ---
app = Flask(__name__)

# --- DISCORD SETUP ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return []

def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_uuid(username):
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 200:
        return response.json().get("id")
    return None

@app.route("/")
def index():
    return render_template("fabcord_users.html")

@app.route("/api/users", methods=["GET"])
def get_users():
    return jsonify(load_users())

@app.route("/api/remove", methods=["POST"])
def remove_user():
    data = request.json
    discord_name = data.get("discord")
    if not discord_name:
        return jsonify({"status": "error", "message": "No Discord name provided"}), 400
    users = load_users()
    new_users = [u for u in users if u["discord"] != discord_name]
    save_users(new_users)
    return jsonify({"status": "success"})

@app.route("/api/verify", methods=["POST"])
def verify_user():
    data = request.json
    discord_name = data.get("discord")
    if not discord_name:
        return jsonify({"status": "error", "message": "No Discord name provided"}), 400
    future = asyncio.run_coroutine_threadsafe(assign_verified_role(discord_name), bot.loop)
    result = future.result()
    return jsonify({"status": "success" if result else "failed"})

async def assign_verified_role(discord_name):
    try:
        for guild in bot.guilds:
            if guild.id == GUILD_ID:
                member = discord.utils.find(lambda m: str(m) == discord_name, guild.members)
                if not member:
                    return False
                role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
                if not role:
                    return False
                await member.add_roles(role)
                users = load_users()
                for user in users:
                    if user["discord"] == str(member):
                        user["verified"] = True
                        break
                save_users(users)
                return True
    except Exception as e:
        print(f"❌ Error assigning role: {e}")
    return False

@app.route("/api/unverify", methods=["POST"])
def unverify_user():
    data = request.json
    discord_name = data.get("discord")
    if not discord_name:
        return jsonify({"status": "error", "message": "No Discord name provided"}), 400
    future = asyncio.run_coroutine_threadsafe(remove_verified_role(discord_name), bot.loop)
    result = future.result()
    return jsonify({"status": "success" if result else "failed"})

async def remove_verified_role(discord_name):
    try:
        for guild in bot.guilds:
            if guild.id == GUILD_ID:
                member = discord.utils.find(lambda m: str(m) == discord_name, guild.members)
                if not member:
                    return False
                role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
                if not role:
                    return False
                await member.remove_roles(role)
                users = load_users()
                for user in users:
                    if user["discord"] == str(member):
                        user["verified"] = False
                        break
                save_users(users)
                return True
    except Exception as e:
        print(f"❌ Error removing role: {e}")
    return False

@bot.event
async def on_ready():
    print(f"✅ Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command()
async def fabcord(ctx):
    try:
        await ctx.author.send("👋 What's your Minecraft username?")
    except discord.Forbidden:
        await ctx.reply("❌ I couldn't DM you. Please enable DMs.")
        return

    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

    try:
        msg = await bot.wait_for("message", timeout=60.0, check=check)
        mc_username = msg.content.strip()
        uuid = get_uuid(mc_username)
        if not uuid:
            await ctx.author.send(f"❌ No Minecraft account found with `{mc_username}`.")
            return
        now = datetime.utcnow().isoformat() + "Z"
        users = load_users()
        users = [u for u in users if u["discord"] != str(ctx.author)]
        new_entry = {
            "discord": str(ctx.author),
            "minecraft": mc_username,
            "uuid": uuid,
            "timestamp": now,
            "verified": False
        }
        users.append(new_entry)
        save_users(users)
        await ctx.author.send(f"✅ Saved!\n**Minecraft:** {mc_username}\n**UUID:** {uuid}")
    except asyncio.TimeoutError:
        await ctx.author.send("⌛ Timed out. Please try `!fabcord` again.")

@bot.command()
async def listplayers(ctx):
    users = load_users()
    if not users:
        await ctx.send("📭 No players registered yet.")
        return
    msg_lines = ["🧑‍💻 **Registered Players:**"]
    for entry in users:
        verified_status = "✅" if entry.get("verified") else "❌"
        msg_lines.append(f"• **{entry['minecraft']}** ({verified_status}) (Discord: {entry['discord']})")
    message = "\\n".join(msg_lines)
    await ctx.send(message[:2000])

@bot.command()
async def verify(ctx):
    guild = ctx.guild
    member = ctx.author
    if not guild:
        await ctx.send("❌ Use this command in a server.")
        return
    role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if not role:
        await ctx.send(f"❌ Role `{VERIFIED_ROLE_NAME}` not found.")
        return
    try:
        await member.add_roles(role)
        users = load_users()
        for user in users:
            if user["discord"] == str(member):
                user["verified"] = True
                break
        save_users(users)
        await ctx.send(f"✅ {member.mention}, you are now verified.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to assign that role.")


@bot.command()
async def sync_verified(ctx):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if not role:
        await ctx.send(f"❌ Role '{VERIFIED_ROLE_NAME}' not found.")
        return

    users = load_users()
    known_discords = {user["discord"] for user in users}
    new_entries = 0
    prompted = 0

    for member in guild.members:
        if role in member.roles and str(member) not in known_discords:
            new_entry = {
                "discord": str(member),
                "minecraft": "Unknown",
                "uuid": "unknown",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "verified": True
            }
            users.append(new_entry)
            new_entries += 1

            # DM the user
            try:
                await member.send("👋 We had an error getting your Minecraft username. Can you please tell me what it is?")
                
                def check(m):
                    return m.author == member and isinstance(m.channel, discord.DMChannel)

                msg = await bot.wait_for("message", timeout=60.0, check=check)
                mc_username = msg.content.strip()
                uuid = get_uuid(mc_username)

                if uuid:
                    for u in users:
                        if u["discord"] == str(member):
                            u["minecraft"] = mc_username
                            u["uuid"] = uuid
                            break
                    await member.send(f"✅ Thanks! You’ve been updated with username `{mc_username}`.")
                else:
                    await member.send(f"❌ I couldn’t find a Minecraft account called `{mc_username}`. Please try again later with !fabcord.")

            except discord.Forbidden:
                await ctx.send(f"❌ Couldn't DM {member}.")
            except asyncio.TimeoutError:
                await member.send("⌛ Timed out waiting for response. You can run !fabcord later.")

    save_users(users)
    await ctx.send(f"✅ Sync complete: {new_entries} new verified users processed.")

def start_flask():
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    Thread(target=start_flask).start()
    bot.run(DISCORD_TOKEN)