""" Default imports """
import asyncio
import logging
import sys

""" aiogram imports """
from aiogram import Dispatcher, Bot, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_file import BufferedInputFile
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, as_marked_section, as_key_value, as_list, Italic, Underline
from aiogram import F

""" Our app imports """
from db_settings.db_models import Player, Card, Character, Drop
from db_settings.db_requests import InitializeDataBase, DropCards, MainPlayer, GrabCard
from utils.custom_bot_commands import custom_commands, commands_list, help_text
from utils.user_permissions import user_is_verified
from api_keys import API_KEY

""" Bot init """
bot = Bot(token=API_KEY, parse_mode=ParseMode.HTML)
dp = Dispatcher(kbs=[])


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """ Greetings """
    await bot.set_my_commands(custom_commands())
    await message.answer(f'Hello, {hbold(message.from_user.full_name)}, im Karuta for Telegram! \n'
                         f' Please verify to start playing!'
                         f' Type /verify, also you can type /help to see list of commands')


""" Quick bot Commands """


@dp.callback_query(F.data == 'success')
async def success(callback: CallbackQuery) -> None:
    """ Calling this func when user verified """
    dp['player'] = MainPlayer(player=callback.from_user.username)
    dp['player'].create_player()
    print(dp['player'])
    await callback.message.answer('success')


@dp.callback_query(F.data == 'decline')
async def decline(callback: CallbackQuery) -> None:
    """ Calling this func when user declined verification """
    await callback.message.answer('decline')


@dp.message(Command('verify'))
async def verify_player(message: Message) -> None:
    """ Verifying user """
    buttons = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='✅', callback_data='success'),
        InlineKeyboardButton(text='❌', callback_data='decline')
    ]])

    await message.answer(**Bold('Wanna verify yourself?').as_kwargs(), reply_markup=buttons)


@dp.message(Command('help'))
async def help(message: Message) -> None:
    """ Help command to navigate in bot """
    command_help = as_list(
        as_marked_section(
            Bold('Commands:'),
            *[as_key_value(c, Underline(Italic(help_text[c]))) for c in sorted(help_text)],
            marker=' '
        ),
        sep="\n\n",
    )
    await message.answer(**command_help.as_kwargs())


@dp.message()
async def commands_listen(message: types.Message) -> None:
    """ Bot Commands Listener """

    drop = DropCards(3)
    get_player = drop.session.query(Player).filter_by(name=message.from_user.username).first()
    command = commands_list.keys()
    if message.text.lower() in command and user_is_verified(get_player):
        if message.text.lower() in 'kd':
            drop.run()
            dp['kbs'] = [InlineKeyboardButton(
                text=['1️⃣', '2️⃣', '3️⃣'][t],
                callback_data=str(d)
            ) for t, d in zip(range(len(drop.get_cards_id()[-3:])), drop.get_cards_id()[-3:])]

            keyboard = InlineKeyboardMarkup(inline_keyboard=[dp['kbs']])

            await message.answer_photo(
                reply_to_message_id=message.message_id,
                photo=BufferedInputFile(drop.merge().getvalue(), 'image.png'),
                reply_markup=keyboard,
            )

        if message.text.lower() in 'ki':
            """ Useless command for now... """

            commands_list['ki'] = f'{message.from_user.username} user inv'
            await message.answer(f'And this is inventory {commands_list[message.text.lower()]}')

        if message.text.lower() in 'kc':
            """ User card collection """

            player_cards = dp['player'].collection(player=get_player.name)

            """ Format the raw information in a human-readable format """
            get_collection = as_list(
                as_marked_section(
                    Bold('Characters: \n'),
                    *[as_key_value(i.code,
                                   ''.join(dp['player']
                                           .session.query(Character.character_name)
                                           .join(Character.cards)
                                           .where(Card.character_id == i.character_id).first()))
                      for i in player_cards],
                    marker=' '
                ),
                sep="\n\n\n",
            )
            print(player_cards)
            await message.answer(**get_collection.as_kwargs())

    else:
        await message.answer('Please verify before start playing 🙏')


@dp.callback_query()
async def grab_btns(callback: CallbackQuery):
    """ Getting the card that the user clicked on """

    grab = GrabCard()
    grabber = dp['player'].session.query(
        Player).filter_by(name=callback.from_user.username).first()

    print('--- CALLBACK DATA ---')
    print(int(callback.data))
    print(type(grab.grab()[0]))

    """ Getting card id from callback and adding it to user collection """
    if int(callback.data) in grab.grab():
        print('Card was successfully added to your collection!')
        grabber.player_cards.append(dp['player'].session.query(Card).filter_by(id=int(callback.data)).first())


async def main() -> None:
    """ Starting bot """
    await dp.start_polling(bot, start=InitializeDataBase())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
