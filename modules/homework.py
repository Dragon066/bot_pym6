from botpackage import *

HW = {value['name']: {} for lesson, value in json.load(open('files/lessons.txt', 'r', encoding='utf-8')).items()}
HW['Неопределено'] = {}


@dp.message_handler(commands=['wk'])
async def com_get_works(msg):
    if checkright(msg):
        await msg.answer(get_works())


@dp.message_handler(commands=['hw', 'hw7', 'hw7next'])
async def com_get_hw(msg):
    if checkright(msg):
        args = arguments(msg.text)
        date_start, date_stop = dt.date.today(), dt.date.today() + dt.timedelta(days=14)
        if args['com'] == 'hw':
            if len(args['args']) > 0:
                line = args['arg1'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
                try:
                    date_start = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
                    date_stop = date_start + dt.timedelta(days = 14)
                except:
                    pass
            if len(args['args']) > 1:
                line = args['arg2'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
                try:
                    date_stop = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
                except:
                    pass
        elif args['com'] == 'hw7':
            date_stop = dt.date.today()
            date_stop = date_stop + dt.timedelta(days=(6 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
        elif args['com'] == 'hw7next':
            date_start = date_start + dt.timedelta(days=(7 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
            date_stop = date_start + dt.timedelta(days=6)
        await go_hw(msg, date_start, date_stop)


@dp.message_handler(commands=['clear'])
async def com_clear(msg):
    if checkright(msg):
        clear_hw()
        await msg.answer(f"✅ Задания двухнедельной давности отчищены! 💨")


@dp.message_handler(commands=['add'])
async def com_add(msg):
    if checkright(msg):
        try:
            id = str(rnd.randint(1, 10000))
            add_hw('Неопределено', id, msg.reply_to_message.text)
            keyboard = types.InlineKeyboardMarkup()
            for subject in HW.keys():
                if subject != 'Неопределено':
                    button = types.InlineKeyboardButton(text=subject, callback_data=f"hw,{id},{subject}")
                    keyboard.add(button)
            button = types.InlineKeyboardButton(text="Другой...", callback_data=f'hw,{id},Неопределено')
            keyboard.add(button)
            await msg.answer("👌 Хорошо. Какой предмет?", reply_markup=keyboard)
        except Exception as err:
            log.exception('Ошибка добавления задания')


@dp.callback_query_handler(Text(startswith='hw,'))
async def callback_hw(call):
    if checkright(call, 'hw'):
        if call.data.split(',')[0] == 'hw':
            if call.message and call.data.split(',')[1] == 'cancel':
                id, subject = call.data.split(',')[2:]
                remove_hw('Неопределено', id)
                save_hw()
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="🚫 Заполнения задания отменено 😥")
            elif call.message and call.data.split(',')[1] == 'another':
                id, subject, value = call.data.split(',')[2:]
                keyboard = create_keyboard_dates(int(int(value) + 7), subject, id)
                button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hw,cancel,{id},{subject}')
                button2 = types.InlineKeyboardButton(text="Другие даты ➡",
                                                     callback_data=f'hw,another,{id},{subject},{int(int(value) + 7)}')
                keyboard.row(button1, button2)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"👍 Отлично, добавляю задание по предмету\n"
                                           f"<b>{subject}</b>.\n<i>На какое число?</i>",
                                      reply_markup=keyboard, parse_mode='HTML')
            elif call.message and call.data.split(',')[1] != '1':
                id, subject = call.data.split(',')[1:]
                keyboard = create_keyboard_dates(0, subject, id)
                button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hw,cancel,{id},{subject}')
                button2 = types.InlineKeyboardButton(text="Другие даты ➡",
                                                     callback_data=f'hw,another,{id},{subject},{0}')
                keyboard.row(button1, button2)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"👍 Отлично, добавляю задание по предмету\n"
                                           f"<b>{subject}</b>.\n<i>На какое число?</i>",
                                      reply_markup=keyboard, parse_mode='HTML')
            elif call.message:
                id, subject, date = call.data.split(',')[2:]
                text = HW['Неопределено'][id]
                remove_hw('Неопределено', id)
                add_hw(subject, date, text)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"🌟 Чудесно, по предмету <b>{subject}</b>\n"
                                           f"на <i>{convert(date)}</i>\n"
                                           f"добавлено задание: <b>{text}</b>", parse_mode='HTML')


@dp.callback_query_handler(Text(startswith='ed,'))
async def callback_ed(call):
    if checkright(call, 'edit'):
        if call.message and call.data.split(',')[0] == 'ed':
            if len(call.data.split(',')) < 3:
                subject = call.data.split(',')[1]
                keyboard = types.InlineKeyboardMarkup()
                for date in HW[subject]:
                    button = types.InlineKeyboardButton(text=convert(date) if subject != 'Неопределено' else date,
                                                        callback_data=f"ed,{subject},{date}")
                    keyboard.add(button)
                button = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f"ed,{subject},cancel")
                keyboard.add(button)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"🔎 Ага, смотрим домашки по предмету <b>{subject}</b>\n"
                                           f"<i>ДЗ какого числа меняем?</i>", reply_markup=keyboard, parse_mode='HTML')
            elif call.data.split(',')[2] == 'cancel':
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="🚫 Отменяем изменения, возвращаю всё на свои места! 😁")
            else:
                subject, date = call.data.split(',')[1], call.data.split(',')[2]
                text = HW[subject][date]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"<code>{text}</code>", parse_mode='HTML')


@dp.callback_query_handler(Text(startswith='del,'))
async def callback_del(call):
    if call.message and call.data.split(',')[0] == 'del':
        if checkright(call, 'del'):
            if len(call.data.split(',')) < 3:
                subject = call.data.split(',')[1]
                keyboard = types.InlineKeyboardMarkup()
                for date in HW[subject]:
                    button = types.InlineKeyboardButton(text=convert(date) if subject != 'Неопределено' else date,
                                                        callback_data=f"del,{subject},{date}")
                    keyboard.add(button)
                button = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f"del,{subject},cancel")
                keyboard.add(button)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"🔎 Ага, смотрим домашки по предмету <b>{subject}</b>\n"
                                           f"<i>ДЗ какого числа удаляем?</i>",
                                      reply_markup=keyboard, parse_mode='HTML')
            elif call.data.split(',')[2] == 'cancel':
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="Отменяем изменения, ничего не удаляем! 🙃")
            else:
                subject, date = call.data.split(',')[1], call.data.split(',')[2]
                text = HW[subject][date]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"🗑 Удаляем задание по предмету <b>{subject}</b>\n"
                                           f"На число <b>{convert(date) if subject != 'Неопределено' else date}</b>"
                                           f"\n<i>{text}</i>",
                                      parse_mode='HTML')
                remove_hw(subject, date)
                save_hw()


@dp.message_handler(commands=['del'])
async def com_del(msg):
    if checkright(msg):
        keyboard = types.InlineKeyboardMarkup()
        for subject in HW.keys():
            if len(HW[subject]) > 0:
                button = types.InlineKeyboardButton(text=subject, callback_data=f"del,{subject}")
                keyboard.add(button)
        button = types.InlineKeyboardButton(text="Другой...", callback_data=f'del,Неопределено')
        keyboard.add(button)
        await msg.answer("✏ Удаляем задание.\n<i>Какой предмет?</i>", reply_markup=keyboard, parse_mode='HTML')


@dp.message_handler(commands=['edit'])
async def com_edit(msg):
    if checkright(msg):
        keyboard = types.InlineKeyboardMarkup()
        for subject in HW.keys():
            if len(HW[subject]) > 0:
                button = types.InlineKeyboardButton(text=subject, callback_data=f"ed,{subject}")
                keyboard.add(button)
        button = types.InlineKeyboardButton(text="Другой...", callback_data=f'ed,Неопределено')
        keyboard.add(button)
        await msg.answer("✏ Круто, изменяем задание!\n<i>Какой предмет?</i>",
                         reply_markup=keyboard, parse_mode='HTML')


async def go_hw(msg, date_start, date_stop):
    await msg.answer(get_hw(date_start, date_stop), parse_mode='HTML')


def update_hw_file():
    global HW
    try:
        with open(HOMEWORK_path, 'r', encoding='utf-8') as f:
            HW = json.load(f)
        log.info('ДЗ загружено')
    except Exception as err:
        log.exception('Ошибка при загрузке ДЗ')


def backup_hw():
    try:
        if not os.path.exists(config['PATH']['homework_backup']):
            os.mkdir(config['PATH']['homework_backup'])
        file = f"{homework_backup_path}homework_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
        shutil.copy(HOMEWORK_path, file)
    except Exception as err:
        log.exception('Ошибка при бекапе ДЗ')


def save_hw():
    backup_hw()
    optimize_hw()
    try:
        with open(HOMEWORK_path, 'w', encoding='utf-8') as f:
            json.dump(HW, f, ensure_ascii=False, indent=4)
        log.info('ДЗ сохранено')
    except Exception as err:
        log.exception('Ошибка при сохранении ДЗ')


def optimize_hw():
    for key in HW:
        HW[key] = dict(sorted(HW[key].items()))


def add_hw(subject, date, text):
    if date == None:
        date = dt.date.today()
    HW[subject][str(date)] = text
    save_hw()


def remove_hw(subject, date):
    try:
        del HW[subject.capitalize()][date]
    except Exception as err:
        log.exception('Ошибка при удалении задания')


def clear_hw():
    date_stop = dt.date.today() - dt.timedelta(days = 14)
    to_remove = {}
    for subject in HW:
        if subject != 'Неопределено':
            for key, value in HW[subject].items():
                if dt.date(int(key[:key.find('-')]), int(key[key.find('-') + 1:key.find('-') + 3]), int(key[key.rfind('-') + 1:])) <= date_stop:
                    to_remove[subject] = key
    for subject, key in to_remove.items():
        del HW[subject][key]
    save_hw()


def get_hw(date_start=dt.date.today(), date_stop=dt.date.today() + dt.timedelta(days=14)):
    result = header(date_start, date_stop)
    sign_this, sign_another, sign_another2, sign_last, sign_today = config['UTILITY']['sign_this_weak'],\
                                             config['UTILITY']['sign_another_weak'],\
                                             config['UTILITY']['sign_another_weak2'],\
                                             config['UTILITY']['sign_last_weaks'], \
                                             config['UTILITY']['sign_today']
    date_another = dt.date.today()
    date_another += dt.timedelta(days = 6 - cal.weekday(date_another.year, date_another.month, date_another.day))
    if len(HW['Неопределено']) > 0:
        for key, value in HW['Неопределено'].items():
            result += f"<i>Неопределено, {key}</i> - {value}\n"
        result += '\n'
    while date_start <= date_stop:
        flag = True
        for subject in HW:
            if subject != 'Неопределено':
                for key, value in HW[subject].items():
                    if date_start == dt.date.fromisoformat(key):
                        if flag:
                            result += f"{sign_today if date_start == dt.date.today() else sign_last if date_start < dt.date.today() else sign_this if date_start <= date_another else sign_another if date_start <= date_another + dt.timedelta(days=7) else sign_another2} " \
                                      f"<b>{convert_dayhw(str(date_start))}</b>:\n\n"
                            flag = False
                        result += f"  <b>{subject}</b> - {value}\n\n"
                        break
        date_start += dt.timedelta(days = 1)
    if abs(len(result) - len(header(date_start, date_stop))) < 5:
        result += 'Домашнего задания нет 🥳'
    return result


def get_works(date_stop = dt.date.today() + dt.timedelta(days=21)):
    date_start = dt.date.today()
    result = header_works(date_start, date_stop)
    sign_this, sign_another, sign_another2, sign_last, sign_today = config['UTILITY']['sign_this_weak'], \
                                                                    config['UTILITY']['sign_another_weak'], \
                                                                    config['UTILITY']['sign_another_weak2'], \
                                                                    config['UTILITY']['sign_last_weaks'], \
                                                                    config['UTILITY']['sign_today']
    date_another = dt.date.today()
    date_another += dt.timedelta(days=6 - cal.weekday(date_another.year, date_another.month, date_another.day))
    if len(HW['Неопределено']) > 0:
        for key, value in HW['Неопределено'].items():
            if '❗' in value:
                result += f"<i>Неопределено</i> - {value[value.find('❗'):]}\n"
        if abs(len(result) - len(header_works(date_start, date_stop))) < 5:
            result += '\n'
    while date_start <= date_stop:
        flag = True
        for subject in HW:
            if subject != 'Неопределено':
                for key, value in HW[subject].items():
                    if date_start == dt.date.fromisoformat(key):
                        if '❗' in value:
                            if flag:
                                result += f"{sign_today if date_start == dt.date.today() else sign_last if date_start < dt.date.today() else sign_this if date_start <= date_another else sign_another if date_start <= date_another + dt.timedelta(days=7) else sign_another2} " \
                                          f"<b>{convert_dayhw(str(date_start))}</b>:\n\n"
                                flag = False
                            result += f"  <b>{subject}</b> - {value[value.find('❗'):]}\n\n"
                            break
        date_start += dt.timedelta(days = 1)
    if abs(len(result) - len(header_works(date_start, date_stop))) < 5:
        result += "Работ нет! 😦"
    return result


log.info('Модуль homework загружен')