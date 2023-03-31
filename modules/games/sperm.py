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
    except Exception as err:
        log.exception('Ошибка при сохранении SPERM')


@dp.message_handler(commands=['gets'])
async def com_gets(msg):
    if msg.reply_to_message:
        id = msg.reply_to_message.from_user.id
        if id not in SPERM:
            sperm_create_default(msg.reply_to_message)
        text = sperm_get_info_another(id)
    else:
        id = msg.from_user.id
        if id not in SPERM:
            sperm_create_default(msg)
        text = sperm_get_info(id)
    await msg.reply(text)


@dp.message_handler(commands=['shops'])
async def com_shops(msg):
    id = msg.from_user.id
    if id not in SPERM:
        sperm_create_default(msg)
    text = sperm_get_shop(id)
    await msg.reply(text, reply_markup=sperm_get_keyboard(id))


@dp.callback_query_handler(Text(startswith='sperm,'))
async def callback_sperm(call):
    if call.data.split(',')[1] == 'lvlup_power':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['power_level'] < 40:
            if SPERM[id]['bak'] >= sperm_get_price_power(id):
                SPERM[id]['bak'] -= sperm_get_price_power(id)
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                SPERM[id]['power_level'] += 1
                save_sperm()
                await call.answer('Вы увеличили силу dro4ки!!! 🤩')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=sperm_get_shop(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает спермы! 😡')
    elif call.data.split(',')[1] == 'lvlup_time':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['power_level'] < 40:
            if SPERM[id]['bak'] >= sperm_get_price_time(id):
                SPERM[id]['bak'] -= sperm_get_price_time(id)
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                SPERM[id]['time_level'] += 1
                save_sperm()
                await call.answer('Вы укрепили зависимость и теперь можете dro4ить чаще!!!!! 🤩')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=sperm_get_shop(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает спермы! 😡')
    elif call.data.split(',')[1] == 'lvlup_rate':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['rate_level'] < 10:
            if SPERM[id]['exp'] >= sperm_get_price_rate(id):
                SPERM[id]['exp'] -= sperm_get_price_rate(id)
                SPERM[id]['exp'] = round(SPERM[id]['exp'], 2)
                SPERM[id]['rate_level'] += 1
                save_sperm()
                await call.answer('У вас увеличились яйца, вы стали круче 😎😎😎😎')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=sperm_get_shop(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает опыта! 😒')
    elif call.data.split(',')[1] == 'lvlup_skill':
        id = int(call.data.split(',')[2])
        if id == call.from_user.id and SPERM[id]['skill_level'] < 40:
            if SPERM[id]['exp'] >= sperm_get_price_skill(id):
                SPERM[id]['exp'] -= sperm_get_price_skill(id)
                SPERM[id]['exp'] = round(SPERM[id]['exp'], 2)
                SPERM[id]['skill_level'] += 1
                save_sperm()
                await call.answer('Вы повысили своё мастерство, мастер 🙏🙏')
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=sperm_get_shop(id), reply_markup=sperm_get_keyboard(id))
            else:
                await call.answer('Не хватает опыта! 😒')


def sperm_get_keyboard(id):
    keyboard = types.InlineKeyboardMarkup()
    if SPERM[id]['power_level'] < 40:
        button = types.InlineKeyboardButton(text=f'LvLUP дрочка ({sperm_get_price_power(id)}мл 🥛)', callback_data=f'sperm,lvlup_power,{id}')
        keyboard.add(button)
    if SPERM[id]['time_level'] < 40:
        button = types.InlineKeyboardButton(text=f'LvLUP зависимость ({sperm_get_price_time(id)}мл 🥛)', callback_data=f'sperm,lvlup_time,{id}')
        keyboard.add(button)
    if SPERM[id]['rate_level'] < 10:
        button = types.InlineKeyboardButton(text=f'LvLUP яйца ({sperm_get_price_rate(id)}exp 🌀)', callback_data=f'sperm,lvlup_rate,{id}')
        keyboard.add(button)
    if SPERM[id]['skill_level'] < 40:
        button = types.InlineKeyboardButton(text=f'LvLUP мастерство ({sperm_get_price_skill(id)}exp 🌀)', callback_data=f'sperm,lvlup_skill,{id}')
        keyboard.add(button)
    return keyboard


def sperm_get_shop(id):
    text = f"🍆 <b>{SPERM[id]['name']}'s dick</b>\n\n" if not SPERM[id][
        'dickname'] else f"<b>{SPERM[id]['dickname']}</b>\n\n"
    text += f"📏 Длина вашей письки: <b>{SPERM[id]['len']} см</b>\n" \
            f"🌀 Опыт: <b>{SPERM[id]['exp']} exp</b>\n" \
            f"🥛 Спермобак: <b>{SPERM[id]['bak']} мл</b>\n\n" \
            f"💪 Уровень дрочки: <b>{SPERM[id]['power_level']}</b>\n" \
            f"💪 {':' * (SPERM[id]['power_level'] - 1)}|{'.' * (39 - SPERM[id]['power_level'])}\n" \
            f"🕔 Уровень зависимости: <b>{SPERM[id]['time_level']}</b> <i>({sperm_get_time(id)} мин)</i>\n" \
            f"🕔 {':' * (SPERM[id]['time_level'] - 1)}|{'.' * (39 - SPERM[id]['time_level'])}\n" \
            f"🥚 Уровень яиц: <b>{SPERM[id]['rate_level']}</b>\n" \
            f"🥚 {':' * (SPERM[id]['rate_level'] - 1)}|{'.' * (9 - SPERM[id]['rate_level'])}\n" \
            f"🚼 Уровень мастерства: <b>{SPERM[id]['skill_level']}</b>\n" \
            f"🚼 {':' * (SPERM[id]['skill_level'] - 1)}|{'.' * (39 - SPERM[id]['skill_level'])}\n"
    return text

def sperm_get_info(id):
    text = f"🍆 <b>{SPERM[id]['name']}'s dick</b>\n\n" if not SPERM[id]['dickname'] else f"<b>{SPERM[id]['dickname']}</b>\n\n"
    text += f"📏 Длина вашей письки: <b>{SPERM[id]['len']} см</b>\n" \
           f"🌀 Опыт: <b>{SPERM[id]['exp']} exp</b>\n" \
           f"🥛 Спермобак: <b>{SPERM[id]['bak']} мл</b>\n\n" \
           f"💪 Уровень дрочки: <b>{SPERM[id]['power_level']}</b>\n" \
           f"💪 {':'*(SPERM[id]['power_level'] - 1)}|{'.'*(39 - SPERM[id]['power_level'])}\n" \
           f"🕔 Уровень зависимости: <b>{SPERM[id]['time_level']}</b> <i>({sperm_get_time(id)} мин)</i>\n" \
           f"🕔 {':'*(SPERM[id]['time_level'] - 1)}|{'.'*(39 - SPERM[id]['time_level'])}\n" \
           f"🥚 Уровень яиц: <b>{SPERM[id]['rate_level']}</b>\n" \
           f"🥚 {':'*(SPERM[id]['rate_level'] - 1)}|{'.'*(9 - SPERM[id]['rate_level'])}\n" \
           f"🚼 Уровень мастерства: <b>{SPERM[id]['skill_level']}</b>\n" \
           f"🚼 {':'*(SPERM[id]['skill_level'] - 1)}|{'.'*(39 - SPERM[id]['skill_level'])}\n" \
           f"🍌 Количество мастурбаций: <b>{SPERM[id]['masturbate_count']}</b>\n" \
           f"💨 Количество CUMчей: <b>{SPERM[id]['cum_count']}</b> 💦\n\n"
    if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes = sperm_get_time(id)) < dt.datetime.now():
        text += f"❗️ <b>Время подрочить! /masturbate</b>"
    else:
        time = str(dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes = sperm_get_time(id)) - dt.datetime.now())
        time = time[:time.find('.')]
        text += f"⏳ <i>До следующей dro4ки: {time}</i>"
    if SPERM[id]['len'] * 0.8 > 1 and (dt.datetime.fromtimestamp(int(SPERM[id]['cum_time'])) + dt.timedelta(minutes = sperm_get_time(id)) < dt.datetime.now()):
        text += f"\n\n<b>Вы можете кончить /cum</b>\n(потеря 20% длины, пополнение 10% spermобака)"
    elif SPERM[id]['len'] * 0.8 > 1:
        time = str(dt.datetime.fromtimestamp(int(SPERM[id]['cum_time'])) + dt.timedelta(
            minutes=sperm_get_time(id)) - dt.datetime.now())
        time = time[:time.find('.')]
        text += f"\n\n🏖 До следующего камшота: <b>{time}</b>"
    else:
        text += f"\n\n🤏 Подростите письку и сможете кончить!"
    if not SPERM[id]['dickname']:
        text += f"\n\n✏️ С помощью 100 мл 🥛 и /rename вы можете переименовать свой 4leн 👀"
    return text


def sperm_get_info_another(id):
    text = f"🍆 <b>{SPERM[id]['name']}'s dick</b>\n\n" if not SPERM[id][
        'dickname'] else f"<b>{SPERM[id]['dickname']}</b>\n\n"
    text += f"🌀 Опыт: <b>{SPERM[id]['exp']} exp</b>\n" \
           f"🥛 Спермобак: <b>{SPERM[id]['bak']} мл</b>\n\n" \
           f"💪 Уровень дрочки: <b>{SPERM[id]['power_level']}</b>\n" \
           f"💪 {':'*(SPERM[id]['power_level'] - 1)}|{'.'*(39 - SPERM[id]['power_level'])}\n" \
           f"🕔 Уровень зависимости: <b>{SPERM[id]['time_level']}</b> <i>({sperm_get_time(id)} мин)</i>\n" \
           f"🕔 {':'*(SPERM[id]['time_level'] - 1)}|{'.'*(39 - SPERM[id]['time_level'])}\n" \
           f"🥚 Уровень яиц: <b>{SPERM[id]['rate_level']}\n</b>" \
           f"🥚 {':'*(SPERM[id]['rate_level'] - 1)}|{'.'*(9 - SPERM[id]['rate_level'])}\n" \
           f"🚼 Уровень мастерства: <b>{SPERM[id]['skill_level']}</b>\n" \
           f"🚼 {':'*(SPERM[id]['skill_level'] - 1)}|{'.'*(39 - SPERM[id]['skill_level'])}\n" \
           f"🍌 Количество мастурбаций: <b>{SPERM[id]['masturbate_count']}</b>\n" \
           f"💨 Количество CUMчей: <b>{SPERM[id]['cum_count']}</b> 💦\n\n"
    return text


def sperm_get_price_power(id):
    n = SPERM[id]['power_level'] + 1
    return round(0.5 * n + (n / 10) ** 1.85535, 2)


def sperm_get_price_time(id):
    n = SPERM[id]['time_level'] + 1
    return round(0.25 * n + (n / 7) ** 1.9051, 2)


def sperm_get_price_rate(id):
    n = SPERM[id]['rate_level'] + 1
    return round((9.9259 + 1.5 * n) ** math.e)


def sperm_get_price_skill(id):
    n = SPERM[id]['skill_level'] + 1
    return round(10 + 11 * n + (n / 2) ** 2.003152)


def sperm_get_rate(id):
    return SPERM[id]['rate'] * (1 + 0.1 * SPERM[id]['rate_level'])


def sperm_get_time(id):
    return 30 - SPERM[id]['time_level'] * 0.5


def sperm_get_exp(id):
    rand = rnd.uniform(1 + 0.25 * SPERM[id]['rate_level'], 10 + 0.25 * SPERM[id]['rate_level'])
    return round(sperm_get_rate(id) * rand)


def sperm_get_len(id):
    from_ = 0.05 + 0.05 * SPERM[id]['power_level']
    to_ = 0.5 + 0.1 * SPERM[id]['power_level']
    return round(sperm_get_rate(id) * rnd.uniform(from_, to_), 2)


def sperm_get_random(id):
    n = SPERM[id]['skill_level']
    return rnd.uniform(0, 1) <= (5 + 1.125 * n) / 100


def sperm_create_default(msg):
    global SPERM
    id = msg.from_user.id
    name = msg.from_user.first_name
    SPERM[id] = {
        'name': name,
        'len': 1,
        'bak': 0,
        'exp': 0,
        'dickname': None,
        'time': 0,
        'cum_time': 0,
        'time_level': 0,
        'power_level': 0,
        'skill_level': 0,
        'rate_level': 0,
        'rate': 1,
        'rate_time': 0,
        'cum_count': 0,
        'masturbate_count': 0
    }
    save_sperm()


@dp.message_handler(commands=['cum'])
async def com_cum(msg):
    id = msg.from_user.id
    if dt.datetime.fromtimestamp(int(SPERM[id]['cum_time'])) + dt.timedelta(
            minutes=sperm_get_time(id)) < dt.datetime.now():
        if SPERM[id]['len'] * 0.8 > 1:
            SPERM[id]['cum_time'] = dt.datetime.timestamp(dt.datetime.now())
            tominus = round(SPERM[id]['len'] * 0.2, 2)
            if not(sperm_get_random(id)):
                toadd = round(sperm_get_rate(id) * SPERM[id]['len'] * 0.2 * 0.5, 2)
                SPERM[id]['len'] = round(SPERM[id]['len'] * 0.8, 2)
                SPERM[id]['bak'] += toadd
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                await msg.reply(
                    f'😲😲😲 <b>ВЫ КОНЧИЛИ!!!!</b> 💦💦💦\n\n<b>+{toadd} мл</b> в spermобак 🥛\n\nОставшаяся длина писюнчика: <b>{SPERM[id]["len"]} см</b> (-{tominus}см)')
            else:
                toadd = round(2 * sperm_get_rate(id) * SPERM[id]['len'] * 0.2 * 0.5, 2)
                SPERM[id]['len'] = round(SPERM[id]['len'] * 0.8, 2)
                SPERM[id]['bak'] += toadd
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                await msg.reply(
                    f'😲😲😲 <b>МЕГА КАМШОТ Х2!!!!</b> 💦💦💦\n<i>Ваше мастерство поражает!</i>\n<b>+{toadd} мл</b> в spermобак 🥛\n\nОставшаяся длина писюнчика: <b>{SPERM[id]["len"]} см</b> (-{tominus}см)')
            SPERM[id]['cum_count'] += 1
            save_sperm()

        else:
            await msg.reply('🤏🤏🤏 У вас слишком маленький писюн, чтобы кончить :( хаха')
    else:
        time = str(dt.datetime.fromtimestamp(int(SPERM[id]['cum_time'])) + dt.timedelta(
            minutes=sperm_get_time(id)) - dt.datetime.now())
        time = time[:time.find('.')]
        await msg.reply(f"🏖 До следующего камшота: <b>{time}</b>")


@dp.message_handler(commands=['masturbate'])
async def com_masturbate(msg):
    if msg.reply_to_message:
        id = msg.reply_to_message.from_user.id
        if id not in SPERM:
            sperm_create_default(msg.reply_to_message)
        if dt.datetime.fromtimestamp(int(SPERM[id]['time'])) + dt.timedelta(minutes=sperm_get_time(id)) < dt.datetime.now():
            SPERM[id]['time'] = dt.datetime.timestamp(dt.datetime.now())
            toadd = round(sperm_get_rate(id) * sperm_get_len(id), 2)
            SPERM[id]['len'] += toadd
            SPERM[id]['len'] = round(SPERM[id]['len'], 2)
            add_exp = sperm_get_exp(id)
            SPERM[id]['exp'] += add_exp
            SPERM[id]['masturbate_count'] += 1
            SPERM[msg.from_user.id]['exp'] += round(add_exp * 0.2)
            await msg.reply(f"<b>{msg.from_user.first_name}</b> подрочил <b>{msg.reply_to_message.from_user.first_name}</b>! ❤️❤️❤️\n\n"
                            f"📏 Писька <b>{msg.reply_to_message.from_user.first_name}</b> увеличилась на <b>{toadd} см</b>\n"
                            f"Теперь длина этого dick'a: <b>{SPERM[id]['len']}</b> 👀\n\n"
                            f"Also, <b>+{add_exp} exp 🌀</b> для <b>{msg.reply_to_message.from_user.first_name}</b> и"
                            f" <b>+{round(add_exp * 0.2)}</b> для <b>{msg.from_user.first_name}</b>")
            if sperm_get_random(id):
                SPERM[id]['bak'] += toadd * 0.5
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                await msg.reply(f"ВЫ ЗАСТАВИЛИ <b>{msg.reply_to_message.from_user.first_name}</b> ПОТЕЧЬ УФФФФ 💦💦💦💦\n\n"
                                f"Вы, как истинный ценитель dro4ки, помогли собрать кончу в баночку:\n"
                                f"<b>+{round(toadd * 0.5, 2)} мл</b> в spermoбак 🥛")
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
            toadd = round(sperm_get_rate(id) * sperm_get_len(id), 2)
            SPERM[id]['len'] += toadd
            SPERM[id]['len'] = round(SPERM[id]['len'], 2)
            add_exp = sperm_get_exp(id)
            SPERM[id]['exp'] += add_exp
            SPERM[id]['masturbate_count'] += 1
            await msg.reply(f"Ох хорошо! 😪\n\n📏 Ваша писька увеличилась на <b>{toadd} см</b>\n"
                            f"❤️ Теперь длина вашего 4leна: <b>{SPERM[id]['len']}\n\n</b>"
                            f"Also, +{add_exp} exp 🌀")
            if sperm_get_random(id):
                SPERM[id]['bak'] += toadd * 0.5
                SPERM[id]['bak'] = round(SPERM[id]['bak'], 2)
                await msg.reply(f"Вы потекли 💦💦😢\n\n"
                                f"Но это даже хорошо! Вы немного, конечно же, случайно, кончили:\n"
                                f"<b>+{round(toadd * 0.5, 2)} мл</b> в spermoбак 🥛")
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