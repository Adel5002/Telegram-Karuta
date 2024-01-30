import asyncio
import logging
import sys

from aiogram.types.user import User
from aiogram import Dispatcher, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, as_marked_section, as_key_value, as_list, Italic, Underline
from aiogram import F

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db_settings.db_models import Base, Player
from utils.custom_bot_commands import custom_commands, commands_list, help_text
from utils.user_permissions import user_is_verified
from api_keys import API_KEY
from utils.bot_commands_fucntionality import generate_cards

dp = Dispatcher()
bot = Bot(token=API_KEY, parse_mode=ParseMode.HTML)

""" Initializing DB """

engine = create_engine("sqlite://", echo=True)
initialize_db = Base.metadata.create_all(engine)

session = Session(bind=engine)

""" Greetings """


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    # user = User(id=message.from_user.id, is_bot=message.from_user.is_bot, first_name=message.from_user.username)
    await bot.set_my_commands(custom_commands())
    await message.answer(f'Hello, {hbold(message.from_user.full_name)}, im Karuta for Telegram! \n'
                         f' Please verify to start playing!'
                         f' Type /verify, also you can type /help to see list of commands')


""" Custom Commands """


@dp.callback_query(F.data == 'success')
async def success(callback: CallbackQuery) -> None:
    player = Player(name=callback.from_user.username, is_verified=True)
    session.add(player)
    # print(session.query(Player).filter_by(name=callback.from_user.username).first())
    print(callback.from_user.username)
    await callback.message.answer('success')


@dp.callback_query(F.data == 'decline')
async def decline(callback: CallbackQuery) -> None:
    await callback.message.answer('decline')


@dp.message(Command('verify'))
async def verify_player(message: Message) -> None:
    buttons = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='✅', callback_data='success'),
        InlineKeyboardButton(text='❌', callback_data='decline')
    ]])

    await message.answer(**Bold('Wanna verify yourself?').as_kwargs(), reply_markup=buttons)


@dp.message(Command('help'))
async def help(message: Message) -> None:
    command_help = as_list(
        as_marked_section(
            Bold('Commands:'),
            *[as_key_value(c, Underline(Italic(help_text[c]))) for c in sorted(help_text)],
            marker=' '
        ),
        sep="\n\n",
    )
    await message.answer(**command_help.as_kwargs())


""" Bot Commands Listener """


@dp.message()
async def commands_listen(message: types.Message) -> None:
    get_player_info = session.query(Player).filter_by(name=message.from_user.username).first()
    command = commands_list.keys()
    if message.text.lower() in command and user_is_verified(get_player_info):
        if message.text.lower() in 'kd':
            commands_list['kd'] = ', '.join(generate_cards(3))
            first_second_third = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='1️⃣', callback_data='first_btn'),
                InlineKeyboardButton(text='2️⃣', callback_data='second_btn'),
                InlineKeyboardButton(text='3️⃣', callback_data='third_btn'),
            ]])
            await message.answer(f'{commands_list[message.text.lower()]}', reply_markup=first_second_third)
        if message.text.lower() in 'ki':
            commands_list['ki'] = f'{message.from_user.username} user inv'
            await message.answer(f'And this is inventory {commands_list[message.text.lower()]}')
    else:
        await message.answer('Please verify before start playing 🙏')
        print(f'IM HERE {command}!!!!')


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
