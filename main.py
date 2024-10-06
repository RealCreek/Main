import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# Bot token and admin chat ID
bot_token = "7667227723:AAGbD16_s_juygylHJCG7QARiYtut8gINyE"
admin_chat_id = 6436299355  # Admin's chat ID
channel_username = "@cautionseals"  # Channel where approved reports will be posted

bot = telebot.TeleBot(bot_token)

# Dictionary to store user report data temporarily
user_data = {}


# Start command handler
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('/report', '/appeal')
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)


# Appeal command handler
@bot.message_handler(commands=['appeal'])
def appeal(message):
    bot.send_message(message.chat.id, "Coming soon!")


# Report command handler
@bot.message_handler(commands=['report'])
def report(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Please provide the scammer's username (with @):")
    bot.register_next_step_handler(message, process_username_step)


def process_username_step(message):
    chat_id = message.chat.id
    username = message.text
    if not username.startswith('@'):
        bot.send_message(chat_id, "Username must start with @. Please try again.")
        bot.register_next_step_handler(message, process_username_step)
        return
    user_data[chat_id] = {'scammer_username': username}
    bot.send_message(chat_id, "Tell the Amount Scammed in $ (Number only, no symbols):")
    bot.register_next_step_handler(message, process_amount_step)


def process_amount_step(message):
    chat_id = message.chat.id
    try:
        amount = float(message.text)  # Ensure the input is a valid number
        user_data[chat_id]['scammed_amount'] = amount
        bot.send_message(chat_id, "Please write an explanation about the scam:")
        bot.register_next_step_handler(message, process_explanation_step)
    except ValueError:
        bot.send_message(chat_id, "Invalid input. Please enter a numeric value:")
        bot.register_next_step_handler(message, process_amount_step)


def process_explanation_step(message):
    chat_id = message.chat.id
    explanation = message.text
    user_data[chat_id]['explanation'] = explanation
    bot.send_message(chat_id, "Make a channel/group, post proofs there, and send the link here:")
    bot.register_next_step_handler(message, process_proof_link_step)


def process_proof_link_step(message):
    chat_id = message.chat.id
    proof_link = message.text
    user_data[chat_id]['proof_link'] = proof_link

    # Send message to admin with options to approve or decline
    scammer_username = user_data[chat_id]['scammer_username']
    scammed_amount = user_data[chat_id]['scammed_amount']
    explanation = user_data[chat_id]['explanation']
    proof_link = user_data[chat_id]['proof_link']

    admin_message = (
        f"Scammer Username: {scammer_username}\n"
        f"Scammed Amount: ${scammed_amount}\n"
        f"Explanation: {explanation}\n"
        f"Proofs: {proof_link}"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Approve', callback_data=f"approve_{chat_id}"),
               InlineKeyboardButton('Decline', callback_data=f"decline_{chat_id}"))

    bot.send_message(admin_chat_id, admin_message, reply_markup=markup)
    bot.send_message(chat_id, "Your report has been submitted to the admin for review.")


# Handle approval or decline by admin
@bot.callback_query_handler(func=lambda call: call.data.startswith('approve_') or call.data.startswith('decline_'))
def handle_admin_response(call):
    chat_id = int(call.data.split('_')[1])  # Extract the user chat_id from callback data
    if call.data.startswith('approve_'):
        bot.send_message(chat_id, "Your report was approved. Thanks for reporting the scammer!")
        scammer_username = user_data[chat_id]['scammer_username']
        scammed_amount = user_data[chat_id]['scammed_amount']
        explanation = user_data[chat_id]['explanation']
        proof_link = user_data[chat_id]['proof_link']

        # Send message to the specified channel
        channel_message = (
            f"Scammer Username: {scammer_username}\n"
            f"Scammed Amount: ${scammed_amount}\n"
            f"Explanation: {explanation}\n"
            f"Proofs: {proof_link}"
        )
        bot.send_message(channel_username, channel_message)
    elif call.data.startswith('decline_'):
        bot.send_message(chat_id, "Sorry, your request was declined.")

    # Delete admin's message
    bot.delete_message(call.message.chat.id, call.message.message_id)


# Start the bot polling to handle incoming updates
bot.polling(none_stop=True)
