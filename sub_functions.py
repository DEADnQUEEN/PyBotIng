import os
import random
import string

import json

try:
    import telebot
except ImportError as e:
    os.system('pip install telebot')
    import telebot

from telebot import types


def path_exists(path: str) -> None:
    for sub_path in list(path.split('\\')):
        path_exists(sub_path)

    if not os.path.exists(path):
        print(f'dir "{path}" have been added')
        os.mkdir(path)


class Root:
    @staticmethod
    def __key_gen(length: int) -> str:
        key = ''
        for i in range(length):
            key += random.choice(string.ascii_letters)

        print('log key - "', key, '"', sep='')

        return key

    def __is_root(self, from_user: types.User) -> bool:
        for i in range(len(self.__root_users)):
            if from_user.id == self.__root_users[i].id:
                return True

        return False

    def root_commands(self, message: types.Message) -> None:
        root = message.text.split(' ', maxsplit=2)

        if len(root) < 2:
            return

        if self.__is_root(message.from_user):

            if root[1] not in list(self.__commands.keys()):
                self.__bot.send_message(
                    message.chat.id,
                    "Unsolved root reference"
                )
                return

            self.__commands[root[1]][0](self, message)

        elif root[1] == 'add':
            self.__add_root(message)

    def __add_root(self, message: types.Message) -> None:
        if message.text.split(' ', 2)[2] == f'"{self.__key_log}"':
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

    def add_user(self, user: types.User) -> None:
        self.__users.append(user)
        self.__make_json_user('json/users', user)

    def __send(self, message: types.Message) -> None:
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

    def __stop(self, message: types.Message) -> None:
        command = message.text.split(' ')
        if len(command) == 2:
            self.__bot.send_message(
                message.chat.id,
                "Bot is offline"
            )
            self.__bot.stop_bot()

    def __help(self, message: types.Message) -> None:
        command = message.text.split(' ')
        text = 'Command List:\n\n'
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
            f'{text}\n'
            f'More information by /root help "command_name"\n'
            f'Or you can also use /help\n'
            f'All command now support to use by command name without root prefix <3'
        )

    def __echo(self, message: types.Message) -> None:
        command = message.text.split(' ', maxsplit=2)
        if command[2].__len__() < 2:
            return

        echo = command[2][1:len(command[2]) - 1]
        if echo in self.echo:
            text = "This text already with echo"
        else:
            text = f'Echo markup added to "{echo}"'
            self.echo.append(echo)

            path_exists(self.__echo_location)

            with open(f'{self.__echo_location}\\{len(os.listdir(self.__echo_location))}.txt', 'w') as file:
                file.write(echo)

        self.__bot.send_message(
            message.chat.id,
            f'{text}'
        )

    def send_echo(self, message: types.Message) -> None:
        for i in range(len(self.__root_users)):
            self.__bot.send_message(
                self.__root_users[i].id,
                f'Full name: {message.from_user.full_name}\n'
                f"Username: @{message.from_user.username}\n"
                f'ID: {message.from_user.id}\n'
                f'Message Text:\n"{message.text}"'
            )

    def __add_button(self, message: types.Message) -> None:
        text = message.text.split(' ', maxsplit=2)

        if len(text) != 3:
            return

        words = text[len(text) - 1].split('"')
        if len(words) == 5:
            if words[1] in list(self.buttons.keys()):
                t = "Данный вопрос уже прописан"
            else:
                t = 'Текст на кнопке: ' + words[1] + '\nОтветный текст по кнопке: ' + words[3]
                self.buttons[words[1]] = words[3]
                self.__save_buttons(self.__buttons_location, words[1], words[3])

            self.__bot.send_message(
                message.chat.id,
                t
            )

    def __remove_button(self, message: types.Message) -> None:
        inline = types.InlineKeyboardMarkup()

        btn_list = list(self.buttons.keys())

        for i in range(len(btn_list)):
            inline.add(types.InlineKeyboardButton(text=btn_list[i], callback_data=f'btn{btn_list[i]}'))

        self.__bot.send_message(
            message.chat.id,
            "List of Buttons",
            reply_markup=inline
        )

    def __remove_echo(self, message: types.Message) -> None:
        inline = types.InlineKeyboardMarkup()

        for i in range(len(self.echo)):
            inline.add(types.InlineKeyboardButton(text=self.echo[i], callback_data=f'echo{self.echo[i]}'))

        self.__bot.send_message(
            message.chat.id,
            "List of Echo",
            reply_markup=inline
        )

    def __send_root_key(self, message: types.Message) -> None:
        self.__bot.send_message(
            message.chat.id,
            f'auth root key - {self.__key_log}\nDo not tell this for everyone'
        )

    @staticmethod
    def __save_buttons(path: str, button_name: str, button_text: str) -> None:
        path_exists(path)
        with open(f'{path}\\{button_name}.txt', 'w', encoding='utf-8') as file:
            file.write(button_text)

    @staticmethod
    def __load_buttons(path: str) -> dict[str: str]:
        out_dict: dict[str: str] = {}

        path_exists(path)

        for file in os.listdir(path):
            if os.path.isfile(f'{path}\\{file}') and file[-4:] == '.txt':
                with open(f'{path}\\{file}', 'r', encoding='utf-8') as f:
                    out_dict[file[:-4]] = '\n'.join(f.readlines())

        return out_dict

    @staticmethod
    def __load_echo(path: str) -> list[str]:
        out_echo: list[str] = []

        path_exists(path)

        for file in os.listdir(path):
            if os.path.isfile(f'{path}\\{file}') and file[-4:] == '.txt':
                with open(f'{path}\\{file}', 'r', encoding='utf-8') as f:
                    out_echo.append('\n'.join(f.readlines()))

        return out_echo

    def is_user_exist(self, user: types.User) -> bool:
        for i in range(len(self.__users)):
            if user.id == self.__users[i].id:
                return True

        return False

    @staticmethod
    def __load_users_json(path: str) -> list[types.User]:
        out_list: list[types.User] = []

        path_exists(path)

        for file_name in os.listdir(path):
            jpath = os.path.join(path, file_name)
            if os.path.isfile(jpath) and file_name[len(file_name) - 5:len(file_name)] == '.json':
                with open(jpath, 'r') as j:
                    out_list.append(types.User.de_json(json.load(j)))

        return out_list

    @staticmethod
    def __make_json_user(path: str, user: types.User) -> None:
        path_exists(path)

        with open(f'{path}/{user.username}.json', 'w') as j:
            json.dump(user.to_json(), j)

    def checker(self, call: types.CallbackQuery) -> bool:
        calls: list = list(self.__calls.keys())
        for i in range(len(calls)):
            if call.data[:len(calls[i])] == calls[i]:
                markup = self.__calls[calls[i]](call.data[len(calls[i]):])
                self.__bot.send_message(
                    call.message.chat.id,
                    f'"{call.data[len(calls[i]):]}"' + " - removed"
                )

                self.__bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=call.message.text,
                    reply_markup=markup
                )

                return True

        return False

    last_message: dict[int, str] = {}

    @property
    def get(self) -> list[str]:
        return list(self.__commands.keys())

    __commands: dict[str: tuple[any, str, str]] = {
        'add': (
            __add_root,
            '/add "safe_key"',
            '/root add "safe_key"\n'
            'or\n'
            '/add "safe_key"\n'
            'Command to add a new user with root permissions\n'
            'Safe key is autogenerated by code after init'
        ),
        'send': (
            __send,
            '/send "user" "message"',
            '/root send "user id / @ - all" "what to send"\n'
            'or\n'
            '/send "user id / @ - all" "what to send"\n'
            'to send info for 2 or more users write "id_first,id_second"\n'
            'use a "," as a separator, not a ", "'
        ),
        'add_button': (
            __add_button,
            '/add_button "button" "answer"',
            '/root add_button "button" "answer"\n'
            'or\n'
            '/add_button "button" "answer"\no'
            '/root add_button "button text" "answer for button click"\n'
        ),
        'remove_button': (
            __remove_button,
            '/remove_button',
            '/root remove_button"\nor\n'
            '/remove_button"\n'
            'Send a list of buttons which already exists in bot'
        ),
        'remove_echo': (
            __remove_echo,
            '/remove_echo',
            '/root remove_echo"\nor\n'
            '/remove_echo"\n'
            "Send a list of echo's which already exists in bot"
        ),
        'send_root_key': (
            __send_root_key,
            "/send_root_key",
            '/root send_root_key - send key to root auth\n'
            'or\n /send_root_key'
        ),
        "echo": (
            __echo,
            '/echo "message"',
            '/root echo "last_user_message"\nor\n'
            '/echo "last_user_message"\n'
            'Next message will be echo to all root users'
        ),
        'stop_bot': (
            __stop,
            "/stop_bot",
            '/root stop_bot - stop bot polling\nor\n'
            '/stop_bot'
        ),
        'help': (
            __help,
            "/help",
            '/root help - see all root commands\nor\n'
            '/help - see all root commands\n'
            '/root help "command" - send extension info for command'
        ),
    }

    buttons: dict[str: str] = {}

    def __init__(self, bot: telebot.TeleBot, button_save_path: str = "buttons", echo_save_path: str = "echo"):
        self.__key_log = self.__key_gen(10)
        self.__bot = bot

        self.__buttons_location = button_save_path
        self.__echo_location = echo_save_path

        self.buttons: dict[str: str] = dict(self.__load_buttons(self.__buttons_location)).copy()
        self.echo: list[str] = self.__load_echo(self.__echo_location)

        self.__root_users: list[types.User] = self.__load_users_json('json/root')
        self.__users: list[types.User] = self.__load_users_json('json/users')

        for i in range(len(self.__users)):
            self.last_message[self.__users[i].id] = ""

        def __echo(value) -> types.InlineKeyboardMarkup:
            lst = self.echo

            os.remove(f'{echo_save_path}\\{self.echo.index(value)}.txt')
            for i in range(self.echo.index(value), len(os.listdir(echo_save_path))):
                os.rename(f'{echo_save_path}\\{i + 1}.txt', f'{echo_save_path}\\{i}.txt')

            lst.remove(value)
            self.echo = lst

            inline = types.InlineKeyboardMarkup()

            for i in range(len(self.echo)):
                inline.add(types.InlineKeyboardButton(text=self.echo[i], callback_data=f'echo{self.echo[i]}'))

            return inline

        def __btn(value) -> types.InlineKeyboardMarkup:
            d: list = list(self.buttons.keys())
            out_d: dict[str: str] = {}
            d.remove(value)

            for i in range(len(d)):
                out_d[d[i]] = self.buttons[d[i]]

            self.buttons = out_d
            inline = types.InlineKeyboardMarkup()

            btn_list = list(self.buttons.keys())

            for i in range(len(btn_list)):
                inline.add(types.InlineKeyboardButton(text=btn_list[i], callback_data=f'btn{btn_list[i]}'))

            return inline

        self.__calls: dict[str: types.InlineKeyboardMarkup] = {
            "btn": lambda value: __btn(value),
            "echo": lambda value: __echo(value),
        }

        for i in range(len(self.__root_users)):
            self.last_message[self.__root_users[i].id] = ""
            self.__bot.send_message(
                self.__root_users[i].id,
                'bot is online',
                reply_markup=types.ReplyKeyboardRemove()
            )
