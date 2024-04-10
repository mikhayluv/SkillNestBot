import telebot
import config
import database

bot = telebot.TeleBot(config.TOKEN)

conn = database.create_connection('skillnestbot.db')
database.create_messages_log_table(conn)

# database.drop_table(conn, 'messages_log')

def log_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text
    database.add_message_to_log_table(conn, user_id, username, message_text)

@bot.message_handler(commands=['start'])
def start_messages(message):
    log_message(message)
    bot.send_message(message.from_user.id,
                     'Привет, дружище! Я Skill Nest Bot - твой помощник в поиске актуальных требований на рынке труда.')
    bot.send_message(message.from_user.id,
                     'Выбери команду "Вакансия"!')

@bot.message_handler(commands=['help'])
def help_messages(message):
    log_message(message)
    bot.send_message(message.from_user.id,
                     'Запутался в себе? Хочешь большие коэффициенты? Хочешь жить как Папито? ИДИ НАХУЙ!')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    log_message(message)
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Привет, я Skill Nest бот!')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Напиши: "Привет"')
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю, дружище. Напиши /help.")


def main():
    bot.polling(none_stop=True, interval=0)

main()