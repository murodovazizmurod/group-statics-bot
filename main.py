import sql
import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('1254019746:AAEkn4uAfTpONZhr9RA94eNuNFy0dI4-A9o')
db = sql.Sql('data.db')
con = sqlite3.connect("data.db", check_same_thread=False)
cur = con.cursor()


@bot.message_handler(commands=['start'])
def add_group_to_db(message):
    if message.chat.type == "supergroup" or message.chat.type == "group":
        if bot.get_chat_member(message.chat.id, message.from_user.id).status == "administrator" or bot.get_chat_member(
                message.chat.id, message.from_user.id).status == "creator":
            if db.create(message.chat.id, message.chat.title):
                bot.send_message(message.chat.id,
                                 "Tabriklaymiz! Sizning guruhingiz muvofaqiyatli ma`lumotlar bazasiga qo'shildi")
            else:
                bot.send_message(message.chat.id, "Ushbu guruh ma`lumotlar bazasida mavjud!")
        else:
            if not db.iswarned(message.chat.id, message.from_user.id):
                bot.send_message(message.chat.id, "Kechirasiz, siz botdan foydalana olmaysiz!")
                db.give_warn(message.chat.id, message.from_user.id)
            else:
                db.give_warn(message.chat.id, message.from_user.id)
                user_info = db.get_user(message.chat.id, message.from_user.id)
                if user_info[0][6] >= 5:
                    bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=3600)
                else:
                    bot.send_message(message.chat.id,
                                     f"{user_info[0][2]} siz ogolantirildingiz! ({user_info[0][6]}/5)\n\t5-ogohlantirishdan so'ng siz guruhdan vaqtincha chetlatilasiz! (BAN)")
    elif message.chat.type == "private":
        bot.send_message(message.chat.id,
                         text="Bot yordamida guruh statistikasini yig'ishni boshlsh uchun botni o'z guruhingizga qo'shing",
                         parse_mode="html")


# /stat buyrug'i berilganda
@bot.message_handler(commands=['stat'])
def stat(message):
    if message.chat.type == "supergroup" or message.chat.type == "group":
        if bot.get_chat_member(message.chat.id, message.from_user.id).status == "administrator" or bot.get_chat_member(
                message.chat.id, message.from_user.id).status == "creator":
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn1 = types.InlineKeyboardButton("Top Users", callback_data='top')
            btn2 = types.InlineKeyboardButton("Developer", callback_data='dev')

            markup.add(btn1, btn2)

            bot.send_message(message.chat.id, f"There are {message.message_id} messages in group.", reply_markup=markup)
        else:
            if not db.iswarned(message.chat.id, message.from_user.id):
                bot.send_message(message.chat.id, "Kechirasiz, siz botdan foydalana olmaysiz!")
                db.give_warn(message.chat.id, message.from_user.id)
            else:
                db.give_warn(message.chat.id, message.from_user.id)
                user_info = db.get_user(message.chat.id, message.from_user.id)
                if user_info[0][6] >= 5:
                    bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=3600)
                else:
                    bot.send_message(message.chat.id,
                                     f"{user_info[0][2]} siz ogolantirildingiz! ({user_info[0][6]}/5)\n\t5-ogohlantirishdan so'ng siz guruhdan vaqtincha chetlatilasiz! (BAN)")

    elif message.chat.type == "private":
        bot.send_message(message.chat.id,
                         text=db.private_is_admin(message.from_user.id, message.from_user.first_name, text="/stat"),
                         parse_mode="html")


# Faqatgina adminlar uchun
# @bot.message_handler(commands=['dev'])
# def dont_enter(message):
#     if message.chat.type == "supergroup" or message.chat.type == "group":
#         if bot.get_chat_member(message.chat.id, message.from_user.id).status == "administrtor" or bot.get_chat_member(
#                 message.chat.id, message.from_user.id).status == "creator":
#             count = len(db.get_all_user(message.chat.id))
#             if count > 5:
#                 markup = types.InlineKeyboardMarkup(row_width=3)
#                 prev = types.InlineKeyboardButton("<< Oldingi")
#                 next = types.InlineKeyboardButton("Keyingi >>")
#                 markup.add(prev, next)
#                 text = db.users_list(message.chat.id, 5)
#                 bot.send_message(message.chat.id, text, reply_markup=markup)
#             else:
#                 text = db.users_list(message.chat.id, 5)
#                 bot.send_message(message.chat.id, text, reply_markup=None)
#     elif message.chat.type == "private":
#         bot.send_message(message.chat.id, "Developer of this bot is: Murodov Azizmurod (@murodov_azizmurod)")


# Istalgan matn yuborilganda
@bot.message_handler(content_types=['text'])
def reg_user(message):
    # Agarda chat turi guruh bo'lsa
    if message.chat.type == "supergroup" or message.chat.type == "group":
        if not db.check_user(message.chat.id, message.from_user.id):  # userni bazadan tekshiramiz, topilmasa qo'shamiz
            user = (
                message.from_user.id,
                message.from_user.first_name,
                message.from_user.last_name,
                bot.get_chat_member(message.chat.id, message.from_user.id).status
            )
            db.add_user(message.chat.id, user)
            db.give_message(message.chat.id, message.from_user.id, message.message_id)
        else:
            db.give_message(message.chat.id, message.from_user.id, message.message_id)
            user_info = db.user(message.chat.id, message.from_user.id)
            if user_info["warnings"] >= 5:
                bot.kick_chat_member(message.chat.id, message.from_user.id, until_date=3600)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    text = db.top_users(call.message.chat.id)
    if call.data == "top":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=None)
    elif call.data == "dev":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Developer and Full Stack Coder: @murodov_azizmurod', reply_markup=None)


@bot.message_handler(content_types=['new_chat_members'])
def message_new_member(message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(content_types=['left_chat_member'])
def message_left_member(message):
    bot.delete_message(message.chat.id, message.message_id)


if __name__ == "__main__":
    bot.polling(none_stop=True)
