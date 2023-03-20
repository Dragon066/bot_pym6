from botpackage import *

STATS = {}


@dp.message_handler(commands=['stats'])
async def com_get_stats(msg):
    if checkright(msg):
        await msg.answer(get_stats())


def stat(command):
    if command in STATS:
        STATS[command] += 1
    else:
        STATS[command] = 1


def clear_stats():
    STATS = {}


def get_stats():
    text = f'📊 <b>Статистика</b>\n<i>за прошедший день</i>\n\n'
    if len(STATS) > 0:
        for command, value in STATS.items():
            text += f"<b>/{command}</b> - {value}\n"
    else:
        text += 'Статистика отсутствует'
    return text

log.info('Модуль statistics загружен')
