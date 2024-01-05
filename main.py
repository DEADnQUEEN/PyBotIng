from sub_functions import Root

try:
    import telebot
except ImportError as e:
    import os
    os.system('pip install telebot')
    import telebot

token = '6925632277:AAE38j8q-lwpkUU_-3UofXlvj1GteC0h5Tk'
bot = telebot.TeleBot(token)
root: Root


@bot.callback_query_handler(func=lambda call: root.checker(call))
def parser(call: telebot.types.CallbackQuery):
    pass


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    if not root.is_user_exist(message.from_user):
        root.add_user(message.from_user)

    with open('intro.txt', 'r', encoding='utf8') as file:
        text = file.readlines()

    bot_text = str.join('\n', text)

    keys = list(root.buttons.keys())
    reply = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(keys)):
        bot_text += f'{i + 1}) {keys[i]}\n'
        reply.add(telebot.types.KeyboardButton(keys[i]))

    bot.send_message(
        message.chat.id,
        bot_text,
        reply_markup=reply
    )

    root.last_message[message.from_user.id] = message.text


@bot.message_handler(commands=['root'])
def start(message: telebot.types.Message):
    root.root_commands(message)


@bot.message_handler(content_types=['text'])
def texter(message: telebot.types.Message):
    text = 'Извините, но я вас не понимаю\n' \
           'Возможно вы вводили вопрос ручками, попробуйте воспользоваться кнопками из функции\n' \
           '/start'

    r = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    r.add(telebot.types.KeyboardButton("/start"))

    if message.text in list(root.buttons.keys()):
        text = root.buttons[message.text] + f'\n'
    elif root.last_message[message.from_user.id] in root.echo:
        with open("echo_answer.txt", 'r', encoding='utf8') as e:
            lines = e.readlines()
            text = str.join('\n', lines)
        root.send_echo(message)

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=r
    )

    root.last_message[message.from_user.id] = message.text


if __name__ == '__main__':
    root = Root(bot)
    bot.polling(none_stop=True, timeout=200)
