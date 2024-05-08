import telebot
from telebot import types
import config
import database
import hh_api
import re

bot = telebot.TeleBot(config.TOKEN)

conn = database.create_connection('skillnestbot.db')

# database.drop_table(conn, 'messages_log')
database.drop_table(conn, 'vacancy_data')

database.create_messages_log_table(conn)
database.create_vacancy_data_table(conn)


user_states = {}



def log_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text
    database.add_message_to_log_table(conn, user_id, username, message_text)

@bot.message_handler(commands=['start'])
def start_messages(message):
    log_message(message)
    bot.send_message(message.from_user.id,
                     'Привет! Я Skill Nest Bot - твой помощник в поиске актуальных требований на рынке труда.')
    bot.send_message(message.from_user.id,
                     'Напиши "Вакансия"!')

@bot.message_handler(commands=['help'])
def help_messages(message):
    log_message(message)
    bot.send_message(message.from_user.id,
                     'Напиши "Вакансия"!')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    log_message(message)
    if message.from_user.id in user_states:
        state = user_states[message.from_user.id]
        if state == 'waiting_for_vacancy_name':
            user_states[message.from_user.id] = 'idle'
            text_search = message.text
            bot.send_message(message.from_user.id, f'Начинаю поиск по запросу: "{text_search}"')

            list_id, found = hh_api.get_list_id_vacancies(text_search)

            if not found:
                user_states[message.from_user.id] = 'waiting_for_vacancy_name'
                return bot.send_message(message.from_user.id, f'По вашему запросу "{text_search}" не было найдено вакансий :(\nПроверьте введенные данные!')

            bot.send_message(message.from_user.id, f'По вашему запросу "{text_search}" было найдено {found} вакансий!')

            # try:
            hh_api.get_and_store_vacancy(list_id, text_search)
            skills = database.get_skills(conn, text_search)
            skills = ', '.join([str(sk[0]) for sk in skills])
            skills = hh_api.swap_skills(skills)
            skills_top, list_of_skills = hh_api.sort_and_count_key_skill(skills)
            bot.send_message(message.from_user.id, f'Вот ТОП 10 навыков для "{text_search}":\n\n{skills_top}')
            keyboard = make_keyboard(list_of_skills)
            bot.send_message(message.from_user.id, 'Если хочешь подкачать навыки, выбери один из навыков:',
                             reply_markup=keyboard)
            # except Exception as e:
            # bot.send_message(message.from_user.id, f'Произошла ошибка: {e}')    #debug
            bot.send_message(message.from_user.id, f'Произошли технические шоколадки :(')

            return

    if message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, 'Привет, напиши "Вакансия"')
        return
    elif message.text.lower() == 'вакансия':
        user_states[message.from_user.id] = 'waiting_for_vacancy_name'
        return bot.send_message(message.from_user.id,
                                'Напиши название вакансии, которая тебя интересует, а я проанализирую свежие объявления и подскажу тебе навыки!')

    return bot.send_message(message.from_user.id, "Я тебя не понимаю... Напиши /help.")


def make_keyboard(skills_list_top):
    keyboard = types.InlineKeyboardMarkup()
    for skill, count in skills_list_top:
        button = types.InlineKeyboardButton(text=skill, callback_data=f'skill_{skill}')
        keyboard.add(button)

    return keyboard


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
