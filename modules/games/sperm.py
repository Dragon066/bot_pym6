from botpackage import *

SPERM = {}


def load_sperm():
    global SPERM
    try:
        with open('files/sperm.txt', 'r', encoding='utf-8') as f:
            SPERM = json.load(f)
        SPERM = {int(k): v for k, v in SPERM.items()}
        log.info('SPERM загружено')
    except Exception as err:
        log.exception('Ошибка при загрузке SPERM')


def save_sperm():
    try:
        with open('files/sperm.txt', 'w', encoding='utf-8') as f:
            json.dump(SPERM, f, ensure_ascii=False, indent=4)
        log.info('SPERM сохранено')
    except Exception as err:
        log.exception('Ошибка при сохранении SPERM')


@dp.message_handler(commands=['gets'])
async def com_gets(msg):
    if msg.reply_to_message:
        id = msg.reply_to_message.from_user.id
        if id not in SPERM:
            sperm_create_default(msg)
        text = sperm_get_info_another(id)
        await msg.reply(text)
    else:
        id = msg.from_user.id
        if id not in SPERM:
            sperm_create_default(msg)
        text = sperm_get_info(id)
        await msg.reply(text, reply_markup=sperm_get_keyboard(id))


@dp.callback_query_handler(Text(startswith='sperm,'))
async def callback_sperm(call):
    if call.data.split(',')[1] == 'lvlup_power':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['power_level'] < 40:
            if SPERM[id]['bak'] > sperm_get_price_power(id):
                SPERM[id]['bak'] -= sperm_get_price_power(id)
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                SPERM[id]['power_level'] += 1
                save_sperm()
                await call.answer('Вы увеличили силу dro4ки!!! 🤩')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=sperm_get_info(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает спермы! 😡')
    elif call.data.split(',')[1] == 'lvlup_time':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['power_level'] < 40:
            if SPERM[id]['bak'] > sperm_get_price_time(id):
                SPERM[id]['bak'] -= sperm_get_price_time(id)
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                SPERM[id]['time_level'] += 1
                save_sperm()
                await call.answer('Вы укрепили зависимость и теперь можете dro4ить чаще!!!!! 🤩')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=sperm_get_info(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает спермы! 😡')


def sperm_get_keyboard(id):
    keyboard = types.InlineKeyboardMarkup()
    if SPERM[id]['power_level'] < 40:
        button1 = types.InlineKeyboardButton(text=f'LvLUP дрочка ({sperm_get_price_power(id)}мл 🥛)', callback_data=f'sperm,lvlup_power,{id}')
        keyboard.add(button1)
    if SPERM[id]['time_level'] < 40:
        button2 = types.InlineKeyboardButton(text=f'LvLUP зависимость ({sperm_get_price_time(id)}мл 🥛)', callback_data=f'sperm,lvlup_time,{id}')
        keyboard.add(button2)
    return keyboard


def sperm_get_info(id):
    text = f"🍆 <b>{SPERM[id]['name']}'s dick</b>\n\n" if not SPERM[id]['dickname'] else f"<b>{SPERM[id]['dickname']}</b>\n\n"
    text += f"📏 Длина вашей письки: <b>{SPERM[id]['len']} см</b>\n" \
           f"🥛 Спермобак: <b>{SPERM[id]['bak']} мл</b>\n\n" \
           f"💪 Уровень дрочки: <b>{SPERM[id]['power_level']}</b>\n" \
           f"🕔 Уровень зависимости: <b>{SPERM[id]['time_level']}</b> <i>({sperm_get_time(id)} мин)</i>\n" \
           f"💨 Количество CUMчей: <b>{SPERM[id]['cum_count']}</b> 💦\n\n"
    if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes = sperm_get_time(id)) < dt.datetime.now():
        text += f"❗️ <b>Время подрочить! /masturbate</b>"
    else:
        time = str(dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes = sperm_get_time(id)) - dt.datetime.now())
        time = time[:time.find('.')]
        text += f"⏳ <i>До следующей dro4ки: {time}</i>"
    if SPERM[id]['len'] * 0.8 > 1:
        text += f"\n\n<b>Вы можете кончить /cum</b>\n(потеря 20% длины, пополнение spermобака, вместо dro4ки)"
    else:
        text += f"\n\n🤏 Подростите письку и сможете кончить!"
    if not SPERM[id]['dickname']:
        text += f"\n\n✏️ С помощью 100 мл 🥛 и /rename вы можете переименовать свой 4leн 👀"
    return text


def sperm_get_info_another(id):
    text = f"🍆 <b>{SPERM[id]['name']}'s dick</b>\n\n" if not SPERM[id][
        'dickname'] else f"<b>{SPERM[id]['dickname']}</b>\n\n"
    text += f"📏 Длина вашей письки: <b>{SPERM[id]['len']} см</b>\n" \
            f"🥛 Спермобак: <b>{SPERM[id]['bak']} мл</b>\n\n" \
            f"💪 Уровень дрочки: <b>{SPERM[id]['power_level']}</b>\n" \
            f"🕔 Уровень зависимости: <b>{SPERM[id]['time_level']}</b> <i>({sperm_get_time(id)} мин)</i>\n" \
            f"💨 Количество CUMчей: <b>{SPERM[id]['cum_count']}</b> 💦\n\n"
    return text


def sperm_get_price_power(id):
    return round(1.5 * math.exp(SPERM[id]['power_level'] / 40 + 1) - 3 * (1 / (SPERM[id]['power_level'] + 1)), 2)


def sperm_get_price_time(id):
    return round(1.25 * math.exp(SPERM[id]['time_level'] / 40 + 1) - 3 * (1 / (SPERM[id]['time_level'] + 1)), 2)


def sperm_get_time(id):
    return 30 - SPERM[id]['time_level'] * 0.5


def sperm_get_len(id):
    from_ = 0.05 + 0.1 * SPERM[id]['power_level']
    to_ = 0.5 + 0.1 * SPERM[id]['power_level']
    return round(rnd.uniform(from_, to_), 2)


def sperm_create_default(msg):
    global SPERM
    id = msg.from_user.id
    name = msg.from_user.first_name
    SPERM[id] = {
        'name': name,
        'len': 1,
        'bak': 0,
        'dickname': None,
        'time': 0,
        'time_level': 0,
        'power_level': 0,
        'cum_count': 0
    }
    save_sperm()


@dp.message_handler(commands=['cum'])
async def com_cum(msg):
    id = msg.from_user.id
    if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(
            minutes=sperm_get_time(id)) < dt.datetime.now():
        if SPERM[id]['len'] * 0.8 > 1:
            SPERM[id]['time'] = dt.datetime.timestamp(dt.datetime.now())
            toadd = round(SPERM[id]['len'] * 0.2 * 0.5, 2)
            SPERM[id]['len'] = round(SPERM[id]['len'] * 0.8, 2)
            SPERM[id]['cum_count'] += 1
            SPERM[id]['bak'] += toadd
            SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
            save_sperm()
            await msg.reply(f'😲😲😲 <b>ВЫ КОНЧИЛИ!!!!</b> 💦💦💦\n\n<b>+{toadd} мл</b> в spermобак 🥛\n\nОставшаяся длина писюнчика: <b>{SPERM[id]["len"]} см</b>')
        else:
            await msg.reply('🤏🤏🤏 У вас слишком маленький писюн, чтобы кончить :( хаха')
    else:
        time = str(dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(
            minutes=sperm_get_time(id)) - dt.datetime.now())
        time = time[:time.find('.')]
        await msg.reply(f"До следующей дрочки: <b>{time}</b>")


@dp.message_handler(commands=['masturbate'])
async def com_masturbate(msg):
    if msg.reply_to_message:
        id = msg.reply_to_message.from_user.id
        if id not in SPERM:
            sperm_create_default(msg.reply_to_message)
        if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes=sperm_get_time(id)) < dt.datetime.now():
            SPERM[id]['time'] = dt.datetime.timestamp(dt.datetime.now())
            toadd = sperm_get_len(id)
            SPERM[id]['len'] += toadd
            SPERM[id]['len'] = round(SPERM[id]['len'], 2)
            await msg.reply(f"<b>{msg.from_user.first_name}</b> подрочил <b>{msg.reply_to_message.from_user.first_name}</b>! ❤️❤️❤️\n\n"
                            f"📏 Писька <b>{msg.reply_to_message.from_user.first_name}</b> увеличилась на <b>{toadd} см</b>\n"
                            f"Теперь длина этого dick'a: <b>{SPERM[id]['len']}</b> 👀")
            save_sperm()
        else:
            time = str(dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(
                minutes=sperm_get_time(id)) - dt.datetime.now())
            time = time[:time.find('.')]
            await msg.reply(f"⏳ До следующей дрочки для <b>{msg.reply_to_message.from_user.first_name}</b>: <b>{time}</b>")
    else:
        id = msg.from_user.id
        if id not in SPERM:
            sperm_create_default(msg)
        if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes=sperm_get_time(id)) < dt.datetime.now():
            SPERM[id]['time'] = dt.datetime.timestamp(dt.datetime.now())
            toadd = sperm_get_len(id)
            SPERM[id]['len'] += toadd
            SPERM[id]['len'] = round(SPERM[id]['len'], 2)
            await msg.reply(f"Ох хорошо (чудесно)! 😪\n\n📏 Ваша писька увеличилась на <b>{toadd} см</b>\n"
                            f"❤️ Теперь длина вашего 4leна: <b>{SPERM[id]['len']}</b>")
            save_sperm()
        else:
            time = str(dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(
                minutes=sperm_get_time(id)) - dt.datetime.now())
            time = time[:time.find('.')]
            await msg.reply(f"⏳ До следующей дрочки: <b>{time}</b>")


@dp.message_handler(commands=['tops'])
async def com_tops(msg):
    await msg.reply(sperm_get_top())


def sperm_get_top():
    global SPERM
    top = []
    for id, val in SPERM.items():
        top.append((val['dickname'] if val['dickname'] else f"{val['name']}'s dick", val['len']))
    top = sorted(top, key=lambda x: x[1], reverse=True)[:10]
    text = f"🥳 <b>Мега топ пиписек</b>:\n"
    for i, person in enumerate(top):
        text += f"\n{i + 1}) <b>{person[0]}</b> — {person[1]} см"
    return text


@dp.message_handler(commands=['rename'])
async def com_rename(msg):
    if msg.reply_to_message:
        id = msg.from_user.id
        if SPERM[id]['bak'] >= 100:
            SPERM[id]['bak'] -= 100
            SPERM[id]['dickname'] = msg.reply_to_message.text
            save_sperm()
            await msg.reply(f"Ура, вы переименовали свой dick в: <b>{msg.reply_to_message.text}</b> 👀\n\nЧудесное имя! ❤️❤️❤️")
        else:
            await msg.reply(f"Не хватает spermы! Дрочите чаще 😪")
    else:
        await msg.reply(f"Ответьте на сообщение с названием вашего dick'a, чтобы дать ему имя 👀\n<b>Стоимость - 100мл spermы 🥛</b>")


load_sperm()
log.info('Модуль sperm загружен')