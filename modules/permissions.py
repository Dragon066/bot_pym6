from botpackage import *

USERS = {}
fields = ['name', 'names', 'id', 'group', 'perms', 'gender', 'rep', 'rep_time']
gender = {'man': {
    'postfix': '',
    'him': 'его',
    'delete': 'удалён',
    'add': 'добавлен'
},
'woman': {
    'postfix': 'а',
    'him': 'её',
    'delete': 'удалена',
    'add': 'добавлена'
}}


def get_gender(id, string):
    return gender[USERS[id]["gender"]][string]


def update_users():
    global USERS
    try:
        with open(USERS_path, 'r', encoding='utf-8') as f:
            USERS = json.load(f)
        USERS = {int(k): v for k, v in USERS.items()}
        for key, user in USERS.items():
            user['id'] = int(user['id'])
        log.info('Пользователи загружены')
    except Exception as err:
        log.exception('Ошибка при загрузке пользователей')


def backup_users():
    try:
        if not os.path.exists(config['PATH']['users_backup']):
            os.mkdir(config['PATH']['users_backup'])
        file = f"{users_backup_path}users_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
        shutil.copy(USERS_path, file)
    except Exception as err:
        log.exception('Ошибка при бекапе пользователей')


def save_users():
    global USERS
    backup_users()
    try:
        with open(USERS_path, 'w', encoding='utf-8') as f:
            json.dump(USERS, f, ensure_ascii=False, indent=4)
        log.info('Пользователи сохранены')
    except Exception as err:
        log.exception('Ошибка при сохранении пользователей')


def checkright(msg, right='-', stat_=True):
    id, right = msg.from_user.id, arguments(msg.text)['com'] if right == '-' else right
    from modules.statistics import stat
    try:
        for r in user_rights(id).split(', '):
            try:
                if re.fullmatch(r, right):
                    if stat_:
                        stat(right)
                    return True
            except Exception as error:
                continue
    except Exception as err:
        log.exception('Ошибка при проверке права')
    if right in user_rights(id):
        if stat_:
            stat(right)
        return True
    return False


def create_user(user):
    USERS[user.id] = {}
    USERS[user.id]['name'] = user.first_name
    USERS[user.id]['names'] = user.first_name
    USERS[user.id]['id'] = user.id
    USERS[user.id]['group'] = 'basic'
    USERS[user.id]['perms'] = ''
    USERS[user.id]['gender'] = 'man'
    USERS[user.id]['rep'] = '0'
    USERS[user.id]['emoji'] = '◻'
    save_users()


@dp.message_handler(commands=['admin'])
async def com_admin(msg):
    if msg.reply_to_message and checkright(msg) and msg.from_user.id != msg.reply_to_message.from_user.id:
        id = msg.reply_to_message.from_user.id
        user = await bot.get_chat(id)
        if id not in USERS.keys():
            create_user(user)
        admins = []
        for u in USERS.values():
            if u['group'] == 'admin':
                admins.append(u['id'])
        if id in admins:
            USERS[id]['group'] = 'basic'
            await msg.answer(f'Список администраторов обновлён. Администратор <b>{user["first_name"]}</b> {get_gender(id, "delete")}.')
        else:
            USERS[id]['group'] = 'admin'
            await msg.answer(f'Список администраторов обновлён. Администратор <b>{user["first_name"]}</b> {get_gender(id, "add")}.')
        save_users()


@dp.message_handler(commands=['trust'])
async def com_trust(msg):
    if msg.reply_to_message and checkright(msg) and msg.from_user.id != msg.reply_to_message.from_user.id:
        id = msg.reply_to_message.from_user.id
        user = await bot.get_chat(id)
        if id not in USERS.keys():
            create_user(user)
        trusted = []
        for u in USERS.values():
            if u['group'] == 'trusted':
                trusted.append(u['id'])
        if id in trusted:
            USERS[id]['group'] = 'basic'
            await msg.answer(f'<b>{user["first_name"]}</b> снят{get_gender(id, "postfix")} с доверия.')
        else:
            USERS[id]['group'] = 'trusted'
            await msg.answer(f'<b>{user["first_name"]}</b> доверен{get_gender(id, "postfix")}.')
        save_users()


@dp.message_handler(commands=['set'])
async def com_set(msg):
    if checkright(msg) and msg.reply_to_message:
        args = arguments(msg.text)
        id = msg.reply_to_message.from_user.id
        if id not in USERS.keys():
            user = await bot.get_chat(id)
            create_user(user)
        if args['arg1'] in USERS[id].keys():
            USERS[id][args['arg1']] = ' '.join(args['args'][1:])
            await msg.answer(f"Для <b>{USERS[id]['name']}</b> установлено:\n<b>{args['arg1']}</b> = {USERS[id][args['arg1']]}")
        save_users()


@dp.message_handler(commands=['getme'])
async def com_getme(msg):
    if checkright(msg):
        first_id = msg.from_user.id
        user_dic = ''
        args = arguments(msg.text)
        if msg.reply_to_message:
            msg = msg.reply_to_message
        if len(args['args']) > 0:
            if find_by_name(args['arg1']):
                user_dic = USERS[find_by_name(args['arg1'])]
            else:
                await msg.answer(f'<b>{args["arg1"]}</b> не найден(а).')
        else:
            if msg.from_user.id not in USERS.keys():
                user = await bot.get_chat(msg.from_user.id)
                create_user(user)
            user_dic = USERS[msg.from_user.id]
        if user_dic:
            text = f"{user_dic['emoji']} <b>{user_dic['name']}</b>\n" \
                   f"<i>aka {user_dic['names']}</i>\n\n" \
                   f"⚜ Репутация: <b>{user_dic['rep']}</b>"
            if first_id in USERS.keys() and 'admin' in USERS[first_id]['group']:
                text += f"\n\nGroup: <b>{user_dic['group']}</b>"
                if user_dic['perms']:
                    text += f"\nДополнительные права: <i>{user_dic['perms']}</i>"
            await msg.answer(text)


def user_rights(id):
    hier = config['PERMISSIONS']['hierarchy'].split(', ')
    if id in USERS.keys():
        perms = set(USERS[id]['perms'].split(', ')) if 'perms' in USERS[id].keys() else set()
        for group in hier[hier.index(USERS[id]['group']):]:
            perms = perms | set(config['PERMISSIONS'][group].split(', '))
        return ', '.join(list(perms))
    return config['PERMISSIONS']['basic']


def find_by_name(name):
    for id, data in USERS.items():
        if name in data['names']:
            return id
    return None


@dp.message_handler(commands=['help', 'start'])
async def help_message(msg):
    if checkright(msg):
        helpmsg = config['HELP']['begin'] + '\n\n'
        hier = config['PERMISSIONS']['hierarchy'].split(', ')[::-1]
        id = msg.from_user.id
        if id not in USERS.keys():
            user = await bot.get_chat(id)
            create_user(user)
        for group in hier[:hier.index(USERS[id]['group']) + 1]:
            helpmsg += config['HELP'][group] + '\n\n'
        helpmsg += config['HELP']['end']
        await msg.answer(helpmsg)


@dp.message_handler(Text(contains='rep'))
async def com_rep(msg):
    if msg.reply_to_message and checkright(msg, 'rep') and msg.from_user.id != msg.reply_to_message.from_user.id and \
            (msg.text[:4] == '-rep' or msg.text[:4] == '+rep'):
        id, id_torep, action = msg.from_user.id, msg.reply_to_message.from_user.id, msg.text[0]
        if id not in USERS.keys():
            user = await bot.get_chat(id)
            create_user(user)
        if 'rep_time' not in USERS[id].keys() or \
                ('rep_time' in USERS[id].keys() and dt.datetime.fromtimestamp(int((USERS[id]['rep_time'])))
                 + dt.timedelta(hours = 16) < dt.datetime.now()):
            if id_torep not in USERS.keys():
                user = await bot.get_chat(id_torep)
                create_user(user)
            USERS[id_torep]['rep'] = str(int(USERS[id_torep]['rep']) + (1 if action == '+' else -1))
            time = str(dt.datetime.timestamp(dt.datetime.now()))
            time = time[:time.find('.')]
            USERS[id]['rep_time'] = time
            text = f'⚜ Репутация <b>{USERS[id_torep]["name"]}</b> по{"выш" if action == "+" else "ниж"}ена.\n' \
                   f'{get_gender(id_torep, "him").capitalize()} текущая репутация: <b>{USERS[id_torep]["rep"]}</b>'
            await msg.reply(text)
            save_users()
        else:
            time = dt.datetime.fromtimestamp(int(USERS[id]["rep_time"])) + dt.timedelta(hours = 16) - dt.datetime.now()
            time = str(time)[:str(time).find('.')]
            await bot.send_message(id, f'До следующего использования rep:\n<b>{time}</b>')


log.info('Модуль permissions загружен')