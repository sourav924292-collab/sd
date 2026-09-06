import os
import json
import requests
import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

Tok = "8918181544:AAF96h6Ps1039gm3SvO4oCTmKpnmhTrHFXY"
Api = "http://51.20.5.41:5000"
Owner = 8590714243
AUTHORIZED_USERS_FILE = "authorized_users.json"
Usr = "@sourav0009"

Cmds = """
/spam {email}
/stop {email}
/status {email}
/list
"""

def load_authorized_users():
    try:
        if os.path.exists(AUTHORIZED_USERS_FILE):
            with open(AUTHORIZED_USERS_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_authorized_users(users):
    try:
        with open(AUTHORIZED_USERS_FILE, 'w') as f:
            json.dump(users, f)
    except:
        pass

AUTHORIZED_USERS = load_authorized_users()

if Owner not in AUTHORIZED_USERS:
    AUTHORIZED_USERS.append(Owner)
    save_authorized_users(AUTHORIZED_USERS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id in AUTHORIZED_USERS:
        message = f"""*Status => Authorized*

*Commands :* 
{Cmds}"""
    else:
        message = """*Status => Not Authorized*

*Gayyyyyyyyy Don't Be Oversmart Go And Buy Access From The Owner : @sourav0009*"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def authorize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != Owner:
        await update.message.reply_text("*Only owner can use this command.*", parse_mode='Markdown')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("*Usage: /a {username or userid}*", parse_mode='Markdown')
        return
    
    target = context.args[0]
    target_id = None
    
    try:
        if target.startswith('@'):
            if update.effective_chat:
                try:
                    chat_member = await context.bot.get_chat_member(
                        update.effective_chat.id, 
                        target
                    )
                    target_id = chat_member.user.id
                except:
                    target_id = None
        else:
            try:
                target_id = int(target)
            except ValueError:
                await update.message.reply_text("*Invalid user ID or username.*", parse_mode='Markdown')
                return
        
        if target_id is None:
            target_id = target
        
        if target_id in AUTHORIZED_USERS:
            await update.message.reply_text("*Already authorized.*", parse_mode='Markdown')
            return
        
        AUTHORIZED_USERS.append(target_id)
        save_authorized_users(AUTHORIZED_USERS)
        
        await update.message.reply_text(f"*Authorized*", parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("*Failed to authorize user.*", parse_mode='Markdown')

async def deauthorize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != Owner:
        await update.message.reply_text("*Only owner can use this command.*", parse_mode='Markdown')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("*Usage: /da {username or userid}*", parse_mode='Markdown')
        return
    
    target = context.args[0]
    target_id = None
    
    try:
        if target.startswith('@'):
            if update.effective_chat:
                try:
                    chat_member = await context.bot.get_chat_member(
                        update.effective_chat.id, 
                        target
                    )
                    target_id = chat_member.user.id
                except:
                    target_id = None
        else:
            try:
                target_id = int(target)
            except ValueError:
                await update.message.reply_text("*Invalid user ID or username.*", parse_mode='Markdown')
                return
        
        if target_id is None:
            target_id = target
        
        if target_id == Owner:
            await update.message.reply_text("*Cannot deauthorize the owner.*", parse_mode='Markdown')
            return
        
        if target_id not in AUTHORIZED_USERS:
            await update.message.reply_text("*User is not authorized.*", parse_mode='Markdown')
            return
        
        AUTHORIZED_USERS.remove(target_id)
        save_authorized_users(AUTHORIZED_USERS)
        
        await update.message.reply_text(f"*User {target} has been deauthorized.*", parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text("*Failed to deauthorize user.*", parse_mode='Markdown')

async def user_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id != Owner:
        await update.message.reply_text("*Only owner can use this command.*", parse_mode='Markdown')
        return
    
    if not AUTHORIZED_USERS:
        await update.message.reply_text("*No authorized users.*", parse_mode='Markdown')
        return
    
    user_list = "*Authorized Users:*\n\n"
    for idx, uid in enumerate(AUTHORIZED_USERS, 1):
        is_owner = uid == Owner
        status = "Owner" if is_owner else "User"
        user_list += f"{idx}. {uid} - {status}\n"
    
    await update.message.reply_text(user_list, parse_mode='Markdown')

async def spam_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("""*Sharam Kar Gay Bola Hu Tab Bhi Commands Bhej Ke Apni Gawari Dikha Raha*

*Contact Owner To Get Access*

*Dubara Command Kiya To Tu Gay+Ramdi*

*Owner : @sourav0009*""", parse_mode='Markdown')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("*Usage: /spam {email}*", parse_mode='Markdown')
        return
    
    email = context.args[0]
    
    if '@' not in email or '.' not in email.split('@')[-1]:
        await update.message.reply_text("*Invalid email format.*", parse_mode='Markdown')
        return
    
    try:
        response = requests.get(
            f"{Api}/blacklist",
            params={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            
            if status == 'already_running':
                await update.message.reply_text(f"*Blacklist Already Running On {email}*", parse_mode='Markdown')
            elif status == 'started':
                await update.message.reply_text(f"*Blacklist Started\nEmail => {email}*", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"*Blacklist {status} on {email}*", parse_mode='Markdown')
        else:
            await update.message.reply_text("*Failed*", parse_mode='Markdown')
    except:
        await update.message.reply_text("*Error connecting to server.*", parse_mode='Markdown')

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("""*Sharam Kar Gay Bola Hu Tab Bhi Commands Bhej Ke Apni Gawari Dikha Raha*

*Contact Owner To Get Access*

*Dubara Command Kiya To Tu Gay+Ramdi*

*Owner : @sourav0009*""", parse_mode='Markdown')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("*Usage: /stop {email}*", parse_mode='Markdown')
        return
    
    email = context.args[0]
    
    try:
        response = requests.get(
            f"{Api}/stop",
            params={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            await update.message.reply_text(f"*Blacklist Stopped\nEmail => {email}*", parse_mode='Markdown')
        else:
            await update.message.reply_text("*Failed*", parse_mode='Markdown')
    except:
        await update.message.reply_text("*Api Off Or Unreachable*", parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("""*Sharam Kar Gay Bola Hu Tab Bhi Commands Bhej Ke Apni Gawari Dikha Raha*

*Contact Owner To Get Access*

*Dubara Command Kiya To Tu Gay+Ramdi*

*Owner : @sourav0009*""", parse_mode='Markdown')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("*Usage: /status {email}*", parse_mode='Markdown')
        return
    
    email = context.args[0]
    
    try:
        response = requests.get(
            f"{Api}/status",
            params={"email": email},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            stats = data.get('stats', {})
            
            pp_stats = stats.get('pp', {})
            pp_success = pp_stats.get('success', 0)
            pp_fail = pp_stats.get('fail', 0)
            pp_error = pp_stats.get('error', 0)
            
            ss_stats = stats.get('ss', {})
            ss_success = ss_stats.get('success', 0)
            ss_fail = ss_stats.get('fail', 0)
            ss_error = ss_stats.get('error', 0)
            
            ap_stats = stats.get('ap', {})
            ap_success = ap_stats.get('success', 0)
            ap_fail = ap_stats.get('fail', 0)
            ap_error = ap_stats.get('error', 0)
            
            message = f"""*Email : {email}*

*Sso =>* Success: {pp_success} | Failed: {pp_fail} | Err: {pp_error}

*Verify =>* Success: {ss_success} | Failed: {ss_fail} | Err: {ss_error}

*INGame =>* Success: {ap_success} | Failed: {ap_fail} | Err: {ap_error}"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("*Failed to get status.*", parse_mode='Markdown')
    except:
        await update.message.reply_text("*Error connecting to server.*", parse_mode='Markdown')

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("""*Sharam Kar Gay Bola Hu Tab Bhi Commands Bhej Ke Apni Gawari Dikha Raha*

*Contact Owner To Get Access*

*Dubara Command Kiya To Tu Gay+Ramdi*

*Owner : @sourav0009*""", parse_mode='Markdown')
        return
    
    try:
        response = requests.get(
            f"{Api}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            active_attacks = data.get('active_attacks', 0)
            status = data.get('status', 'unknown')
            tor_status = data.get('tor_status', 'unknown')
            
            message = f"""*Active Blacklists : {active_attacks}*
*Status: {status}*
*Tor Status: {tor_status}*"""
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text("*Failed to get list.*", parse_mode='Markdown')
    except:
        await update.message.reply_text("*Error connecting to server.*", parse_mode='Markdown')

async def handle_unauthorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("""*Sharam Kar Gay Bola Hu Tab Bhi Commands Bhej Ke Apni Gawari Dikha Raha*

*Contact Owner To Get Access*

*Dubara Command Kiya To Tu Gay+Ramdi*

*Owner : @sourav0009*""", parse_mode='Markdown')

def main() -> None:
    application = Application.builder().token(Tok).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("a", authorize_command))
    application.add_handler(CommandHandler("da", deauthorize_command))
    application.add_handler(CommandHandler("ul", user_list_command))
    application.add_handler(CommandHandler("spam", spam_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("list", list_command))
    
    application.add_handler(MessageHandler(filters.COMMAND, handle_unauthorized))

    print("=> Running")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()