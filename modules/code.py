from botpackage import *
import sympy as sp
import numpy as np
import itertools
import math


@dp.message_handler(commands=['code'])
async def com_code(msg):
    if checkright(msg):
        code = msg.text[6:]
        if len(code) > 0:
            try:
                if '\n' in code:
                    loc = {}
                    exec(code, globals(), loc)
                    res = '\n'.join([f'<b>{k}:</b> {v}' for k, v in loc.items()])
                    await msg.reply(f'<i>Код выполнен, результат:</i>\n{res}')
                else:
                    await msg.reply(eval(code))
            except Exception as err:
                await msg.reply(f'Ошибка выполнения:\n<i>{err}</i>')
                log.exception('Ошибка выполнения code')
        else:
            await msg.reply(f"✈ Для исполнения кода Python введите его в качестве аргумента.\n<i>Например, /code 1 + 1</i>")


log.info('Модуль code загружен')