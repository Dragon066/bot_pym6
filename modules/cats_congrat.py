from botpackage import *

CATSHASH = {}


def load_catshash():
    global CATSHASH
    try:
        with open(CATSHASH_path, 'r', encoding='utf-8') as f:
            CATSHASH = json.load(f)
        log.info('CATSHASH загружен')
    except Exception as err:
        log.exception('Ошибка при загрузке CATSHASH')


def save_catshash():
    try:
        with open(CATSHASH_path, 'w', encoding='utf-8') as f:
            json.dump(CATSHASH, f, ensure_ascii=False, indent=4)
    except Exception as err:
        log.exception('Ошибка при сохранении CATSHASH')


def get_cats_congrat_keyboard(hash):
    keyboard = types.InlineKeyboardMarkup()
    if CATSHASH[hash]['text'] != None:
        button1 = types.InlineKeyboardButton(text='🥳 Отправить в группу (с текстом)', callback_data=f'cats,{hash},True')
        button2 = types.InlineKeyboardButton(text='🥳 Отправить в группу (без текста)', callback_data=f'cats,{hash},False')
        keyboard.add(button1)
        keyboard.add(button2)
    else:
        button = types.InlineKeyboardButton(text='🥳 Отправить в группу', callback_data=f'cats,{hash},False')
        keyboard.add(button)
    return keyboard


@dp.callback_query_handler(Text(startswith='cats,'))
async def callback_cats_congrat(call):
    if checkright(call, 'sendcats'):
        hash = call.data.split(',')[1]
        photo = CATSHASH[hash]['photos'][0]
        capt = CATSHASH[hash]['text'] if call.data.split(',')[2] == 'True' else None
        await bot.send_photo(chat_id=GROUP, photo=photo, caption=capt)
        text = (call.message.caption if call.message.caption else '') + '\n\n--------\n' + f'<i>Отправлено by <b>{call["from"]["first_name"]}</b></i>'
        await bot.edit_message_caption(message_id=call.message.message_id, chat_id=call.message.chat.id,
                                    caption=text)


def get_cats_congrat(url='https://vk.com/m4a12'):
    result = {}
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'lxml')

    posts = soup.find_all('div', class_='wall_item')

    for post in posts:
        try:
            temp = post.find('div', {'class': 'wi_body'})
            try:
                text = temp.find('div', {'class': 'pi_text'}).text
            except:
                text = None
            photos = temp.find_all('img')
            photos = [photo['src'] for photo in photos if 'https://sun' in photo['src']]
            hash = str(text) + ''.join(photos)
            hash = hashlib.md5(hash.encode()).hexdigest()
            if hash not in CATSHASH:
                result[hash] = {
                    'text': text,
                    'photos': photos
                }
                CATSHASH[hash] = result[hash]
                save_catshash()
        except Exception as ex:
            print(ex)
            continue

    return result


async def send_cats_congrat():
    data = get_cats_congrat()

    if len(data) > 0:
        for hash, post in data.items():
            capt = post['text']
            await bot.send_photo(chat_id=ADM_GROUP, photo=post['photos'][0],
                                 caption=capt, reply_markup=get_cats_congrat_keyboard(hash))
            if len(post['photos']) > 1:
                media = types.MediaGroup()
                capt = '<i>Все фото</i>'
                for photo in post['photos']:
                    media.attach_photo(photo, caption=capt)
                    capt = None
                await bot.send_media_group(ADM_GROUP, media=media)

load_catshash()

log.info('Котятки загружены')