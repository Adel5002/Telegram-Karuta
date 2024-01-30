from aiogram.types.bot_command_scope_default import BotCommandScopeDefault
from aiogram.types.bot_command import BotCommand


def custom_commands():
    bot_commands = [
        BotCommand(command='/help', description='Helps people!'),
        BotCommand(command='/verify', description='Verify people!'),
    ]
    return bot_commands


""" List of commands """
commands_list = {
    'kd': None,
    'kv': None,
    'ki': None,
    'kc': None,
    'klu': None,
}

""" Help text for commands """
help_text = {
    'kd': 'dropping cards...',
    'kv': 'viewing card...',
    'ki': 'player inventory...',
    'kc': 'player card collection...',
    'klu': 'card lookup...',
}
