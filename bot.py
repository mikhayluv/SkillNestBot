import telebot
import config
import database

bot = telebot.TeleBot(config.TOKEN)

conn = database.create_connection('skillnestbot.db')
database.create_table(conn)
# database.drop_table(conn, 'messages_log')


@bot.message_handler(commands=['start'])
def intro_messages(message):
    bot.send_message(message.from_user.id,
                     'Привет, дружище! Я Skill Nest Bot - твой помощник в поиске актуальных требований на рынке труда.')
    bot.send_message(message.from_user.id,
                     'Выбери команду "Вакансия"!')

@bot.message_handler(commands=['help'])
def intro_messages(message):
    bot.send_message(message.from_user.id,
                     'Запутался в себе? Хочешь большие коэффициенты? Хочешь жить как Папито? ИДИ НАХУЙ!')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text
    database.add_message(conn, user_id, username, message_text)
    if message.text == 'Привет':
        bot.send_message(message.from_user.id, 'Привет, я Skill Nest бот!')
    elif message.text == '/help':
        bot.send_message(message.from_user.id, 'Напиши: "Привет"')
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


def main():
    bot.polling(none_stop=True, interval=0)

main()