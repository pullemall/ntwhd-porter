import threading
import time

import telebot
from peewee import DoesNotExist
from telebot.apihelper import ApiException

from config import config, get_text, text_edit
from models import Message, User, db

db.create_tables([User, Message])

UNSAFE_MESSAGES = dict()
ADMINS = list()
MESSAGES = dict()

# define bot
bot = telebot.TeleBot(config["token"].get())


def kick_user(message, msg_from_bot):
    """
        executes in separate thread;
        kicks user and removes its messages after timeout if it didn't pass the exam
    """
    time.sleep(config["captcha"]["timeout"].get())
    if message.from_user.id in UNSAFE_MESSAGES:

        bot.kick_chat_member(message.chat.id, message.from_user.id)
        # bot.unban_chat_member(message.chat.id, message.from_user.id)

        for msg_id in UNSAFE_MESSAGES[message.from_user.id]:
            bot.delete_message(chat_id=message.chat.id, message_id=msg_id)

        bot.delete_message(message.chat.id, msg_from_bot)
        del UNSAFE_MESSAGES[message.from_user.id]


def check_access(bot_function):

    def a_wrapper_accepting_arguments(message):
        if message.from_user.id in ADMINS:
            bot_function(message)

    return a_wrapper_accepting_arguments


@bot.message_handler(commands=["edit_hello_message"])
@check_access
def edit_hello_message(message):
    try:
        msg = message.text.replace("/edit_hello_message ", "")
        text_edit(msg)
        bot.send_message(message.from_user.id, "Edited")
    except ApiException:
        print("bot can\'t initiate conversation with a user")


@bot.message_handler(commands=["test_access"])
@check_access
def test_access(message):
    try:
        print(ADMINS)
        print("User id: {}".format(message.from_user.id))
        print(message.from_user.id in ADMINS)
        bot.reply_to(message, "Access TEST")
    except ApiException:
        print("bot can\'t initiate conversation with a user")


@bot.message_handler(commands=["test"])
@check_access
def test_hello_message(message):
    try:
        bot.send_message(message.from_user.id, get_text(), parse_mode="html")
    except ApiException:
        print("bot can\'t initiate conversation with a user")


@bot.message_handler(func=lambda m: True, content_types=["new_chat_members"])
def new_user(message):
    """
        sends notification message to each joined user and triggers `kick_user`
    """

    def _gen_captcha_text(user):
        _captcha_text = (
            "[{0}](tg://user?id={1}), Пожалуйста, введите код с картинки в течении "
            "({2} sec)"
        )
        return _captcha_text.format(
            user.first_name, user.id, config["captcha"]["timeout"].get()
        )

    try:
        user = User.select().where(User.uid == message.from_user.id).get()
    except DoesNotExist:
        if message.from_user.id not in UNSAFE_MESSAGES:
            UNSAFE_MESSAGES[message.from_user.id] = [message.message_id]
            photo = open("download.jpg", "rb")
            msg_from_bot = bot.send_photo(
                message.chat.id,
                photo=photo,
                caption=_gen_captcha_text(message.from_user),
                parse_mode="Markdown",
            )
            MESSAGES[message.from_user.id] = msg_from_bot.message_id
            thread = threading.Thread(
                target=kick_user, args=(message, msg_from_bot.message_id,)
            )
            thread.start()


@bot.message_handler(
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "audio",
        "animation",
        "voice",
        "sticker",
        "bot_command",
    ]
)
def get_user_messages(message):
    """
        processes all new messages;
        removes those which exceed predefined LIMIT
    """
    if message.from_user.id in UNSAFE_MESSAGES:
        if (
                len(UNSAFE_MESSAGES[message.from_user.id])
                >= config["captcha"]["msg_limit"].get()
        ):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        else:
            UNSAFE_MESSAGES[message.from_user.id].append(message.message_id)
    else:
        Message.from_message(message)
    if message.text == "netw95hood":
        print(MESSAGES.get(message.from_user.id))
        bot.delete_message(message.chat.id, MESSAGES.get(message.from_user.id))
        del UNSAFE_MESSAGES[message.from_user.id]
        
        User.from_message(message)
        bot.reply_to(message, get_text(), parse_mode="html")


if __name__ == "__main__":
    for admin in bot.get_chat_administrators(config["chat"].get()):
        ADMINS.append(admin.user.id)
    try:
        while True:
            try:
                bot.polling(none_stop=True, timeout=60)
            except Exception as e:
                bot.stop_polling()
                time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        raise
