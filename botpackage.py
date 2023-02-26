from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

import sys
import yaml
import re
import datetime as dt
import calendar as cal
import random as rnd
import requests
import shutil
import os
import json
import hashlib
import asyncio
from io import StringIO, BytesIO
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

bot = Bot(token=token, parse_mode='HTML')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})

ADM_GROUP = config['SECURITY']['admin_group']
GROUP = config['SECURITY']['group']
GROUP_NAME = config['SECURITY']['group_name']
BOT_ID = int(config['SECURITY']['bot_id'])

SEND_HD = int(config['SETTINGS']['send_hd'])

USERS_path = config['PATH']['users']
HOMEWORK_path = config['PATH']['homework']
MEDIA_path = config['PATH']['media']
RUZ_path = config['PATH']['ruz']
FILES_path = config['PATH']['files']

users_backup_path = config['PATH']['users_backup']
homework_backup_path = config['PATH']['homework_backup']
files_backup_path = config['PATH']['files_backup']
ruz_backup_path = config['PATH']['ruz_backup']
mail_backup_path = config['PATH']['mail_backup']

UPTIME = dt.datetime.now()

from modules.service import *
from modules.permissions import *
update_users()