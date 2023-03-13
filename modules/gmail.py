import hashlib

from botpackage import *
from modules.files import *

from bs4 import BeautifulSoup
import base64
import os.path
from lxml import html

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

GMAIL_path = config['PATH']['gmail_token']

MAIL = {}


def get_keyboard_mails(start):
    keyboard = types.InlineKeyboardMarkup()
    mail_list = list(MAIL.keys())
    for i in range(int(start), int(start) + 5):
        if i < len(MAIL.keys()):
            text = '📎 ' if 'attachment' in MAIL[mail_list[i]].keys() else '✉ '
            sender = html.fromstring(MAIL[mail_list[i]]['sender']).text_content().strip().replace('"', '')
            subject = MAIL[mail_list[i]]['subject']
            text += f"[{sender}] {subject} "
            button = types.InlineKeyboardButton(text=text, callback_data=f'ml,{mail_list[i]}')
            keyboard.add(button)
    if int(start) > 0 and int(start) + 5 < len(list(MAIL.keys())):
        button1 = types.InlineKeyboardButton(text='⬅ Предыдущая', callback_data=f'ml,go,{int(start) - 5}')
        button2 = types.InlineKeyboardButton(text='Следующая ➡', callback_data=f'ml,go,{int(start) + 5}')
        keyboard.row(button1, button2)
    else:
        if int(start) > 0:
            button = types.InlineKeyboardButton(text='⬅ Предыдущая страница', callback_data=f'ml,go,{int(start) - 5}')
            keyboard.add(button)
        if int(start) + 5 < len(list(MAIL.keys())):
            button = types.InlineKeyboardButton(text='Следующая страница ➡', callback_data=f'ml,go,{int(start) + 5}')
            keyboard.add(button)
    button = types.InlineKeyboardButton(text='🚫 Выход', callback_data=f'ml,cancel')
    keyboard.add(button)
    return keyboard


@dp.message_handler(commands=['mail'])
async def com_mail(msg):
    if checkright(msg):
        text = f'📬 <b>Почта Gmail:</b>\n<i>Страница 1, 1-5 / {len(MAIL.keys())}</i>'
        await msg.answer(text, reply_markup=get_keyboard_mails(0))


@dp.callback_query_handler(Text(startswith='ml,'))
async def callback_mail(call):
    if len(call.data.split(',')) > 2:
        start = call.data.split(',')[2]
        text = f'📬 <b>Почта Gmail:</b>\n<i>Страница {int(start)//5 + 1},' \
               f' {int(start) + 1}-{int(start) + 5 if int(start) + 5 < len(MAIL.keys()) else len(MAIL.keys())} / {len(list(MAIL.keys()))}</i>'
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text, reply_markup=get_keyboard_mails(start))
    elif call.data.split(',')[1] == 'cancel':
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text="⭕ Выход из почты :(")
    else:
        id = call.data.split(',')[1]
        text = get_mail(id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text=text)
        if 'attachment' in MAIL[id].keys():
            await bot.send_chat_action(call.message.chat.id, types.ChatActions.UPLOAD_DOCUMENT)
            for att in MAIL[id]['attachment']:
                keyboard = None
                capt = None
                from modules.files import FILES
                if not FILES[att]['id']:
                    file = open(att, 'rb')
                else:
                    file = FILES[att]['id']
                new_msg = await bot.send_document(call.message.chat.id, file, reply_to_message_id=call.message.message_id,
                                       caption=capt)
                if not FILES[att]['id']:
                    FILES[att]['id'] = new_msg.document.file_id
                    save_files()
    
    
def load_mail():
    global MAIL
    try:
        with open('files/mail.txt', 'r', encoding='utf-8-sig') as f:
            MAIL = json.load(f)
        log.info('Почта загружена')
    except Exception as err:
        log.exception('Ошибка при загрузке почты')


def backup_mail():
    try:
        if not os.path.exists(config['PATH']['mail_backup']):
            os.mkdir(config['PATH']['mail_backup'])
        file = f"{mail_backup_path}mail_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
        shutil.copy('files/mail.txt', file)
    except Exception as err:
        log.exception('Ошибка при бекапе почты')


def optimize_mail():
    global MAIL
    MAIL = dict(sorted(MAIL.items(), key=lambda x: dt.datetime.strptime(x[1]['date_value'], '%Y-%m-%d %H:%M:%S'), reverse=True))


def save_mail():
    backup_mail()
    try:
        with open('files/mail.txt', 'w', encoding='utf-8-sig') as f:
            json.dump(MAIL, f, ensure_ascii=False, indent=4)
        log.info('Почта сохранена')
    except Exception as err:
        log.exception('Ошибка при сохранении почты')


async def get_creds():
    creds = None
    try:
        if os.path.exists(GMAIL_path + 'token.json'):
            creds = Credentials.from_authorized_user_file(GMAIL_path + 'token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(GMAIL_path + 'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open(f'{GMAIL_path}token.json', 'w') as token:
                token.write(creds.to_json())
    except Exception as err:
        log.exception('Ошибка получения токена Gmail')
        await bot.send_message(ADM_GROUP, f'<b>❗ Ошибка получения токена GMAIL:</b>\n\n{err}')
    return creds


def GetAttachments(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        paths = []

        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = 'media/gmail/' + part['filename']
                from modules.files import FILES
                if path in FILES.keys():
                    i = 1
                    ext = path[path.rfind('.'):]
                    part1 = path[:path.find(ext)]
                    while f"{part1} ({i}){ext}" in FILES.keys():
                        i += 1
                    path = f"{part1} ({i}){ext}"
                paths.append(path)
                update_files()

                with open(path, 'wb') as f:
                    f.write(file_data)

    except Exception as error:
        log.exception('Ошибка при скачивании вложения')

    return paths


async def gmail_update_msgs():
    global MAIL
    creds = await get_creds()

    new_mails = {}
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        with open('files/mailhash.txt', 'r') as f:
            hash_old = f.read()

        if hash_old != str(messages):
            log.info('Почта: хэши не совпадают, начинаю обработку писем...')
            for i, msg in enumerate(messages):
                if msg['id'] in MAIL.keys():
                    continue
                await asyncio.sleep(0.001)
                txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                try:
                    payload = txt['payload']
                    if payload.get('parts') == None:
                        continue
                    headers = payload['headers']
                    subject = ''
                    sender = ''
                    date = ''
                    date_value = ''
                    for d in headers:
                        if d['name'] == 'Subject':
                            subject = d['value']
                            continue
                        if d['name'] == 'From':
                            sender = d['value']
                            continue
                        if d['name'] == 'Date':
                            date = d['value']
                            try:
                                date_value = dt.datetime.strptime(' '.join(date.split()[:-1]), '%a, %d %b %Y %H:%M:%S')
                            except:
                                date_value = dt.datetime.strptime(' '.join(date.split()[:-2]), '%a, %d %b %Y %H:%M:%S')
                    if 'pm22to6@gmail.com' in sender:
                        continue
                    parts = payload.get('parts')
                    data = ''
                    attachment = False
                    for part in parts:
                        if 'multipart' in part['mimeType']:
                            for inpart in part['parts']:
                                if 'text/plain' in inpart['mimeType']:
                                    try:
                                        temp = inpart['body']['data']
                                        temp = temp.replace("-", "+").replace("_", "/")
                                        decoded_data = base64.b64decode(temp).decode('utf-8')
                                        data += decoded_data + '\n\n'
                                    except:
                                        continue
                                elif part['filename']:
                                    attachment = True
                        elif part['filename']:
                            attachment = True
                        elif 'text/plain' in part['mimeType']:
                            try:
                                temp = part['body']['data']
                                temp = temp.replace("-", "+").replace("_", "/")
                                decoded_data = base64.b64decode(temp).decode('utf-8')
                                data += decoded_data + '\n\n'
                            except:
                                continue

                    soup = BeautifulSoup(data, "lxml").text
                    body = soup
                    MAIL[txt['id']] = {}
                    MAIL[txt['id']]['subject'] = subject if subject else '(без темы)'
                    MAIL[txt['id']]['sender'] = sender if sender else '(отсутствует)'
                    MAIL[txt['id']]['message'] = body if body else '(отсутствует)'
                    MAIL[txt['id']]['date'] = date if date else '(отсутствует)'
                    MAIL[txt['id']]['date_value'] = str(date_value) if date_value else '2050-01-01 01:01:01'
                    if attachment:
                        result = GetAttachments(service, 'me', msg['id'])
                        MAIL[txt['id']]['attachment'] = result
                    new_mails[txt['id']] = MAIL[txt['id']]
                    log.info(f'{txt["id"]} обработан, {i + 1}/{len(messages)}')

                except Exception as err:
                    log.exception('Ошибка при обработке письма')
                    pass

        with open('files/mailhash.txt', 'w') as f:
            f.write(str(messages))

    except HttpError as err:
        log.exception('Ошибка при получении писем с почты')

    if len(new_mails) > 0:
        backup_mail()
        optimize_mail()
        save_mail()
        await send_new_mails(new_mails)
        update_files()


async def send_new_mails(mails):
    await bot.send_message(GROUP, f'📬 <b>Обнаружены новые сообщения на почте!</b>\n<i>Количество: {len(mails)}</i>')
    for id in mails:
        text = get_mail(id)
        if len(mails) < 5:
            await bot.send_message(GROUP, text=text)
        if 'Ирина ИВ Баскова' in MAIL[id]['sender']:
            await bot.send_message(813128237, text=text)
        if 'attachment' in MAIL[id].keys():
            if len(mails) < 5:
                await bot.send_chat_action(GROUP, types.ChatActions.UPLOAD_DOCUMENT)
                for att in MAIL[id]['attachment']:
                    keyboard = None
                    capt = None
                    update_files()
                    from modules.files import FILES
                    if not FILES[att]['id']:
                        file = open(att, 'rb')
                    else:
                        file = FILES[att]['id']
                    new_msg = await bot.send_document(GROUP, file, caption=capt)
                    if 'Ирина ИВ Баскова' in MAIL[id]['sender']:
                        await bot.send_document(813128237, file, caption=capt)
                    if not FILES[att]['id']:
                        FILES[att]['id'] = new_msg.document.file_id
                        save_files()


def get_mail(id):
    subject = html.fromstring(MAIL[id]["subject"]).text_content()
    sender = html.fromstring(MAIL[id]["sender"]).text_content().replace('"', '')
    try:
        date = dt.datetime.strptime(MAIL[id]['date_value'], '%Y-%m-%d %H:%M:%S')
        date = convert_day_header(date.date()) + f' {date.date().year}, {date.time()}'
    except:
        date = html.fromstring(MAIL[id]["date"]).text_content()
    msg = html.fromstring(MAIL[id]["message"]).text_content()
    text = f'<b>Тема:</b> <code>{subject}</code>\n<b>Отправитель:</b> <code>{sender}</code>\n' \
           f'<b>Дата:</b> <code>{date}</code>\n\n<b>Сообщение:</b>\n{msg}'
    if 'attachment' in MAIL[id].keys():
        text += f'\n\n<b>Прикреплено к письму:</b>'
        for att in MAIL[id]["attachment"]:
            ext = att[att.rfind('.') + 1:]
            ext = file_types[ext] if ext in file_types else '📄'
            text += f'<i>\n{ext} {att[att.rfind("/") + 1:]}</i>'
    while '\n\xa0\n' in text:
        text = text.replace('\n\xa0\n', '\n\n')
    text = text.replace('\xa0', ' ')
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    if len(text) > 4096:
        text = text[:4090] + '\n\n...'
    return text


log.info('Модуль gmail загружен')