from pathlib import Path
from interactions.client.client import Client
from interactions.ext.debug_extension import setup as de_setup
from interactions.ext.prefixed_commands.manager import setup as pc_setup
from interactions.models.discord.enums import Intents
from AlbertoX3 import __root_logger__
from AlbertoX3.constants import Config, LIB_PATH
from AlbertoX3.database import db, redis
from AlbertoX3.environment import TOKEN
from AlbertoX3.translations import load_translations
from AlbertoX3.utils.extensions import load_extensions, get_extensions


Config(LIB_PATH.parent.joinpath("config.alberto-x3.yml"))

bot = Client(
    token=TOKEN,
    intents=Intents.ALL,  # Intent.ALL is very bad practice!!!
)
pc_setup(client=bot, default_prefix="t!")
de_setup(bot)
load_translations()
load_extensions(bot=bot, extensions=get_extensions(folder=Path("./extensions/")))

bot.async_startup_tasks.append((db.create_tables, (), {}))
bot.async_startup_tasks.append((redis.execute_command, ("FLUSHDB", b"ASYNC"), {}))

__root_logger__.critical("This code is just for testing and does nothing useful by now!!!")

bot.start()
