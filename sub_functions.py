import os
import random
import string
import telebot
from telebot import types
import json


class Root:
    @staticmethod
    def __key_gen(length: int):
        key = ''
        for i in range(length):
            key += random.choice(string.ascii_letters)

        return key

    def __is_root(self, from_user: types.User):
        for i in range(len(self.__root_users)):
            if from_user.id == self.__root_users[i].id:
                return True

        return False

    def root_commands(self, message: types.Message):
        root = message.text.split(' ', maxsplit=2)

        if self.__is_root(message.from_user):
            if root[1] not in list(self.__commands.keys()):
                self.__bot.send_message(
                    message.chat.id,
                    "Unsolved root reference"
                )
            else:
                self.__commands[root[1]][0](message)
        elif root[1] == 'add' and root[2] == self.__key_log:
            self.__add_root(message)

    def __add_root(self, message: types.Message):
        if message.text.split(' ', 2)[2] == self.__key_log:
            if self.__is_root(message.from_user):
                self.__bot.send_message(
                    message.chat.id,
                    f'{message.from_user.full_name}, you are already have a root access'
                )
                return
            else:
                self.__root_users.append(message.from_user)

                self.__make_json_user('json/root', message.from_user)

                for i in range(len(self.__root_users)):
                    self.__bot.send_message(
                        self.__root_users[i].id,
                        f'Added a new root user!\n{message.from_user.full_name}, @{message.from_user.username}'
                    )

    def add_user(self, user: types.User):
        self.__users.append(user)
        self.__make_json_user('json/users', user)

    def __send(self, message: types.Message):
        """
        /root send id text
        send - command name
        id - personal id of user ('s but separator is ',', not a ' '),
             or it could be @, which means all (except root users)
        text - text, which must be in ""

        :return: send text for user by id
        """
        command = message.text.split(' ', maxsplit=3)

        if len(command) != 4:
            return

        for i in range(len(self.__users)):
            if command[2] == '"@"' or (command[2].isdigit() and int(command[2]) == self.__users[i].id):
                self.__bot.send_message(
                    self.__users[i].id,
                    command[3][1: len(command[3]) - 1]
                )

    def __stop(self, message: types.Message):
        command = message.text.split(' ')
        if len(command) == 2:
            self.__bot.send_message(
                message.chat.id,
                "Bot is offline"
            )
            self.__bot.stop_bot()

    def __help(self, message: types.Message):
        command = message.text.split(' ')
        text = ''
        if len(command) == 2:
            for prompt in list(self.__commands.keys()):
                text += f'{self.__commands[prompt][1]}\n'
        elif len(command) == 3:
            if command[2][1:len(command[2]) - 1] in list(self.__commands.keys()):
                text = self.__commands[command[2][1:len(command[2]) - 1]][1] + "\n" + \
                       self.__commands[command[2][1:len(command[2]) - 1]][2] + "\n"

        else:
            return

        self.__bot.send_message(
            message.chat.id,
            f'{text}\nMore information by /root help "command_name"'
        )

    def __echo(self, message: types.Message):
        command = message.text.split(' ', maxsplit=2)
        if command[2].__len__() < 2:
            return

        echo = command[2][1:len(command[2]) - 1]
        if echo in self.echo:
            text = "This text already with echo"
        else:
            text = f'Echo markup added to "{echo}"'
            self.echo.append(echo)

        self.__bot.send_message(
            message.chat.id,
            f'{text}'
        )

    def send_echo(self, message: types.Message):
        for i in range(len(self.__root_users)):
            self.__bot.send_message(
                self.__root_users[i].id,
                f'Full name: {message.from_user.full_name}\n'
                f"Username: @{message.from_user.username}\n"
                f'ID: {message.from_user.id}\n'
                f'Message Text:\n"{message.text}"'
            )

    def __add_button(self, message: types.Message):
        text = message.text.split(' ', maxsplit=2)
        words = text[len(text) - 1].split('"')
        if len(words) == 5:
            if words[1] in list(self.buttons.keys()):
                t = "Данный вопрос уже прописан"
            else:
                t = 'Текст на кнопке: ' + words[1] + '\nОтветный текст по кнопке: ' + words[3]
                self.buttons[words[1]] = words[3]
            self.__bot.send_message(
                message.chat.id,
                t
            )

    def __send_root_key(self, message: types.Message):
        self.__bot.send_message(
            message.chat.id,
            f'auth root key - {self.__key_log}\nDo not tell this for everyone'
        )

    def is_user_exist(self, user: types.User):
        for i in range(len(self.__users)):
            if user.id == self.__users[i].id:
                return True

        return False

    @staticmethod
    def __load_users_json(path: str):
        out_list: list[types.User] = []

        if not os.path.exists(path):
            os.mkdir(path=path)
            
        for file_name in os.listdir(path):
            jpath = os.path.join(path, file_name)
            if os.path.isfile(jpath) and file_name[len(file_name) - 5:len(file_name)] == '.json':
                with open(jpath, 'r') as j:
                    out_list.append(types.User.de_json(json.load(j)))

        return out_list

    @staticmethod
    def __make_json_user(path: str, user: types.User):
        with open(f'{path}/{user.username}.json', 'w') as j:
            json.dump(user.to_json(), j)

    last_message: dict[int, str] = {}

    __commands: dict[str: tuple] = {
        'add': (
            __add_root,
            '/root add "safe_key"',
            '/root add "safe_key"\n'
            'Command to add a new user with root permissions\n'
            'Safe key is autogenerated by code after init'
        ),
        'send': (
            __send,
            '/root send "user" "message"',
            '/root send "user id / @ - all" "what to send"\n'
            'to send info for 2 or more users write "id_first,id_second"\n'
            'use a "," as a separator, not a ", "'),
        'add_button': (
            __add_button,
            '/root add_button "button" "answer"',
            '/root add_button "button text" "answer for button click"\n'
        ),
        'send_root_key': (
            __send_root_key,
            "/root send_root_key",
            '/root send_root_key - send key to root auth'
        ),
        "echo": (
            __echo,
            '/root echo "message"',
            '/root echo "last_user_message"\n'
            'Next message will be echo to all root users'
        ),
        'stop_bot': (
            __stop,
            "/root stop_bot",
            '/root stop_bot - stop bot polling'
        ),
        'help': (
            __help,
            "/root help",
            '/root help - see all root commands\n'
            '/root help "command" - send extension info for command'
        ),
    }

    buttons: dict[str: str] = {}
    echo: list[str] = []

    def __init__(self, bot: telebot.TeleBot):
        self.__key_log = self.__key_gen(10)
        self.__bot = bot

        self.__root_users: list[types.User] = self.__load_users_json('json/root')
        self.__users: list[types.User] = self.__load_users_json('json/users')

        for i in range(len(self.__users)):
            self.last_message[self.__users[i].id] = ""

        for i in range(len(self.__root_users)):
            self.last_message[self.__root_users[i].id] = ""
            self.__bot.send_message(
                self.__root_users[i].id,
                'bot is online',
                reply_markup=types.ReplyKeyboardRemove()
            )
