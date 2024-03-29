from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor, markdown

import sys
import yaml
import re
import math
import datetime as dt
import calendar as cal
import random as rnd
import requests
import shutil
import os
import json
import hashlib
import asyncio
import aiohttp
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from modules.logger import log

log.info('--------------------------------------')
log.info('Библиотеки загружены')
log.info('Загрузка модулей...')

try:
    config = yaml.safe_load(open('config.yaml', 'r', encoding='utf-8'))
except Exception as ex:
    print(f'Ошибка при загрузке конфига: {ex}')
    log.exception('Ошибка при загрузке конфига')

token = config['SECURITY']['token'] if not config['SECURITY']['test_bot'] else config['SECURITY']['token2']

bot = Bot(token=token, parse_mode='HTML', disable_web_page_preview=True)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})

ADM_GROUP = config['SECURITY']['admin_group'] if not config['SECURITY']['test_bot'] else 1056768423
GROUP = config['SECURITY']['group'] if not config['SECURITY']['test_bot'] else 1056768423
GROUP_NAME = config['SECURITY']['group_name']
BOT_ID = int(config['SECURITY']['bot_id'])

SEND_HD = config['SETTINGS']['send_hd']
SEND_STATS = config['SETTINGS']['send_stats']
SEND_TOPS = config['SETTINGS']['send_tops']
SEND_FACTS = config['SETTINGS']['send_facts']
SEND_WEATHER = config['SETTINGS']['send_weather']
SEND_CATS = config['SETTINGS']['send_cats']
SILENCE = True

USERS_path = config['PATH']['users']
HOMEWORK_path = config['PATH']['homework']
MEDIA_path = config['PATH']['media']
RUZ_path = config['PATH']['ruz']
FILES_path = config['PATH']['files']
STATS_path = config['PATH']['stats']
CATSHASH_path = config['PATH']['catshash']

users_backup_path = config['PATH']['users_backup']
homework_backup_path = config['PATH']['homework_backup']
files_backup_path = config['PATH']['files_backup']
ruz_backup_path = config['PATH']['ruz_backup']
mail_backup_path = config['PATH']['mail_backup']

UPTIME = dt.datetime.now()

from modules.service import *
from modules.permissions import *
from modules.statistics import *
update_users()

if config['MODULES']['homework']:
    from modules.homework import *

    update_hw_file()

if config['MODULES']['holidays']:
    from modules.holidays import *

if config['MODULES']['commands']:
    from modules.commands import *

if config['MODULES']['files']:
    from modules.files import *

    update_files()

if config['MODULES']['ruz']:
    from modules.ruz import *

if config['MODULES']['gmail']:
    from modules.gmail import *

    load_mail()

if config['MODULES']['code']:
    from modules.code import *

if config['MODULES']['open']:
    from modules.open import *

if config['MODULES']['weather']:
    from modules.weather import *

if config['MODULES']['sperm']:
    from modules.games.sperm import *

if config['MODULES']['cats_congrat']:
    from modules.cats_congrat import *

if config['MODULES']['sched']:
    from modules.sched import *

if config['MODULES']['crossword']:
    from modules.games.crossword import *

if config['MODULES']['chatgpt']:
    from modules.chatgpt import *
