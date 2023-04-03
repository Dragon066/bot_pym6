from botpackage import *


@dp.message_handler(commands=['test'])
async def com_test(msg):
    if checkright(msg):
        await msg.answer('Это тестовая функция. Сейчас здесь ничего нет.')


@dp.message_handler(commands=['ping'])
async def com_ping(msg):
    if checkright(msg):
        time = dt.datetime.now() - UPTIME
        text = f'Pong! 😉\n<b>Uptime: {str(time)[:str(time).find(".")]}</b>'
        await msg.answer(text)


@dp.message_handler(commands=['getchat'])
async def com_getchat(msg):
    text = f'<b>ID данного чата</b>:\n<code>{msg.chat.id}</code>'
    await msg.answer(text)


@dp.message_handler(commands=['update'])
async def com_update(msg):
    if checkright(msg):
        args = arguments(msg.text)
        silence = True if len(args['args']) > 1 and 'silen' in args['arg2'] else False
        if len(args['args']) > 0:
            if args['arg1'] in ('hw', 'homework') and config['MODULES']['homework']:
                from modules.homework import update_hw_file
                update_hw_file()
                await msg.answer("♻️ Домашнее задание обновлено")
            elif args['arg1'] in ('config', 'cfg'):
                update_config_file()
                await msg.answer("♻️ Конфигурационный файл обновлён")
            elif args['arg1'] in ('users', 'user'):
                update_users()
                await msg.answer("♻️ Данные пользователей обновлены")
            elif args['arg1'] in ('ruz',) and config['MODULES']['ruz']:
                from modules.ruz import update_ruz
                await update_ruz(silence)
                if not silence:
                    await msg.answer("♻️ Расписание обновлено")
            elif args['arg1'] in ('mail', 'gmail') and config['MODULES']['gmail']:
                from modules.gmail import gmail_update_msgs
                await gmail_update_msgs()
                await msg.answer("♻️ Почта обновлена")
            elif args['arg1'] in ('files', 'dirs', 'file', 'dir') and config['MODULES']['files']:
                from modules.files import update_files
                update_files()
                await msg.answer("♻️ Файловая система обновлена")
            elif args['arg1'] in ('s', 'sperm', 'cum') and config['MODULES']['sperm']:
                from modules.games.sperm import load_sperm
                load_sperm()
                await msg.answer("♻️ Спермодрочеры обновлены")
            else:
                await update_all(msg)
        else:
            await update_all(msg)

async def update_all(msg):
    update_users()
    update_config_file()
    if config['MODULES']['homework']:
        from modules.homework import update_hw_file
        update_hw_file()
    if config['MODULES']['gmail']:
        from modules.gmail import gmail_update_msgs
        await gmail_update_msgs()
    if config['MODULES']['ruz']:
        from modules.ruz import update_ruz
        await update_ruz()
    if config['MODULES']['files']:
        from modules.files import update_files
        update_files()
    if config['MODULES']['sperm']:
        from modules.games.sperm import load_sperm
        load_sperm()
    await msg.answer("♻️ Файлы обновлены")


@dp.message_handler(commands=['delmsg'])
async def com_delmsg(msg):
    if checkright(msg) and msg.reply_to_message:
        try:
            await bot.delete_message(msg.chat.id, msg.reply_to_message.message_id)
        except Exception as err:
            log.exception('Ошибка при удалении сообщения (delmsg)')


@dp.message_handler(commands=['logs'])
async def com_logs(msg):
    if checkright(msg):
        try:
            with open('files/logs.txt', 'r', encoding='utf-8') as f:
                text = f.read()[-4096:]
                text = text[text.find('\n'):]
            if len(msg.text.split()) == 1 and '--------------------------------------' in text:
                text = text[text.rfind('--------------------------------------'):]
            await msg.answer(text, parse_mode=None)
        except Exception as ex:
            await msg.answer(f'😱 Возникла ошибка при загрузке логов:\n<i>{ex}</i>')
            log.exception('Ошибка загрузки логов')


@dp.message_handler(commands=['silence'])
async def com_silence(msg):
    if checkright(msg):
        global SILENCE
        if SILENCE:
            SILENCE = False
            await msg.answer('🔇 Режим тишины <b>включён</b>.\nВ это время перестанут поступать уведомления '
                             'об изменениях в расписании и получении новых писем.')
        else:
            SILENCE = True
            await msg.answer('🔉 Режим тишины <b>отключён</b>')


@dp.message_handler(commands=['fact'])
async def com_fact(msg):
    await msg.reply(get_random_fact(1)[0])


def get_random_fact(n):
    result = []
    for i in range(n):
        resp = requests.get('https://lucky-random.ru/modules/frand/api.php')
        text = resp.text
        text = text[text.find('|') + 1 : text.find('|', text.find('|') + 2)]
        result.append(text)
    return result


log.info('Модуль commands загружен')