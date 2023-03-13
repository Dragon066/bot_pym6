import os.path

from botpackage import *

file_types = {'png': '🌅', 'jpg': '🌅', 'jpeg': '🌅', 'docx': '📘', 'doc': '📘', 'ipynb': '📒', 'py': '🐍',
              'txt': '📝', 'xlsx': '📗', 'csv': '📗', 'pptx': '📙', 'pdf': '📕', 'mp4': '🎞', 'zip': '📚', 'rar': '📚'}

uploading = {}
uploading_dir = {}
FILES = {}

class MDir(StatesGroup):
    dir = State()


def backup_files():
    try:
        if not os.path.exists(config['PATH']['files_backup']):
            os.mkdir(config['PATH']['files_backup'])
        file = f"{files_backup_path}files_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
        shutil.copy(FILES_path, file)
    except Exception as err:
        log.exception('Ошибка при бекапе файлов')


def save_files():
    global FILES
    backup_files()
    try:
        with open(FILES_path, 'w', encoding='utf-8') as f:
            json.dump(FILES, f, ensure_ascii=False, indent=4)
        log.info('Файлы сохранены')
    except Exception as err:
        log.exception('Ошибка при сохранении файлов')


def get_checksum(file):
    if os.path.isfile(file):
        md5h = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5h.update(chunk)
        return md5h.hexdigest()
    return 'isdir'


def update_files():
    global FILES
    dirs = get_all_dirs(MEDIA_path)
    try:
        with open(FILES_path, 'r', encoding='utf-8') as f:
            FILES = json.load(f)
    except Exception as err:
        log.exception('Ошибка при загрузке файлов')
    old_files = FILES
    flag = False
    for dir in dirs:
        if dir not in FILES or FILES[dir]['checksum'] != get_checksum(dir):
            FILES[dir] = {}
            FILES[dir]['hash'] = hashlib.md5(dir.encode()).hexdigest()
            FILES[dir]['id'] = ''
            FILES[dir]['checksum'] = get_checksum(dir)
            flag = True
    for dir in list(FILES.keys()):
        if dir not in dirs:
            del FILES[dir]
    if old_files != FILES or flag:
        save_files()
    log.info('Файлы загружены')


def get_dir(hash):
    for dir in FILES.keys():
        if FILES[dir]['hash'] == hash:
            return dir


def get_all_dirs(dir):
    dirs = []
    dirs.append(dir)
    for file in os.listdir(dir):
        indir = dir + '/' + file
        if os.path.isfile(indir):
            dirs.append(indir)
        if os.path.isdir(indir):
            dirs += get_all_dirs(indir)
    return dirs


def get_keyboard_util(dir, page=0):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='✏ Переименовать файл', callback_data=f"uf,rename,{dir},{page}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='↗ Переместить файл', callback_data=f"uf,move,{dir},{page}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='❌ Удалить файл', callback_data=f"uf,delete,{dir},{page}")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🗂 Создать директорию', callback_data=f"uf,newdir")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Закрыть файловую сессию', callback_data=f"uf,exit")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='⬅ Назад', callback_data=f"uf,back,{dir},{page}")
    keyboard.add(button)
    return keyboard


def get_keyboard_files(dir, page=0):
    keyboard = types.InlineKeyboardMarkup()
    dirs = sorted([dr for dr in os.listdir(dir) if '.' not in dr])
    fils = sorted([file for file in os.listdir(dir) if '.' in file])
    files = dirs + fils
    for file in files[page : page + 7]:
        if file == '_private':
            continue
        ext = file[file.rfind('.') + 1:].lower()
        ext = ext[:ext.find(' ')] if ' ' in ext else ext
        if ext in file_types:
            ext = file_types[ext]
        else:
            ext = '📄'
        text = f"{ext if '.' in file else '🗂'} {file}"
        try:
            button = types.InlineKeyboardButton(text=text, callback_data=f"f,{FILES[dir + '/' + file]['hash']}")
            keyboard.add(button)
        except:
            continue
    if len(files) > 7:
        button1 = types.InlineKeyboardButton(text='➡', callback_data=f"f,{FILES[dir]['hash']},{page + 7}")
        button2 = types.InlineKeyboardButton(text='⬅', callback_data=f"f,{FILES[dir]['hash']},{page - 7}")
        if page > 0 and len(files) - page > 7:
            keyboard.row(button2, button1)
        elif page > 0:
            keyboard.add(button2)
        else:
            keyboard.add(button1)
    if dir[dir.find('/') + 1:dir.find('/') + 9] == '_private' and dir.count('/') == 2:
        button1 = types.InlineKeyboardButton(text='⬅ Выйти из папки', callback_data=f"f,{FILES[MEDIA_path]['hash']}")
    elif '/' in dir:
        button1 = types.InlineKeyboardButton(text='⬅ Выйти из папки', callback_data=f"f,{FILES[dir[:dir.rfind('/')]]['hash']}")
    button2 = types.InlineKeyboardButton(text='Действия...', callback_data=f"uf,list,{FILES[dir]['hash']},{page}")
    if '/' in dir:
        keyboard.row(button1, button2)
    else:
        keyboard.add(button2)
    if dir == MEDIA_path:
        button = types.InlineKeyboardButton(text='🔑 Личная папка', callback_data=f"f,{FILES['media/_private']['hash']}")
        keyboard.add(button)
    return keyboard


def get_keyboard_upload(dir, id):
    keyboard = types.InlineKeyboardMarkup()
    dirs = sorted([dr for dr in os.listdir(dir) if '.' not in dr])
    fils = sorted([file for file in os.listdir(dir) if '.' in file])
    files = dirs + fils
    for file in files:
        if file == '_private':
            continue
        if '.' in file:
            break
        text = f"🗂 {file}"
        button = types.InlineKeyboardButton(text=text, callback_data=f"up,{id},{FILES[dir + '/' + file]['hash']}")
        keyboard.add(button)
    if dir[dir.find('/') + 1:dir.find('/') + 9] == '_private' and dir.count('/') == 2:
        button = types.InlineKeyboardButton(text='⬅ Выйти из папки', callback_data=f"up,{id},{FILES[MEDIA_path]['hash']}")
        keyboard.add(button)
    elif '/' in dir:
        button = types.InlineKeyboardButton(text='⬅ Выйти из папки', callback_data=f"up,{id},{FILES[dir[:dir.rfind('/')]]['hash']}")
        keyboard.add(button)
    button = types.InlineKeyboardButton(text='🗂 Создать новую папку', callback_data=f"up,{id},{FILES[dir]['hash']},cr")
    keyboard.add(button)
    button = types.InlineKeyboardButton(text='✅ Загрузить файл сюда', callback_data=f"up,{id},{FILES[dir]['hash']},go")
    keyboard.add(button)
    if 'media/_private' not in dir:
        button = types.InlineKeyboardButton(text='🔑 Личная папка', callback_data=f"up,{id},{FILES[f'media/_private/{id}']['hash']}")
        keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Отменить загрузку', callback_data=f"up,{id},cancel")
    keyboard.add(button)
    return keyboard


@dp.message_handler(commands=['ls'])
async def com_ls(msg):
    if checkright(msg):
        args = arguments(msg.text)
        dir = f'{"".join(args["args"]) if len(args["args"]) > 0 else "."}'
        await msg.answer(f'🔎 Просматриваю:\n<i>{dir}</i>', reply_markup=get_keyboard_files(dir))


@dp.message_handler(commands=['files'])
async def com_files(msg):
    dir = f'{MEDIA_path}'
    await msg.answer(f'🔎 Просматриваю:\n<i>{dir}</i>', reply_markup=get_keyboard_files(dir))


@dp.callback_query_handler(Text(startswith='f,'))
async def callback_file(call):
    if dt.datetime.now() - dt.timedelta(hours=10) < call.message.date:
        dir = get_dir(call.data.split(',')[1])
        if len(call.data.split(',')) > 2:
            page = int(call.data.split(',')[2])
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f'🔎 Просматриваю:\n<i>{dir}</i>', reply_markup=get_keyboard_files(dir, page))
        else:
            if dir == 'media/_private':
                if not os.path.exists(f'media/_private/{call.from_user.id}'):
                    os.mkdir(f'media/_private/{call.from_user.id}')
                dir += '/' + str(call.from_user.id)
            if os.path.isdir(dir):
                await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text=f'🔎 Просматриваю:\n<i>{dir}</i>', reply_markup=get_keyboard_files(dir))
            if os.path.isfile(dir):
                await call.answer(f'Отправляю {dir[dir.rfind("/") + 1:]}...')
                ext = dir[dir.rfind('.') + 1:].lower()
                capt = None
                if not FILES[dir]['id']:
                    file = open(dir, 'rb')
                else:
                    file = FILES[dir]['id']
                if ext in 'txt':
                    try:
                        with open(dir, 'r', encoding='utf-8') as f:
                            text = f.read()
                            if len(text) < 4096:
                                await call.message.answer(text)
                    except Exception as err:
                        pass
                if ext in 'png, jpg, jpeg':
                    await bot.send_chat_action(call.message.chat.id, types.ChatActions.UPLOAD_PHOTO)
                    new_msg = await call.message.answer_photo(file, caption=capt)
                elif ext in 'mp4':
                    await bot.send_chat_action(call.message.chat.id, types.ChatActions.UPLOAD_VIDEO)
                    new_msg = await call.message.answer_video(file, caption=capt)
                else:
                    await bot.send_chat_action(call.message.chat.id, types.ChatActions.UPLOAD_DOCUMENT)
                    new_msg = await call.message.answer_document(file, caption=capt)
                if not FILES[dir]['id']:
                    FILES[dir]['id'] = new_msg.document.file_id
                    save_files()
    else:
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'К сожалению, эта файловая сессия <b>истекла</b>. 😔\nОткройте новую с помощью /files')


@dp.callback_query_handler(Text(startswith='uf,'))
async def callback_utilfile(call):
    args = call.data.split(',')
    if args[1] == 'list':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=call.message.text, reply_markup=get_keyboard_util(args[2], args[3]))
    if args[1] == 'move':
        await call.answer('В разработке...')
    if args[1] == 'delete':
        await call.answer('В разработке...')
    if args[1] == 'rename':
        await call.answer('В разработке...')
    if args[1] == 'newdir':
        await call.answer('В разработке...')
    if args[1] == 'back':
        dir = get_dir(args[2])
        page = int(args[3])
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'🔎 Просматриваю:\n<i>{dir}</i>', reply_markup=get_keyboard_files(dir, page))
    if args[1] == 'exit':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f'🚫 Файловая сессия закрыта')


def make_dir(dir):
    try:
        os.mkdir(dir)
    except Exception as err:
        log.exception(f'Ошибка создания директории {dir}')
    update_files()


async def upload_file(dir, id):
    file = await bot.get_file(uploading[id]['file_id'])
    name = uploading[id]["file_name"]
    path = f"{dir}/{name}"
    if path in FILES.keys():
        i = 1
        ext = path[path.rfind('.'):]
        part1 = path[:path.find(ext)]
        while f"{part1} ({i}){ext}" in FILES.keys():
            i += 1
        path = f"{part1} ({i}){ext}"
    await bot.download_file(file.file_path, path)
    update_files()
    FILES[path]['id'] = uploading[id]['file_id']


@dp.message_handler(commands=['upload'])
async def com_upload(msg):
    if checkright(msg):
        if msg.reply_to_message and msg.reply_to_message.document:
            uploading[msg.from_user.id] = msg.reply_to_message.document
            await msg.answer(f"🌀 Загружаем файл <b>{uploading[msg.from_user.id]['file_name']}</b>\n<i>{MEDIA_path}</i>",
                             reply_markup=get_keyboard_upload(MEDIA_path, msg.from_user.id))
        else:
            await msg.answer('Ответьте на сообщение с документом, чтобы загрузить его 🤔')


@dp.callback_query_handler(Text(startswith='up,'))
async def callback_upload(call):
    id, action = int(call.data.split(',')[1]), call.data.split(',')[-1]
    if id in uploading.keys():
        if action == 'cancel':
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=f"Загрузка файла <b>{uploading[id]['file_name']}</b> отменена 😔")
            del uploading[id]
        elif action == 'go':
            dir = get_dir(call.data.split(',')[2])
            await upload_file(dir, id)
            text = f'⬇ Файл <b>{uploading[id]["file_name"]}</b> загружен в:\n<i>{dir}</i>'
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=text)
            del uploading[id]
        elif action == 'cr':
            dir = get_dir(call.data.split(',')[2])
            uploading_dir[id] = dir
            await MDir.dir.set()
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text='🌀 Отправь имя папки. /cancel для отмены')
        else:
            dir = get_dir(call.data.split(',')[2])
            text = call.message.text.split('\n')[0]
            text = f"🌀 Загружаем файл <b>{text[text.find('файл') + 5:]}</b>"
            text = f"{text}\n<i>{dir}</i>"
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text=text, reply_markup=get_keyboard_upload(dir, id))
    elif action == 'cancel':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=f"Загрузка файла отменена 😔")


@dp.message_handler(state='*', commands=['cancel'])
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await msg.reply('🚫 Отменено')


@dp.message_handler(state=MDir.dir)
async def state_mdir(msg: types.Message, state: FSMContext):
    if '.' not in msg.text and '/' not in msg.text and '*' not in msg.text:
        await state.finish()
        dir = uploading_dir[msg.from_user.id] + '/' + msg.text
        make_dir(dir)
        await msg.reply(f"🌀 Создана папка: {msg.text}")
        await msg.answer(f"🌀 Загружаем файл <b>{uploading[msg.from_user.id]['file_name']}</b>\n<i>{dir}</i>",
                         reply_markup=get_keyboard_upload(dir, msg.from_user.id))
        del uploading_dir[msg.from_user.id]
    else:
        await msg.reply('❗ Используйте только допустимые символы 😡')


log.info('Модуль files загружен')