import time
import telebot
from telebot import types
from telegram.constants import ParseMode
import config
import database
import hh_api
import stepik_api
import re

bot = telebot.TeleBot(config.TOKEN)

conn = database.create_connection('skillnestbot.db')

# database.drop_table(conn, 'messages_log')
# database.drop_table(conn, 'vacancy_data')

database.create_messages_log_table(conn)
database.create_vacancy_data_table(conn)


user_states = {}
pmode= "MarkdownV2"


def log_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text
    database.add_message_to_log_table(conn, user_id, username, message_text)

@bot.message_handler(commands=['start'])
def start_messages(message):
    log_message(message)
    text_hello = 'Привет\!\nЯ *Skill* *Nest* *Bot* \- твой проводник в мир актуальных требований рынка труда\.\n\nВ меню тебя ждут две кнопки\: *Навыки* и *Курсы*\n\n• *Навыки* — узнай, какие требования нужны для вакансии твоей мечты\!\n• *Курсы* — подбери лучший онлайн\-курс на *Stepik* для прокачки своих скиллов\!'
    bot.send_message(message.from_user.id, text_hello, parse_mode=pmode, reply_markup=two_buttons())


@bot.message_handler(commands=['help'])
def help_messages(message):
    log_message(message)
    text_help = 'Выбери одну из двух кнопок в меню!'
    bot.send_message(message.from_user.id, text_help)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    log_message(message)
    if message.from_user.id in user_states:
        state = user_states[message.from_user.id]
        if state == 'waiting_for_vacancy_name' and message.text != 'Навыки' and message.text != 'Курсы':
            user_states[message.from_user.id] = 'work'
            text_search = message.text
            bold_text_search = escape_special_characters(text_search)
            text_search = text_search.lower()
            bot.send_message(message.from_user.id, f'Начинаю поиск по запросу\: *{bold_text_search}*', parse_mode=pmode)

            try:
                check = hh_api.check_vacancy_search(conn,text_search)

                if isinstance(check, tuple):
                    list_id, found = check
                    if not found:
                        user_states[message.from_user.id] = 'waiting_for_vacancy_name'
                        unlucky_text = f'По вашему запросу *{bold_text_search}* не было найдено вакансий\.\nПроверьте введенные данные\!'
                        bot.send_message(message.from_user.id, unlucky_text, parse_mode=pmode)
                        return

                    text_found = f'По вашему запросу *{bold_text_search}* найдено *вакансий*\: *{found}*\!'
                    bot.send_message(message.from_user.id, text_found, parse_mode=pmode)
                    time.sleep(3)
                    text_get_vac = 'Получаю самые актуальные вакансии с онлайн\-биржи *HeadHunter*\.\.\.'
                    bot.send_message(message.from_user.id, text_get_vac, parse_mode=pmode)
                    hh_api.get_and_store_vacancy(list_id, text_search)
                    text_get_skills_data = 'Получаю требования из описаний полученных вакансий\.\.\.'
                    bot.send_message(message.from_user.id, text_get_skills_data, parse_mode=pmode)
                    skills = database.get_skills(conn, text_search)
                    print(f'skills {skills}')
                else:
                    skills = check
                skills = ', '.join([str(sk[0]) for sk in skills])
                skills = hh_api.swap_skills(skills)
                skills_top, list_of_skills = hh_api.sort_and_count_key_skill(skills)
                skills_top = escape_special_characters(skills_top)
                time.sleep(3)
                keyboard_skills = make_keyboard(list_of_skills)
                text_result = f'Вот *ТОП*\-*10* навыков для *{bold_text_search}*\:\n\n{skills_top}\n\nЕсли не знаешь какой\-то навык, выбери его из списка ниже\!'
                bot.send_message(message.from_user.id, text_result, parse_mode=pmode, reply_markup=keyboard_skills)
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошли технические шоколадки: {e}')
            return

        if state == 'waiting_for_сourse_name' and message.text != 'Навыки' and message.text != 'Курсы':
            try:
                user_states[message.from_user.id] = 'work'
                text_search = message.text
                bot.send_message(message.from_user.id, f'Начинаю поиск курсов по навыку: *{text_search}*', parse_mode=pmode)
                list_of_skills = stepik_api.get_courses(conn, text_search)
                if not list_of_skills:
                    user_states[message.from_user.id] = 'waiting_for_сourse_name'
                mes = message_with_courses(list_of_skills, text_search)
                bot.send_message(message.from_user.id, mes, parse_mode=pmode)
                user_states[message.from_user.id] = 'waiting_for_сourse_name'
            except Exception as e:
                bot.send_message(message.from_user.id, f'Произошли технические шоколадки: {e}')
            return

    if message.text.lower() == 'привет':
        text_privet = 'Привет\! Выбери, *Навыки* или *Курсы*\.'
        bot.send_message(message.from_user.id, text_privet, parse_mode=pmode)
        return
    elif message.text.lower() == 'навыки':
        text_navik = 'Напиши мне *название* *вакансии*, и я подскажу требования для неё\.'
        user_states[message.from_user.id] = 'waiting_for_vacancy_name'
        bot.send_message(message.from_user.id, text_navik, parse_mode=pmode)
        return
    elif message.text.lower() == 'курсы':
        text_course = 'Напиши мне *навык*, и я поищу курсы на *Stepik* для его изучения\.'
        user_states[message.from_user.id] = 'waiting_for_сourse_name'
        bot.send_message(message.from_user.id, text_course, parse_mode=pmode)
        return
    else:
        return bot.send_message(message.from_user.id, "Я тебя не понимаю... Напиши /help.")

@bot.callback_query_handler(func=lambda callback: True)
def course_from_stepik(callback):
    skill = callback.data
    print(skill)
    list_of_courses = stepik_api.get_courses(conn, skill)
    print(list_of_courses)
    mess = message_with_courses(list_of_courses, skill)

    return bot.send_message(callback.message.chat.id, mess, parse_mode=pmode)


def escape_special_characters(text):
    special_characters = r'_*[]()~`>#\+\-=|{}.!\]'
    escaped_text = re.sub(r'([' + re.escape(special_characters) + r'])', r'\\\1', text)

    return escaped_text


def message_with_courses(list_of_courses, text):
    mess = f"Вот подборка курсов по навыку *{text}*\:\n\n"
    if not list_of_courses:
        text = escape_special_characters(text)
        mess = f'По навыку *{text}* не было найдено хороших курсов\.'
    for course in list_of_courses:
        name = course[2]
        name = escape_special_characters(name)
        url = course[3]
        mess += f"\- [{name}]({url})\n"

    return mess


def two_buttons():
    buttons = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Навыки")
    btn2 = types.KeyboardButton("Курсы")
    buttons.add(btn1, btn2)

    return buttons

def make_keyboard(skills_list_top):
    keyboard = types.InlineKeyboardMarkup()
    for skill, count in skills_list_top:
        button = types.InlineKeyboardButton(text=skill, callback_data=f'{skill}')
        keyboard.add(button)

    return keyboard


def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
