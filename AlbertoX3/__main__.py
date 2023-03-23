from pathlib import Path
from interactions.client.client import Client
from interactions.ext.prefixed_commands.manager import setup as pc_setup
from interactions.models.discord.enums import Intents
from AlbertoX3 import __root_logger__
from AlbertoX3.environment import TOKEN
from AlbertoX3.utils import load_extensions, get_extensions


bot = Client(
    token=TOKEN,
    intents=Intents.ALL,  # Intent.ALL is very bad practice!!!
)
pc_setup(client=bot, default_prefix="t!")
load_extensions(bot=bot, extensions=get_extensions(folder=Path("./extensions/")))


__root_logger__.critical("This code is just for testing and does nothing useful by now!!!")

bot.start()
