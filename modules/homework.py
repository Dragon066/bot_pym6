from botpackage import *
import aiogram.utils.exceptions

LESSONS = json.load(open('files/lessons.txt', 'r', encoding='utf-8'))
HW = {lesson: {} for lesson in LESSONS}
temp_hw = {}


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
    clear_hw()
    for key in HW:
        HW[key] = dict(sorted(HW[key].items()))
    try:
        with open(HOMEWORK_path, 'w', encoding='utf-8') as f:
            json.dump(HW, f, ensure_ascii=False, indent=4)
        log.info('ДЗ сохранено')
    except Exception as err:
        log.exception('Ошибка при сохранении ДЗ')


def get_keyboard_dates(start, id):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(int(start), int(start) + 7):
        date1 = str(dt.date.today() + dt.timedelta(days = i))
        date2 = str(dt.date.today() + dt.timedelta(days = i + 7))
        text1 = convert(date1)
        text2 = convert(date2)
        subject = [sub for sub, value in LESSONS.items() if value['name'] == temp_hw[id]['subject']][0]
        from modules.ruz import table
        if date1.replace('-', '.') in table:
            for time, value in table[date1.replace('-', '.')].items():
                if value['discipline'] == subject:
                    text1 = f'({value["work"][0]})' + '👉 ' + text1
                    break
        if date2.replace('-', '.') in table:
            for time, value in table[date2.replace('-', '.')].items():
                if value['discipline'] == subject:
                    text2 = f'({value["work"][0]})' + '👉 ' + text2
                    break
        button1 = types.InlineKeyboardButton(text=text1, callback_data=f'hwedit,add,date,{id},{date1}')
        button2 = types.InlineKeyboardButton(text=text2, callback_data=f'hwedit,add,date,{id},{date2}')
        keyboard.row(button1, button2)
    return keyboard


@dp.message_handler(commands=['hw'])
async def com_hw(msg):
    if msg.reply_to_message and checkright(msg, 'hw.edit'):
        temp_hw[str(msg.from_user.id)] = {'text': msg.reply_to_message.text}
        keyboard = types.InlineKeyboardMarkup()
        buttons = []
        for subject in HW:
            buttons.append(types.InlineKeyboardButton(text=LESSONS[subject]['name'],
                                                callback_data=f"hwedit,add,subject,{msg.from_user.id},{LESSONS[subject]['name']}"))
        for i in range(len(buttons) // 2):
            keyboard.row(buttons[2 * i], buttons[2 * i + 1])
        if len(buttons) % 2 == 1:
            keyboard.add(buttons[-1])
        button = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hwedit,cancel,{msg.from_user.id}')
        keyboard.add(button)
        text = get_add_text(temp_hw[str(msg.from_user.id)]['text'])
        await msg.answer(text, reply_markup=keyboard)
    elif checkright(msg, 'hw.view'):
        await msg.answer(get_hw(dt.date.today(), dt.date.today() + dt.timedelta(days = 6) - dt.timedelta(days = dt.date.today().weekday())),
                         reply_markup=get_keyboard_hw(dt.date.today(), msg))


def get_keyboard_hw(date=dt.date.today(), msg=None):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='⬅️', callback_data=f'hw,week,{date - dt.timedelta(days=7)}')
    button2 = types.InlineKeyboardButton(text='Текущее', callback_data=f'hw,thisweek,{dt.date.today()}')
    button3 = types.InlineKeyboardButton(text='➡️', callback_data=f'hw,week,{date + dt.timedelta(days=7)}')
    keyboard.row(button1, button2, button3)
    button1 = types.InlineKeyboardButton(text='🔜 Сегодня и завтра', callback_data=f'hw,today')
    if msg and checkright(msg, 'hw.edit', stat_=False):
        button2 = types.InlineKeyboardButton(text='✏️ Управление...', callback_data=f'hwedit,del')
        keyboard.row(button1, button2)
    else:
        keyboard.add(button1)
    return keyboard


def get_week(date):
    start = date - dt.timedelta(days=date.weekday())
    end = start + dt.timedelta(days=6)
    return (start, end)


def get_sign(date):
    sign_this, sign_another, sign_another2, sign_last, sign_today = '🟢', '🟡', '🟠', '🔘', '⚪️'
    date_another = dt.date.today() + dt.timedelta(days=(6 - dt.date.today().weekday()))
    if date == dt.date.today():
        return sign_today
    if date < dt.date.today():
        return sign_last
    if date <= date_another:
        return sign_this
    if date <= date_another + dt.timedelta(days=7):
        return sign_another
    return sign_another2


def get_add_text(text, subject=None, date=None):
    if not subject:
        subject, date = 'выбирается...', '--'
    if not date:
        date = 'выбирается...'
    text = f"✏️ <b>Добавление ДЗ</b>" \
           f"\n\n 📃 <b>Задание</b>: <i>{text}</i>" \
           f"\n 📔 <b>Предмет</b>: <i>{subject}</i>" \
           f"\n 📅 <b>Дата</b>: <i>{date}</i>"
    return text


@dp.callback_query_handler(Text(startswith='hw,'))
async def callback_hw(call):
    if checkright(call, 'hw.view'):
        if call.data.split(',')[1] == 'thisweek':
            date_start = dt.date.fromisoformat(call.data.split(',')[2])
            date_stop = date_start + dt.timedelta(days = 6) - dt.timedelta(days = date_start.weekday())
            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=get_hw(date_start, date_stop), reply_markup=get_keyboard_hw(date_start, call.message))
            except aiogram.utils.exceptions.MessageNotModified:
                await call.answer()
        if call.data.split(',')[1] == 'week':
            date_start, date_stop = get_week(dt.date.fromisoformat(call.data.split(',')[2]))
            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=get_hw(date_start, date_stop), reply_markup=get_keyboard_hw(date_start, call.message))
            except aiogram.utils.exceptions.MessageNotModified:
                await call.answer()
        elif call.data.split(',')[1] == 'today':
            date_start, date_stop = dt.date.today(), dt.date.today() + dt.timedelta(days=1)
            try:
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=get_hw(date_start, date_stop), reply_markup=get_keyboard_hw(date_start, call.message))
            except aiogram.utils.exceptions.MessageNotModified:
                await call.answer()


@dp.callback_query_handler(Text(startswith='hwedit,'))
async def callback_hwedit(call):
    data = call.data.split(',')
    if checkright(call.message, 'hw.edit'):
        if data[1] == 'add':
            if data[2] == 'subject':
                temp_hw[data[3]]['subject'] = data[4]
                keyboard = get_keyboard_dates(0, data[3])
                button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hwedit,cancel,{data[3]}')
                button2 = types.InlineKeyboardButton(text="Другие даты ➡",
                                                     callback_data=f'hwedit,add,date,{data[3]},another,7')
                keyboard.row(button1, button2)
                text = get_add_text(temp_hw[data[3]]['text'], temp_hw[data[3]]['subject'])
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=text, reply_markup=keyboard)
            if data[2] == 'date':
                if 'another' in data:
                    keyboard = get_keyboard_dates(int(data[5]), data[3])
                    button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hwedit,cancel,{data[3]}')
                    button2 = types.InlineKeyboardButton(text="Другие даты ➡",
                                                         callback_data=f'hwedit,add,date,{data[3]},another,{int(data[5]) + 7}')
                    keyboard.row(button1, button2)
                    text = get_add_text(temp_hw[data[3]]['text'], temp_hw[data[3]]['subject'])
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                text=text, reply_markup=keyboard)
                else:
                    date = dt.date.fromisoformat(data[4])
                    id = data[3]
                    subject = [sub for sub, value in LESSONS.items() if value['name'] == temp_hw[id]['subject']][0]
                    HW[subject][str(date)] = temp_hw[id]['text']
                    save_hw()
                    text = get_add_text(temp_hw[id]['text'], temp_hw[id]['subject'], convert_dayhw(date)) + '\n\n💫 Добавлено!'
                    del temp_hw[id]
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                text=text)
        if data[1] == 'del':
            if len(data) < 3:
                keyboard = types.InlineKeyboardMarkup()
                buttons = []
                for subject in HW.keys():
                    if len(HW[subject]) > 0:
                        buttons.append(types.InlineKeyboardButton(text=LESSONS[subject]['name'],
                                                            callback_data=f"hwedit,del,{LESSONS[subject]['name']}"))
                for i in range(len(buttons) // 2):
                    keyboard.row(buttons[2 * i], buttons[2 * i + 1])
                if len(buttons) % 2 == 1:
                    keyboard.add(buttons[-1])
                button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f'hw,thisweek,{dt.date.today()}')
                keyboard.add(button)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="✏️ <b>Удаление ДЗ</b>\n<i>Выберите предмет:</i>", reply_markup=keyboard)
            elif len(data) < 4:
                subject = data[2]
                sub = [sub for sub, value in LESSONS.items() if value['name'] == subject][0]
                keyboard = types.InlineKeyboardMarkup()
                for date in HW[sub]:
                    text = convert(date) + f" ({HW[sub][date][:10]}...)"
                    button = types.InlineKeyboardButton(text=text,
                                                        callback_data=f"hwedit,del,{subject},{date}")
                    keyboard.add(button)
                button = types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f'hw,thisweek,{dt.date.today()}')
                keyboard.add(button)
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"✏️ <b>Удаление ДЗ</b>\n<b>Предмет</b>: <i>{subject}</i>\n"
                                           f"<i>Выберите дату:</i>",
                                      reply_markup=keyboard, parse_mode='HTML')
            else:
                subject, date = data[2], data[3]
                sub = [sub for sub, value in LESSONS.items() if value['name'] == subject][0]
                text = HW[sub][date]
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"✏️ <b>Удаление ДЗ</b>\n<b>Предмет</b>: <i>{subject}</i>\n"
                                           f"<b>Дата</b>: <i>{convert(date)}</i>\n"
                                           f"<b>Задание</b>: <i>{text}</i>"
                                           f"\n🗑 Удалено!",
                                      parse_mode='HTML')
                del HW[sub][date]
                save_hw()
        if data[1] == 'cancel':
            if len(data) > 2 and data[2] in temp_hw:
                del temp_hw[data[2]]
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='Изменение ДЗ отменено 😢')


def get_hw(date_start=dt.date.today(), date_stop=dt.date.today() + dt.timedelta(days=14)):
    result = header(date_start, date_stop)
    while date_start <= date_stop:
        flag = True
        for subject in HW:
            if str(date_start) in HW[subject]:
                if flag:
                    result += f"{get_sign(date_start)} <b>{convert_dayhw(str(date_start))}</b>:\n\n"
                    flag = False
                result += f" 🔹 <b>{LESSONS[subject]['name']}</b> - {HW[subject][str(date_start)]}\n\n"
        date_start += dt.timedelta(days = 1)
    if abs(len(result) - len(header(date_start, date_stop))) < 5:
        result += 'Домашнего задания нет 🥳'
    return result


def clear_hw():
    date_stop = dt.date.today() - dt.timedelta(days = 60)
    to_remove = {}
    for subject in HW:
        for key, value in HW[subject].items():
            if dt.date.fromisoformat(key) <= date_stop:
                to_remove[subject] = key
    for subject, key in to_remove.items():
        del HW[subject][key]


@dp.message_handler(commands=['wk'])
async def com_get_works(msg):
    if checkright(msg):
        await msg.answer(get_works())


def get_works(date_stop = dt.date.today() + dt.timedelta(days=21)):
    date_start = dt.date.today()
    result = header_works(date_start, date_stop)
    while date_start <= date_stop:
        flag = True
        for subject in HW:
            if subject != 'Неопределено':
                for key, value in HW[subject].items():
                    if date_start == dt.date.fromisoformat(key):
                        if '❗' in value:
                            if flag:
                                result += f"{get_sign(date_start)} <b>{convert_dayhw(str(date_start))}</b>:\n\n"
                                flag = False
                            result += f"  <b>{LESSONS[subject]['name']}</b> - {value[value.find('❗'):]}\n\n"
                            break
        date_start += dt.timedelta(days = 1)
    if abs(len(result) - len(header_works(date_start, date_stop))) < 5:
        result += "Работ нет! 😦"
    return result


log.info('Модуль homework загружен')

# HW = {value['name']: {} for lesson, value in json.load(open('files/lessons.txt', 'r', encoding='utf-8')).items()}
# HW['Неопределено'] = {}
#
#
# @dp.message_handler(commands=['wk'])
# async def com_get_works(msg):
#     if checkright(msg):
#         await msg.answer(get_works())
#
#
# @dp.message_handler(commands=['hw', 'hw7', 'hw7next'])
# async def com_get_hw(msg):
#     if checkright(msg):
#         args = arguments(msg.text)
#         date_start, date_stop = dt.date.today(), dt.date.today() + dt.timedelta(days=14)
#         if args['com'] == 'hw':
#             if len(args['args']) > 0:
#                 line = args['arg1'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
#                 try:
#                     date_start = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
#                     date_stop = date_start + dt.timedelta(days = 14)
#                 except:
#                     pass
#             if len(args['args']) > 1:
#                 line = args['arg2'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
#                 try:
#                     date_stop = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
#                 except:
#                     pass
#         elif args['com'] == 'hw7':
#             date_stop = dt.date.today()
#             date_stop = date_stop + dt.timedelta(days=(6 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
#         elif args['com'] == 'hw7next':
#             date_start = date_start + dt.timedelta(days=(7 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
#             date_stop = date_start + dt.timedelta(days=6)
#         await go_hw(msg, date_start, date_stop)
#
#
# @dp.message_handler(commands=['clear'])
# async def com_clear(msg):
#     if checkright(msg):
#         clear_hw()
#         await msg.answer(f"✅ Задания двухнедельной давности отчищены! 💨")
#
#
# @dp.message_handler(commands=['add'])
# async def com_add(msg):
#     if checkright(msg):
#         try:
#             id = str(rnd.randint(1, 10000))
#             add_hw('Неопределено', id, msg.reply_to_message.text)
#             keyboard = types.InlineKeyboardMarkup()
#             for subject in HW.keys():
#                 if subject != 'Неопределено':
#                     button = types.InlineKeyboardButton(text=subject, callback_data=f"hw,{id},{subject}")
#                     keyboard.add(button)
#             button = types.InlineKeyboardButton(text="Другой...", callback_data=f'hw,{id},Неопределено')
#             keyboard.add(button)
#             await msg.answer("👌 Хорошо. Какой предмет?", reply_markup=keyboard)
#         except Exception as err:
#             log.exception('Ошибка добавления задания')
#
#
# @dp.callback_query_handler(Text(startswith='hw,'))
# async def callback_hw(call):
#     if checkright(call, 'hw'):
#         if call.data.split(',')[0] == 'hw':
#             if call.message and call.data.split(',')[1] == 'cancel':
#                 id, subject = call.data.split(',')[2:]
#                 remove_hw('Неопределено', id)
#                 save_hw()
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text="🚫 Заполнения задания отменено 😥")
#             elif call.message and call.data.split(',')[1] == 'another':
#                 id, subject, value = call.data.split(',')[2:]
#                 keyboard = create_keyboard_dates(int(int(value) + 7), subject, id)
#                 button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hw,cancel,{id},{subject}')
#                 button2 = types.InlineKeyboardButton(text="Другие даты ➡",
#                                                      callback_data=f'hw,another,{id},{subject},{int(int(value) + 7)}')
#                 keyboard.row(button1, button2)
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"👍 Отлично, добавляю задание по предмету\n"
#                                            f"<b>{subject}</b>.\n<i>На какое число?</i>",
#                                       reply_markup=keyboard, parse_mode='HTML')
#             elif call.message and call.data.split(',')[1] != '1':
#                 id, subject = call.data.split(',')[1:]
#                 keyboard = create_keyboard_dates(0, subject, id)
#                 button1 = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f'hw,cancel,{id},{subject}')
#                 button2 = types.InlineKeyboardButton(text="Другие даты ➡",
#                                                      callback_data=f'hw,another,{id},{subject},{0}')
#                 keyboard.row(button1, button2)
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"👍 Отлично, добавляю задание по предмету\n"
#                                            f"<b>{subject}</b>.\n<i>На какое число?</i>",
#                                       reply_markup=keyboard, parse_mode='HTML')
#             elif call.message:
#                 id, subject, date = call.data.split(',')[2:]
#                 text = HW['Неопределено'][id]
#                 remove_hw('Неопределено', id)
#                 add_hw(subject, date, text)
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"🌟 Чудесно, по предмету <b>{subject}</b>\n"
#                                            f"на <i>{convert(date)}</i>\n"
#                                            f"добавлено задание: <b>{text}</b>", parse_mode='HTML')
#
#
# @dp.callback_query_handler(Text(startswith='ed,'))
# async def callback_ed(call):
#     if checkright(call, 'edit'):
#         if call.message and call.data.split(',')[0] == 'ed':
#             if len(call.data.split(',')) < 3:
#                 subject = call.data.split(',')[1]
#                 keyboard = types.InlineKeyboardMarkup()
#                 for date in HW[subject]:
#                     button = types.InlineKeyboardButton(text=convert(date) if subject != 'Неопределено' else date,
#                                                         callback_data=f"ed,{subject},{date}")
#                     keyboard.add(button)
#                 button = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f"ed,{subject},cancel")
#                 keyboard.add(button)
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"🔎 Ага, смотрим домашки по предмету <b>{subject}</b>\n"
#                                            f"<i>ДЗ какого числа меняем?</i>", reply_markup=keyboard, parse_mode='HTML')
#             elif call.data.split(',')[2] == 'cancel':
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text="🚫 Отменяем изменения, возвращаю всё на свои места! 😁")
#             else:
#                 subject, date = call.data.split(',')[1], call.data.split(',')[2]
#                 text = HW[subject][date]
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"<code>{text}</code>", parse_mode='HTML')
#
#
# @dp.callback_query_handler(Text(startswith='del,'))
# async def callback_del(call):
#     if call.message and call.data.split(',')[0] == 'del':
#         if checkright(call, 'del'):
#             if len(call.data.split(',')) < 3:
#                 subject = call.data.split(',')[1]
#                 keyboard = types.InlineKeyboardMarkup()
#                 for date in HW[subject]:
#                     button = types.InlineKeyboardButton(text=convert(date) if subject != 'Неопределено' else date,
#                                                         callback_data=f"del,{subject},{date}")
#                     keyboard.add(button)
#                 button = types.InlineKeyboardButton(text="🚫 Отмена", callback_data=f"del,{subject},cancel")
#                 keyboard.add(button)
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"🔎 Ага, смотрим домашки по предмету <b>{subject}</b>\n"
#                                            f"<i>ДЗ какого числа удаляем?</i>",
#                                       reply_markup=keyboard, parse_mode='HTML')
#             elif call.data.split(',')[2] == 'cancel':
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text="Отменяем изменения, ничего не удаляем! 🙃")
#             else:
#                 subject, date = call.data.split(',')[1], call.data.split(',')[2]
#                 text = HW[subject][date]
#                 await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
#                                       text=f"🗑 Удаляем задание по предмету <b>{subject}</b>\n"
#                                            f"На число <b>{convert(date) if subject != 'Неопределено' else date}</b>"
#                                            f"\n<i>{text}</i>",
#                                       parse_mode='HTML')
#                 remove_hw(subject, date)
#                 save_hw()
#
#
# @dp.message_handler(commands=['del'])
# async def com_del(msg):
#     if checkright(msg):
#         keyboard = types.InlineKeyboardMarkup()
#         for subject in HW.keys():
#             if len(HW[subject]) > 0:
#                 button = types.InlineKeyboardButton(text=subject, callback_data=f"del,{subject}")
#                 keyboard.add(button)
#         button = types.InlineKeyboardButton(text="Другой...", callback_data=f'del,Неопределено')
#         keyboard.add(button)
#         await msg.answer("✏ Удаляем задание.\n<i>Какой предмет?</i>", reply_markup=keyboard, parse_mode='HTML')
#
#
# @dp.message_handler(commands=['edit'])
# async def com_edit(msg):
#     if checkright(msg):
#         keyboard = types.InlineKeyboardMarkup()
#         for subject in HW.keys():
#             if len(HW[subject]) > 0:
#                 button = types.InlineKeyboardButton(text=subject, callback_data=f"ed,{subject}")
#                 keyboard.add(button)
#         button = types.InlineKeyboardButton(text="Другой...", callback_data=f'ed,Неопределено')
#         keyboard.add(button)
#         await msg.answer("✏ Круто, изменяем задание!\n<i>Какой предмет?</i>",
#                          reply_markup=keyboard, parse_mode='HTML')
#
#
# async def go_hw(msg, date_start, date_stop):
#     await msg.answer(get_hw(date_start, date_stop), parse_mode='HTML')
#
#
# def update_hw_file():
#     global HW
#     try:
#         with open(HOMEWORK_path, 'r', encoding='utf-8') as f:
#             HW = json.load(f)
#         log.info('ДЗ загружено')
#     except Exception as err:
#         log.exception('Ошибка при загрузке ДЗ')
#
#
# def backup_hw():
#     try:
#         if not os.path.exists(config['PATH']['homework_backup']):
#             os.mkdir(config['PATH']['homework_backup'])
#         file = f"{homework_backup_path}homework_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
#         shutil.copy(HOMEWORK_path, file)
#     except Exception as err:
#         log.exception('Ошибка при бекапе ДЗ')
#
#
# def save_hw():
#     backup_hw()
#     optimize_hw()
#     try:
#         with open(HOMEWORK_path, 'w', encoding='utf-8') as f:
#             json.dump(HW, f, ensure_ascii=False, indent=4)
#         log.info('ДЗ сохранено')
#     except Exception as err:
#         log.exception('Ошибка при сохранении ДЗ')
#
#
# def optimize_hw():
#     for key in HW:
#         HW[key] = dict(sorted(HW[key].items()))
#
#
# def add_hw(subject, date, text):
#     if date == None:
#         date = dt.date.today()
#     HW[subject][str(date)] = text
#     save_hw()
#
#
# def remove_hw(subject, date):
#     try:
#         del HW[subject.capitalize()][date]
#     except Exception as err:
#         log.exception('Ошибка при удалении задания')
#
#
# def clear_hw():
#     date_stop = dt.date.today() - dt.timedelta(days = 14)
#     to_remove = {}
#     for subject in HW:
#         if subject != 'Неопределено':
#             for key, value in HW[subject].items():
#                 if dt.date(int(key[:key.find('-')]), int(key[key.find('-') + 1:key.find('-') + 3]), int(key[key.rfind('-') + 1:])) <= date_stop:
#                     to_remove[subject] = key
#     for subject, key in to_remove.items():
#         del HW[subject][key]
#     save_hw()
#
#
# def get_hw(date_start=dt.date.today(), date_stop=dt.date.today() + dt.timedelta(days=14)):
#     result = header(date_start, date_stop)
#     sign_this, sign_another, sign_another2, sign_last, sign_today = config['UTILITY']['sign_this_weak'],\
#                                              config['UTILITY']['sign_another_weak'],\
#                                              config['UTILITY']['sign_another_weak2'],\
#                                              config['UTILITY']['sign_last_weaks'], \
#                                              config['UTILITY']['sign_today']
#     date_another = dt.date.today()
#     date_another += dt.timedelta(days = 6 - cal.weekday(date_another.year, date_another.month, date_another.day))
#     if len(HW['Неопределено']) > 0:
#         for key, value in HW['Неопределено'].items():
#             result += f"<i>Неопределено, {key}</i> - {value}\n"
#         result += '\n'
#     while date_start <= date_stop:
#         flag = True
#         for subject in HW:
#             if subject != 'Неопределено':
#                 for key, value in HW[subject].items():
#                     if date_start == dt.date.fromisoformat(key):
#                         if flag:
#                             result += f"{sign_today if date_start == dt.date.today() else sign_last if date_start < dt.date.today() else sign_this if date_start <= date_another else sign_another if date_start <= date_another + dt.timedelta(days=7) else sign_another2} " \
#                                       f"<b>{convert_dayhw(str(date_start))}</b>:\n\n"
#                             flag = False
#                         result += f"  <b>{subject}</b> - {value}\n\n"
#                         break
#         date_start += dt.timedelta(days = 1)
#     if abs(len(result) - len(header(date_start, date_stop))) < 5:
#         result += 'Домашнего задания нет 🥳'
#     return result
#
#
# def get_works(date_stop = dt.date.today() + dt.timedelta(days=21)):
#     date_start = dt.date.today()
#     result = header_works(date_start, date_stop)
#     sign_this, sign_another, sign_another2, sign_last, sign_today = config['UTILITY']['sign_this_weak'], \
#                                                                     config['UTILITY']['sign_another_weak'], \
#                                                                     config['UTILITY']['sign_another_weak2'], \
#                                                                     config['UTILITY']['sign_last_weaks'], \
#                                                                     config['UTILITY']['sign_today']
#     date_another = dt.date.today()
#     date_another += dt.timedelta(days=6 - cal.weekday(date_another.year, date_another.month, date_another.day))
#     if len(HW['Неопределено']) > 0:
#         for key, value in HW['Неопределено'].items():
#             if '❗' in value:
#                 result += f"<i>Неопределено</i> - {value[value.find('❗'):]}\n"
#         if abs(len(result) - len(header_works(date_start, date_stop))) < 5:
#             result += '\n'
#     while date_start <= date_stop:
#         flag = True
#         for subject in HW:
#             if subject != 'Неопределено':
#                 for key, value in HW[subject].items():
#                     if date_start == dt.date.fromisoformat(key):
#                         if '❗' in value:
#                             if flag:
#                                 result += f"{sign_today if date_start == dt.date.today() else sign_last if date_start < dt.date.today() else sign_this if date_start <= date_another else sign_another if date_start <= date_another + dt.timedelta(days=7) else sign_another2} " \
#                                           f"<b>{convert_dayhw(str(date_start))}</b>:\n\n"
#                                 flag = False
#                             result += f"  <b>{subject}</b> - {value[value.find('❗'):]}\n\n"
#                             break
#         date_start += dt.timedelta(days = 1)
#     if abs(len(result) - len(header_works(date_start, date_stop))) < 5:
#         result += "Работ нет! 😦"
#     return result
#
#
# log.info('Модуль homework загружен')