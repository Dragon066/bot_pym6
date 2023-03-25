from botpackage import *
from PIL import Image, ImageDraw, ImageFont

DATA = {}
WORDS = {}
try:
    cw_sessions = json.load(open('files/crossword_data/cw_sessions.txt', 'r', encoding='utf-8'))
except Exception as err:
    cw_sessions = {}
    log.exception(f'Ошибка при загрузке сессий кроссвордов')
try:
    STATS = json.load(open('files/crossword_data/STATS.txt', 'r', encoding='utf-8'))
except Exception as err:
    STATS = {}
    log.exception('Ошибка при загрузке статистики кроссвордов')
try:
    TEMPLATES = json.load(open('files/crossword_data/TEMPLATES.txt', 'r', encoding='utf-8'))
except Exception as err:
    TEMPLATES = {}
    log.exception('Ошибка при загрузке образцов кроссворда')
cwheader = '<b>🀄️ <u>CrossWords</u></b>'
word_ending = {0: '', 1: 'о', 2: 'а', 3: 'а', 4: 'а', 5: '', 6: '', 7: '', 8: '', 9: ''}

class GenCW(StatesGroup):
    cw = State()


def field_from_template(template):
    template = '\n'.join([template['field'][i * template['cols'] : i * template['cols'] + template['cols']] for i in range(template['rows'])])
    field = []
    for row in template.split('\n'):
        field.append(list(row.strip()))
    return field


async def generate_crossword(field, attempts = 1000):
    while attempts:
        try:
            return gen(field)
        except Exception as ex:
            attempts -= 1
        await asyncio.sleep(0.0001)
    return None, None


def gen(field):
    # rows
    new_field = []
    meta_data = {}
    current_num = 1
    for i, row in enumerate(field):
        row = ''.join(row)
        s = re.search(r'[^#]{2,}', row)
        new_row = row
        while s:
            word = s.group().replace('*', '.')
            new_word = find_word(word).lower()
            if new_word not in meta_data.keys():
                meta_data[new_word] = {}
                meta_data[new_word]['num'] = current_num
                current_num += 1
                meta_data[new_word]['start'] = (i, s.span()[0])
                meta_data[new_word]['end'] = (i, s.span()[1] - 1)
                question = WORDS[str(len(word))][new_word][rnd.randint(0, len(WORDS[str(len(word))][new_word]) - 1)]
                meta_data[new_word]['question'] = question
                meta_data[new_word]['direction'] = 'horizontal'
                meta_data[new_word]['answered'] = False
                meta_data[new_word]['answered_by'] = None
            else:
                raise
            new_row = new_row[:s.span()[0]] + new_word + new_row[s.span()[1]:]
            row = row[:s.span()[0]] + '#' * len(s.group()) + row[s.span()[1]:]
            s = re.search(r'[^#]{2,}', row)
        new_field.append(list(new_row))
    # columns
    for column in range(len(new_field[0])):
        column_old = ''
        for row in range(len(new_field)):
            column_old += new_field[row][column]
        s = re.search(r'[^#]{2,}', column_old)
        new_column = column_old
        while s:
            word = s.group().replace('*', '.')
            new_word = find_word(word).lower()
            if new_word not in meta_data.keys():
                meta_data[new_word] = {}
                meta_data[new_word]['num'] = current_num
                current_num += 1
                meta_data[new_word]['start'] = (s.span()[0], column)
                meta_data[new_word]['end'] = (s.span()[1] - 1, column)
                question = WORDS[str(len(word))][new_word][rnd.randint(0, len(WORDS[str(len(word))][new_word]) - 1)]
                meta_data[new_word]['question'] = question
                meta_data[new_word]['direction'] = 'vertical'
                meta_data[new_word]['answered'] = False
                meta_data[new_word]['answered_by'] = None
            else:
                raise
            new_column = new_column[:s.span()[0]] + new_word + new_column[s.span()[1]:]
            column_old = column_old[:s.span()[0]] + '#' * len(s.group()) + column_old[s.span()[1]:]
            s = re.search(r'[^#]{2,}', column_old)
        for row in range(len(new_field)):
            new_field[row][column] = new_column[row]
    return {'field': to_raw_text(field), 'rows': len(field), 'columns': len(field[0])}, meta_data


def find_word(pattern):
    lst = list(WORDS[str(len(pattern))].keys())
    lst_ok = []
    for word in lst:
        if re.fullmatch(pattern, word):
            lst_ok.append(word)
    return lst_ok[rnd.randint(0, len(lst_ok) - 1)]


def to_raw_text(field):
    result = ""
    for row in field:
        result+= ''.join(row)
    return result


def get_all_questions(data):
    vertical, horizontal = [], []
    for key, word in data.items():
        temp = f"<b>{word['num']}.</b> {word['question']} <i>({len(key)})</i>"
        if word['answered']:
            temp = f"<strike>{temp}</strike>"
        if word['direction'] == 'horizontal':
            horizontal.append(temp)
        else:
            vertical.append(temp)
    vertical = '\n'.join(sorted(vertical, key=lambda s: s[:s.find('.')].isdigit()))
    horizontal = '\n'.join(sorted(horizontal, key=lambda s: s[:s.find('.')].isdigit()))
    if len(horizontal) == 0:
        horizontal = 'Отсутсвует :('
    if len(vertical) == 0:
        vertical = 'Отсутсвует :('
    result = f"<i>По горизонтали:</i>\n{horizontal}\n\n<i>По вертикали:</i>\n{vertical}"
    return result


def open_words():
    global WORDS
    if not WORDS:
        with open('files/crossword_data/words.txt', 'r', encoding='utf-8') as f:
            WORDS = json.load(f)


def save_cw_sessions():
    global cw_sessions
    with open('files/crossword_data/cw_sessions.txt', 'w', encoding='utf-8') as f:
        json.dump(cw_sessions, f, ensure_ascii=False, indent=4)


def save_stats():
    global STATS
    with open('files/crossword_data/STATS.txt', 'w', encoding='utf-8') as f:
        json.dump(STATS, f, ensure_ascii=False, indent=4)


async def get_stat(id):
    if id not in STATS.keys():
        STATS[id] = {}
        STATS[id]['total'] = 0
        user = await bot.get_chat(int(id))
        STATS[id]['name'] = user.first_name
    text = f'{cwheader} <b>Stats</b>\n\n<b>{STATS[id]["name"]}</b>\n📍 Правильно данных ответов: <b>{STATS[id]["total"]}</b>'
    return text


def get_cw_top():
    result = {v['name']: v['total'] for id, v in STATS.items() if id != str(bot_id)}
    result = dict(sorted(list(result.items()), key=lambda x: x[1], reverse=True))
    text = f'{cwheader} <b>Top</b>\n\n'
    symbs = {1: '🥇', 2: '🥈', 3: '🥉'}
    count = 1
    for name, total in list(result.items())[:10]:
        text += f"{f'  {count}' if count not in symbs else symbs[count]}{'. ' if count not in symbs else ''} <b>{name}</b> — {total}\n"
        count += 1
    return text


def display_cw(field):
    result = ''
    rows = field['rows']
    try:
        cols = field['columns']
    except:
        cols = field['cols']
    for row in range(rows):
        result += ' '.join(field['field'][row * cols : row * cols + cols]) + '\n'
    return f"<code>{result}</code>"


def display_cw_img(field, data):
    rows = field['rows']
    cols = field['columns']
    field = field['field']
    layer = Image.new('RGBA', (100 * cols + 20 + 2 * cols, 100 * rows + 20 + 2 * rows), 'lightblue')
    draw = ImageDraw.Draw(layer)
    for col in range(cols):
        for row in range(rows):
            color = 'grey' if field[row * cols + col] == '#' else 'white'
            draw.rectangle((10 + col * 102, 10 + row * 102, 110 + col * 102, 110 + row * 102), fill=color)
            if field[row * cols + col] not in '*#':
                draw.text((10 + col * 102 + 28, 10 + row * 102 + 11), field[row * cols + col],
                          font=ImageFont.truetype('/usr/share/fonts/consolas/YaHei.Consolas.1.12.ttf', size=80), fill='black')
    for word, value in data.items():
        start = value['start']
        assign = 86 if value['direction'] == 'vertical' else 0
        if value['num'] // 10 > 0 and assign:
            assign -= 12
        draw.text((12 + start[1] * 102 + assign, 12 + start[0] * 102), str(value['num']),
                  font=ImageFont.truetype('/usr/share/fonts/consolas/YaHei.Consolas.1.12.ttf', size=20), fill='black')
    img = BytesIO()
    layer.save(img, 'PNG')
    img.seek(0)
    return img


def cw_checkfinish(id):
    for word in cw_sessions[id]['meta_data']:
        if not cw_sessions[id]['meta_data'][word]['answered']:
            return False
    return True


def get_cwutil_keyboard(id):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='🔮 Получить подсказку', callback_data=f"cw,tip,{id}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='✏ Завершить кроссворд', callback_data=f"cw,end,{id}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='❌ Удалить кроссворд', callback_data=f"cw,del,{id}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Закрыть меню', callback_data=f"cw,close")
    keyboard.add(button)
    return keyboard


def get_tip_keyboard(id, page):
    keyboard = types.InlineKeyboardMarkup()
    page = int(page)
    total = []
    for word, data in cw_sessions[id]['meta_data'].items():
        if not data['answered']:
            total.append((word, data['num'], data['question']))
    mx = page + 5 if page + 5 <= len(total) else len(total)
    for item in total[page:mx]:
        text = f"{item[1]} ({item[2][:15]}...)"
        button = types.InlineKeyboardButton(text=text, callback_data=f"cw,tip_go,{id},{item[0]}")
        keyboard.add(button)
    if len(total) > 5:
        button1 = types.InlineKeyboardButton(text='➡', callback_data=f"cw,tip_page,{id},{page + 5}")
        button2 = types.InlineKeyboardButton(text='⬅', callback_data=f"cw,tip_page,{id},{page - 5}")
        if page > 0 and len(total) - page > 5:
            keyboard.row(button2, button1)
        elif page > 0:
            keyboard.add(button2)
        else:
            keyboard.add(button1)
    button = types.InlineKeyboardButton(text='⬅ Назад', callback_data=f"cw,util,{id}")
    keyboard.add(button)
    return keyboard


def get_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='🎲 Cлучайный кроссворд', callback_data=f"cw,random")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='📂 Сгенерировать по образцу', callback_data=f"cw,gen,{None},0")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='❔ Как играть', callback_data=f"cw,help")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🌟 Топ', callback_data=f"cw,top")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='📊 Ваша статистика', callback_data=f"cw,stat")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🀄️ О CrossWords', callback_data=f"cw,info")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Закрыть', callback_data=f"cw,close")
    keyboard.add(button)
    return keyboard


def get_tryagain_keyboard(category, field):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='✏ Попробовать ещё раз', callback_data=f"cw,gen_go,{category},{field}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Закрыть', callback_data=f"cw,close")
    keyboard.add(button)
    return keyboard


def get_gen_keyboard(category, page):
    keyboard = types.InlineKeyboardMarkup()
    page = int(page)
    if category != 'None':
        mx = page + 5 if page + 5 <= len(TEMPLATES[category]) else len(TEMPLATES[category])
        for key, value in list(TEMPLATES[category].items())[page:mx]:
            ending = word_ending[value['words']['total'] % 10] if not 10 < value['words']['total'] % 100 < 20 else ''
            text = f"{key} ({value['rows']}x{value['cols']}, {value['words']['total']} слов{ending})"
            button = types.InlineKeyboardButton(text=text, callback_data=f"cw,gen_go,{category},{key}")
            keyboard.add(button)
        if len(TEMPLATES[category]) > 5:
            button1 = types.InlineKeyboardButton(text='➡', callback_data=f"cw,gen,{category},{page + 5}")
            button2 = types.InlineKeyboardButton(text='⬅', callback_data=f"cw,gen,{category},{page - 5}")
            if page > 0 and len(TEMPLATES[category]) - page > 5:
                keyboard.row(button2, button1)
            elif page > 0:
                keyboard.add(button2)
            else:
                keyboard.add(button1)
        button = types.InlineKeyboardButton(text='⬅ Назад', callback_data=f"cw,gen,{None},0")
        keyboard.add(button)
    else:
        for key, value in TEMPLATES.items():
            text = f"🗂 {key}"
            button = types.InlineKeyboardButton(text=text, callback_data=f"cw,gen,{key},0")
            keyboard.add(button)
        button = types.InlineKeyboardButton(text='✏ Создать по образцу', callback_data=f"cw,gen_own")
        keyboard.add(button)
        button = types.InlineKeyboardButton(text='⬅ Назад', callback_data=f"cw,menu")
        keyboard.add(button)
    return keyboard


async def cw_get_statistics(id):
    result = {}
    for word, data in cw_sessions[id]['meta_data'].items():
        if data['answered_by'] in result.keys():
            result[data['answered_by']] += 1
        else:
            result[data['answered_by']] = 1
    result = dict(sorted(list(result.items()), key=lambda d: d[1]))
    text = "Количество верно данных ответов:\n"
    for id, num in result.items():
        user = await bot.get_chat(id)
        if str(id) not in STATS.keys():
            STATS[str(id)] = {}
            STATS[str(id)]['total'] = 0
        STATS[str(id)]['name'] = user.first_name
        STATS[str(id)]['total'] += num
        text += f"<b>{user.first_name}</b> — {num}\n"
    save_stats()
    return text


def cw_ans(id, ans):
    global cw_sessions
    rows = cw_sessions[id]['field']['rows']
    cols = cw_sessions[id]['field']['columns']
    start = cw_sessions[id]['meta_data'][ans]['start']
    end = cw_sessions[id]['meta_data'][ans]['end']
    field = cw_sessions[id]['field']['field']
    if cw_sessions[id]['meta_data'][ans]['direction'] == 'horizontal':
        cw_sessions[id]['field']['field'] = field[:start[0] * cols + start[1]] + ans + field[start[0] * cols + start[1] + len(ans):]
    else:
        for i in range(len(ans)):
            field = field[:(i + start[0]) * cols + start[1]] + ans[i] + field[(i + start[0]) * cols + start[1] + 1:]
        cw_sessions[id]['field']['field'] = field
    cw_sessions[id]['meta_data'][ans]['answered'] = True


@dp.callback_query_handler(Text(startswith='cw,'))
async def callback_cw(call):
    global cw_sessions
    action = call.data.split(',')[1]
    if action == 'menu':
        await bot.edit_message_text(f'{cwheader}', chat_id=call.message.chat.id,
                                    message_id=call.message.message_id, reply_markup=get_menu_keyboard())
    if action == 'random':
        open_words()
        total = []
        for cat, templ in TEMPLATES.items():
            for field, value in templ.items():
                total.append((cat, (field, value)))
        rand = rnd.randint(0, len(total) - 1)
        gen_msg = await bot.edit_message_text(f'{cwheader}\n<i>Создаю кроссворд...</i>\n<span class="tg-spoiler">Категория: {total[rand][0]}</span>',
                                              chat_id=call.message.chat.id, message_id=call.message.message_id)
        field, meta_data = await generate_crossword(field_from_template(total[rand][1][1]))
        if field:
            await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
            msg_quest = await call.message.answer(get_all_questions(meta_data))
            msg_cw = await bot.send_photo(chat_id=call.message.chat.id, photo=display_cw_img(field, meta_data))
            cw_sessions[str(msg_cw.message_id)] = {'msg_quest': msg_quest.message_id, 'meta_data': meta_data,
                                                   'field': field}
            save_cw_sessions()
        else:
            await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                text=f"{cwheader}\nК сожалению, не удалось создать кроссворд по данному образцу:\n{display_cw(total[rand][1][1])}"
                f"\nВозможно, стоит попробовать другой?", reply_markup=get_tryagain_keyboard(total[rand][0], total[rand][1][0]))
    if action == 'gen':
        category, page = call.data.split(',')[2], call.data.split(',')[3]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{cwheader} <b>Create</b>', reply_markup=get_gen_keyboard(category, page))
    if action == 'gen_own':
        await GenCW.cw.set()
        text = f"{cwheader}\nОтправьте прямоугольный образец, состоящий из # (блок) и * (пустая клетка)\n\n" \
               f"Например,\n<code>****\n*##*\n*##*\n****</code>\n\n/cancel для отмены"
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text)
    if action == 'gen_go':
        open_words()
        category, key = call.data.split(',')[2], call.data.split(',')[3]
        gen_msg = await bot.edit_message_text(
            f'{cwheader}\n<i>Создаю кроссворд...</i>\n<span class="tg-spoiler">Категория: {category}</span>',
            chat_id=call.message.chat.id, message_id=call.message.message_id)
        field, meta_data = await generate_crossword(field_from_template(TEMPLATES[category][key]))
        if field:
            await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
            msg_quest = await call.message.answer(get_all_questions(meta_data))
            msg_cw = await bot.send_photo(chat_id=call.message.chat.id, photo=display_cw_img(field, meta_data))
            cw_sessions[str(msg_cw.message_id)] = {'msg_quest': msg_quest.message_id, 'meta_data': meta_data,
                                                   'field': field}
            save_cw_sessions()
        else:
            await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                                        text=f"{cwheader}\nК сожалению, не удалось создать кроссворд по данному образцу:\n{display_cw(TEMPLATES[category][key])}"
                                             f"\nВозможно, стоит попробовать другой?",
                                        reply_markup=get_tryagain_keyboard(category, key))
    if action == 'top':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=get_cw_top())
    if action == 'stat':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=await get_stat(str(call['from']['id'])))
    if action == 'info':
        await call.answer('Пару секунд, подсчитываю...')
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=get_info())
    if action == 'help':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=get_help())
    if action == 'tip':
        id = call.data.split(',')[2]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{cwheader} <b>Tip</b>\n<i>Выберите номер вопроса</i>:', reply_markup=get_tip_keyboard(id, 0))
    if action == 'tip_page':
        id, page = call.data.split(',')[2], call.data.split(',')[3]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{cwheader} <b>Tip</b>\n<i>Выберите номер вопроса</i>:', reply_markup=get_tip_keyboard(id, page))
    if action == 'tip_go':
        open_words()
        keyboard = types.InlineKeyboardMarkup()
        id, word = call.data.split(',')[2], call.data.split(',')[3]
        if len(WORDS[str(len(word))][word]) > 1:
            button = types.InlineKeyboardButton(text='🔅 Другая формулировка', callback_data=f"cw,tip1,{id},{word}")
            keyboard.add(button)
        button = types.InlineKeyboardButton(text='🔅 Показать некоторые буквы', callback_data=f"cw,tip2,{id},{word}")
        keyboard.add(button)
        button = types.InlineKeyboardButton(text='🔅 Отгадать слово', callback_data=f"cw,tip3,{id},{word}")
        keyboard.add(button)
        button = types.InlineKeyboardButton(text='⬅ Назад', callback_data=f"cw,tip,{id}")
        keyboard.add(button)
        text = f'{cwheader} <b>Tip</b>\nПодсказка для вопроса: ' \
               f'{cw_sessions[id]["meta_data"][word]["num"]}. <i>{cw_sessions[id]["meta_data"][word]["question"]}</i>'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text,
                                    reply_markup=keyboard)
    if action == 'tip1':
        id, word = call.data.split(',')[2], call.data.split(',')[3]
        for quest in WORDS[str(len(word))][word]:
            if quest != cw_sessions[id]['meta_data'][word]['question']:
                break
        text = f"{cwheader} <b>Tip</b>\nИная формулировка для номера {cw_sessions[id]['meta_data'][word]['num']}:" \
               f"\n\n<code>{quest}</code>"
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text)
    if action == 'tip2':
        id, word = call.data.split(',')[2], call.data.split(',')[3]
        to_show = []
        for i in range(len(word) // 3 + (len(word) % 3 > 0)):
            letter = rnd.randint(0, len(word) - 1)
            while letter in to_show:
                letter = rnd.randint(0, len(word) - 1)
            to_show.append(letter)
        new_word = word
        for i in range(len(new_word)):
            if i not in to_show:
                new_word = new_word[:i] + '_' + new_word[i + 1:]
        text = f"{cwheader} <b>Tip</b>\nПодсказка для вопроса №{cw_sessions[id]['meta_data'][word]['num']}:\n\n<code>{new_word}</code>"
        cw_sessions[id]['meta_data'][word]['answered_by'] = bot_id
        save_cw_sessions()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text)
    if action == 'tip3':
        id, word = call.data.split(',')[2], call.data.split(',')[3]
        cw_sessions[id]['meta_data'][word]['answered_by'] = bot_id
        save_cw_sessions()
        text = f"{cwheader} <b>Tip</b>\nПодсказка для вопроса №{cw_sessions[id]['meta_data'][word]['num']}:\n\n<code>{word}</code>"
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text)
    if action == 'util':
        id = call.data.split(',')[2]
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'{cwheader}', reply_markup=get_cwutil_keyboard(id))
    if action == 'end':
        id = call.data.split(',')[2]
        await bot.send_message(chat_id=call.message.chat.id, text=get_all_questions(cw_sessions[id]['meta_data']))
        for ans in cw_sessions[id]['meta_data']:
            if not cw_sessions[id]['meta_data'][ans]['answered']:
                cw_ans(id, ans)
                cw_sessions[id]['meta_data'][ans]['answered_by'] = bot_id
        await bot.delete_message(chat_id=call.message.chat.id, message_id=cw_sessions[id]['msg_quest'])
        await bot.delete_message(chat_id=call.message.chat.id, message_id=int(id))
        await bot.send_photo(photo=display_cw_img(cw_sessions[id]['field'], cw_sessions[id]['meta_data']),
                                     chat_id=call.message.chat.id)
        text = await cw_get_statistics(id)
        await call.message.answer(f'{cwheader}\nВы завершили кроссворд, мяу! 💫\n\n{text}')
        del cw_sessions[id]
        save_cw_sessions()
    if action == 'del':
        id = call.data.split(',')[2]
        await bot.delete_message(chat_id=call.message.chat.id, message_id=cw_sessions[id]['msg_quest'])
        await bot.delete_message(chat_id=call.message.chat.id, message_id=int(id))
        del cw_sessions[id]
        save_cw_sessions()
        await call.answer('Кроссворд удалён :(')
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    if action == 'close':
        await call.answer('Окно закрыто')
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@dp.message_handler(state=GenCW.cw)
async def state_mdir(msg: types.Message, state: FSMContext):
    if not msg.text.replace('*', '').replace('#', '').replace('\n', ''):
        rows = msg.text.count('\n') + 1 if '\n' in msg.text else 1
        cols = len(msg.text[:msg.text.find('\n')])
        if rows > 1:
            for row in msg.text.split('\n'):
                if len(row) != cols:
                    await msg.reply(f'{cwheader}\nПредложенное поле не имеет прямоугольный вид\n/cancel для отмены')
                    return False
        await state.finish()
        open_words()
        gen_msg = await msg.answer(f'{cwheader}\nСоздаю кроссворд по вашему образцу...')
        text = msg.text.replace('\n', '')
        template = {
            "field": f"{text}",
            "rows": rows,
            "cols": cols, }
        field, meta_data = await generate_crossword(field_from_template(template))
        if field:
            await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
            msg_quest = await msg.answer(get_all_questions(meta_data))
            msg_cw = await bot.send_photo(chat_id=msg.chat.id, photo=display_cw_img(field, meta_data))
            cw_sessions[str(msg_cw.message_id)] = {'msg_quest': msg_quest.message_id, 'meta_data': meta_data,
                                                   'field': field}
            save_cw_sessions()
        else:
            await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                                        text=f"{cwheader}\nК сожалению, не удалось создать кроссворд по данному образцу:\n{display_cw(template)}"
                                             f"\nВозможно, стоит попробовать другой?")
    else:
        await msg.reply(f'{cwheader}\nПоле содержит недоступные символы\n/cancel для отмены')


@dp.message_handler(commands=['crossword', 'cw'])
async def com_cw(msg):
    global cw_sessions
    if checkright(msg):
        try:
            id = str(msg.reply_to_message.message_id)
        except Exception as ex:
            id = msg.message_id
        if msg.reply_to_message and id in cw_sessions.keys()  or int(id) in [cw_sessions[key]['msg_quest'] for key in cw_sessions.keys()]:
            if id not in cw_sessions.keys():
                for key, value in cw_sessions.items():
                    if value['msg_quest'] == int(id):
                        id = key
                        break
            await msg.answer(f'{cwheader}', reply_markup=get_cwutil_keyboard(id))
        else:
            await msg.answer(f'{cwheader}', reply_markup=get_menu_keyboard())


@dp.message_handler(lambda msg: msg.reply_to_message and msg.text[0] != '/')
async def answer_to_cw(msg):
    global cw_sessions
    id = str(msg.reply_to_message.message_id)
    if id in cw_sessions.keys() or int(id) in [cw_sessions[key]['msg_quest'] for key in cw_sessions.keys()]:
        if id not in cw_sessions.keys():
            for key, value in cw_sessions.items():
                if value['msg_quest'] == int(id):
                    id = key
                    break
        try:
            if len(msg.text.split(' ')) > 1:
                num, ans = msg.text.split(' ')[0], msg.text.split(' ')[1].lower()
            else:
                ans = msg.text.split(' ')[0].lower()
            if ans in cw_sessions[id]['meta_data']:
                if not cw_sessions[id]['meta_data'][ans]['answered']:
                    cw_ans(id, ans)
                    await bot.delete_message(chat_id=msg.chat.id, message_id=int(id))
                    await bot.delete_message(chat_id=msg.chat.id, message_id=cw_sessions[id]['msg_quest'])
                    msg_quest = await msg.answer(get_all_questions(cw_sessions[id]['meta_data']))
                    msg_cw = await msg.answer_photo(display_cw_img(cw_sessions[id]['field'], cw_sessions[id]['meta_data']))
                    if not cw_sessions[id]['meta_data'][ans]['answered_by']:
                        cw_sessions[id]['meta_data'][ans]['answered_by'] = msg.from_user.id
                    if not cw_checkfinish(id):
                        cw_sessions[str(msg_cw.message_id)] = {'msg_quest': msg_quest.message_id,
                                                               'meta_data': cw_sessions[id]['meta_data'],
                                                               'field': cw_sessions[id]['field']}
                        del cw_sessions[id]
                    else:
                        text = await cw_get_statistics(id)
                        await msg.answer(f'{cwheader}\nВы завершили кроссворд, мяу! 💫\n\n{text}')
                        del cw_sessions[id]
                    save_cw_sessions()
        except Exception as ex:
            pass


def get_info():
    text = f'{cwheader} <b>About</b>\n\n'
    with open("files/crossword_data/RAW_DATA.txt", "r", encoding="utf-8") as f:
        amount = '{0:,}'.format(len(json.load(f))).replace(',', '.')
        text += f'Всего в базе данных: <b>{amount}' \
                f'</b> элементов вида "вопрос — ответ"\n'
    with open("files/crossword_data/data.txt", "r", encoding="utf-8") as f:
        amount = '{0:,}'.format(len(json.load(f))).replace(',', '.')
        text += f'Из них <b>{amount}</b> ' \
                f'пригодны для использования в русских кроссвордах\n'
    open_words()
    all_len = 0
    mx = 0
    for key, value in WORDS.items():
        all_len += len(value)
        for inkey, invalue in value.items():
            if mx < len(invalue):
                mx = len(invalue)
    all_len = amount = '{0:,}'.format(all_len).replace(',', '.')
    text += f'В базе данных <b>{all_len}</b> уникальных слов для составления незабываемых кроссвордов!\n\n'
    text += f'Это интересно 🧐\n'
    text += f'📌 На генерацию кроссворда уходит вплоть до <b>1.000</b> попыток! 😱\n'
    text += f'📌 Подсказка <b>"Другая формулировка"</b>, в отличие от остальных, не отнимает у вас возможность улучшить свою статистику 😌\n'
    text += f'📌 <b>{mx}</b> — именно такое наибольшее количество вопросов для одного лишь слова! 😦'
    return text


def get_help():
    result = f"{cwheader} <b>How to play</b>\n\n\n"
    result += f"""📂 <b><u>Создание кроссворда</u></b>
    
Для создания кроссворда воспользуйтесь кнопками из главного меню:

'🎲 <b>Случайный кроссворд</b>' — создаёт кроссворд из случайно выбранного образца.

'📂 <b>Сгенерировать по образцу</b>' — в отличие от случайного создания, создаёт кроссворд по конкретному образцу. Формат имени такого образца - <i>название (длинаXширина, кол-во слов)</i>.
- '✏ <b>Создать по образцу</b>' — генерирует кроссворд по вашему образцу - для этого необходимо нажать кнопку и прислать текстовый образец согласно приведённому примеру. Используйте /cancel для отмены этой операции.

❗ Для создания больших кроссвордов может потребоваться некоторое время и даже несколько попыток.


✏ <b><u>Решение кроссворда</u></b>

Для внесения своего ответа в поле кроссворда, достаточно <u>ОТВЕТИТЬ</u> на сообщение с кроссвордом (или списком вопросов) сообщением вида
'<i>номер_вопроса ответ</i>' или '<i>ответ</i>'.
Например, '<i>4 изба</i>' или '<i>изба</i>'.

Кроссворд <i>завершится</i>, когда все поля будут заполнены.

Для получения дополнительных опций конкретного кроссворда, необходимо <u>ОТВЕТИТЬ</u> на сообщение с кроссвордом (или списком вопросов) командой <b>/cw</b>.

С помощью такого дополнительного меню можно:

- '🔮 <b>Получить подсказку</b>' (виды подсказок рассмотрены в блоке ниже)

- '✏ <b>Завершить кроссворд</b>' — автоматически заполнить все пустые поля и, тем самым, <i>завершить</i> решение кроссворда. Заполненные таким образом вопросы в вашу статистику не попадут, однако все ранее данные ответы будут учтены.

- '❌ <b>Удалить кроссворд</b>' — удаляет созданный кроссворд. В отличие от предыдущей функции, все ранее данные ответы в статистику не будут учтены.


📊 <b><u>Статистика</u></b>

Система ведёт автоматическую статистику, представляющая собой количество правильно данных ответов.

Эта статистика обновляется <u>только после <i>завершения</i> кроссворда полностью</u>.

При использовании некоторых подсказок, данный после них ответ в статистику не учитывается.

Для просмотра статистики используйте кнопки в главном меню:

'📊 <b>Ваша статистика</b>' — выведет только собственную статистику.

'🌟 <b>Топ</b>' — выведет первых 10 игроков, лидирующих по количеству верно данных ответов.


🔮 <b><u>Подсказки</u></b>

Подсказки для данного кроссворда можно получить с помощью дополнительного меню, полученного с помощью <u>ОТВЕТА</u> на сообщение с кроссвордом (или списком вопросов) командой <b>/cw</b>.

При нажатии на '🔮 <b>Получить подсказку</b>' на выбор даётся список нерешённых вопросов.

После выбора вопроса, можно получить на него одну из трёх подсказок:

- '🔅 <b>Другая формулировка</b> — выведет иной вопрос для того же слова, что загадано. Эта подсказка доступна не всегда в силу ограниченности вопросов на некоторые слова. В отличие от остальных подсказок, после использования этой подсказки у вас <u>остаётся</u> возможность ответить на данный вопрос с последующем занесением его в статистику.

- '🔅 <b>Показать некоторые буквы</b> — показывает ~30% букв слова (не учитывая те, что уже отгаданы). После использования данной подсказки данный вопрос будет считаться как отвеченный системой и в вашу статистку он не пойдёт.

- '🔅 <b>Отгадать слово</b> — показывает загаданное слово. После использования данной подсказки данный вопрос будет считаться как отвеченный системой и в вашу статистку он не пойдёт.
"""
    return result


log.info('Модуль crosswords загружен')