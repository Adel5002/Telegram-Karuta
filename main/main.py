import asyncio
import logging
import sys

from aiogram import Dispatcher, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import BufferedInputFile
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, as_marked_section, as_key_value, as_list, Italic, Underline
from aiogram import F

from sqlalchemy import select

from db_settings.db_models import Player, Card, Character
from db_settings.db_requests import InitializeDataBase, DropCards, MainPlayer, GrabCard
from utils.custom_bot_commands import custom_commands, commands_list, help_text
from utils.user_permissions import user_is_verified
from api_keys import API_KEY

bot = Bot(token=API_KEY, parse_mode=ParseMode.HTML)
dp = Dispatcher()

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
    dp['player'] = MainPlayer(player=callback.from_user.username)
    dp['player'].create_player()
    print(dp['player'])
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
    get_player = dp['player'].session.query(Player).filter_by(name=message.from_user.username).first()
    command = commands_list.keys()
    if message.text.lower() in command and user_is_verified(get_player):
        if message.text.lower() in 'kd':
            drop = DropCards(3)
            drop.run()
            first_second_third = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='1️⃣', callback_data='first_btn'),
                InlineKeyboardButton(text='2️⃣', callback_data='second_btn'),
                InlineKeyboardButton(text='3️⃣', callback_data='third_btn'),
            ]])

            await message.answer_photo(
                reply_to_message_id=message.message_id,
                photo=BufferedInputFile(drop.merge().getvalue(), 'image.png'),
                reply_markup=first_second_third,
            )
        if message.text.lower() in 'ki':
            commands_list['ki'] = f'{message.from_user.username} user inv'
            await message.answer(f'And this is inventory {commands_list[message.text.lower()]}')

        if message.text.lower() in 'kc':
            player_cards = dp['player'].collection()

            # get_collection = as_list(
            #     as_marked_section(
            #         Bold('Commands: \n'),
            #         *[as_key_value(i.code,
            #                        ''.join(dp['player'].session.query(Card).join(Card.character).where(Character.id == i.character_id))) for i in player_cards],
            #         marker=' '
            #     ),
            #     sep="\n\n\n",
            # )
            print(player_cards)
            print(dp['player'].session.query(Card).join(Card.player).where(Player.name == message.from_user.username))
            # await message.answer(**get_collection.as_kwargs())

    else:
        await message.answer('Please verify before start playing 🙏')



@dp.callback_query()
async def grab_btns(callback: CallbackQuery):
    grab = GrabCard()
    grabber = dp['player'].session.query(
        Player).filter_by(name=callback.from_user.username).first()

    btns = {
        'first_btn': dp['player'].session.query(Card).where(
            Card.id == grab.grab()[0]).first(),
        'second_btn': dp['player'].session.query(Card).where(
            Card.id == grab.grab()[1]).first(),
        'third_btn': dp['player'].session.query(Card).where(
            Card.id == grab.grab()[2]).first(),
    }

    if callback.data in btns.keys():
        grabber.player_cards.append(btns.get(callback.data))
        # print(callback.data)
        # print(btns.keys())


async def main() -> None:
    await dp.start_polling(bot, start=InitializeDataBase())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
