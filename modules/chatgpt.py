from botpackage import *
import openai_async
import tiktoken_async

CHAT_TOKEN = config['SECURITY']['openai_token']
MESSAGES = {}


@dp.message_handler(Text(startswith='!'))
async def chatgpt_call(msg):
    if checkright(msg, 'chatgpt'):
        global MESSAGES
        id = msg.chat.id
        if id not in MESSAGES:
            default_settings(id)
        if len(msg.text) > 2048:
            await msg.reply('😢 Задано слишком длинное сообщение (>2048 символов)')
            return
        if msg.text == '!!clear':
            MESSAGES[id]['content'] = []
            await msg.reply('💨 История отчищена')
        elif msg.text[:8] == '!!system':
            if len(msg.text) > 9:
                message = msg.text[9:]
                MESSAGES[id]['content'].append({'role': 'system', 'content': message})
                await msg.reply(f'🖥 Добавлен параметр: "{message}"')
            else:
                current = [v['content'] for v in MESSAGES[id]['content'] if v['role'] == 'system']
                await msg.reply(f'❗️ Напишите параметр (например, поведение бота - "You are a kitty")\nТекущие параметры: \n<b>{"; ".join(current)}</b>')
        elif msg.text[:13] == '!!temperature':
            message = msg.text[14:]
            try:
                n = float(message)
                if 0 <= n <= 1:
                    MESSAGES[id]['temperature'] = n
                    await msg.reply(f'🌡 Задана температура = {n}')
                else:
                    await msg.reply(f'❗️ Необходимо задать параметр от 0 до 1. (0 - ответ более серьёзный, точнее; 1 - ответ более случайный, креативный)\nТекущая температура = <b>{MESSAGES[id]["temperature"]}</b>')
            except Exception as ex:
                await msg.reply(f'❗️ Для задания температуры напишите число от 0 до 1. (0 - ответ более серьёзный, точнее; 1 - ответ более случайный, креативный)\nТекущая температура = <b>{MESSAGES[id]["temperature"]}</b>')
        elif msg.text[:8] == '!!tokens':
            message = msg.text[9:]
            try:
                n = int(message)
                if 0 <= n <= 4000:
                    MESSAGES[id]['max_tokens'] = n
                    await msg.reply(f'🧬 Заданы токены = {n}')
                else:
                    await msg.reply(f'❗️ Необходимо задать параметр от 0 до 4000. (максимальное кол-во токенов для ответа) \nТекущие токены = <b>{MESSAGES[id]["max_tokens"]}</b>')
            except Exception as ex:
                await msg.reply(f'❗️ Для задания максимального кол-ва токенов напишите число от 0 до 4000. \nТекущие токены = <b>{MESSAGES[id]["max_tokens"]}</b>')
        elif msg.text[:2] == '!!':
            message = msg.text[2:].strip()
            gen_msg = await msg.reply('⏳ Обрабатываю...')
            try:
                response = await chatgpt_get(id, message, single=True)
                await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                if len(response) > 4096:
                    await msg.reply(text=markdown.quote_html(response[:4096]), parse_mode=None)
                    await msg.reply(text=markdown.quote_html(response[4096:]), parse_mode=None)
                else:
                    await msg.reply(text=markdown.quote_html(response), parse_mode=None)
            except Exception as ex:
                await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                await msg.reply(text=f'😢 К сожалению, возникла следующая ошибка:\n\n <i>{ex}</i>')
        else:
            message = msg.text[1:].strip()
            gen_msg = await msg.reply('⏳ Обрабатываю...')
            try:
                response = await chatgpt_get(id, message)
                await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                if len(response) > 4096:
                    await msg.reply(text=markdown.quote_html(response[:4096]), parse_mode=None)
                    await msg.reply(text=markdown.quote_html(response[4096:]), parse_mode=None)
                else:
                    await msg.reply(text=markdown.quote_html(response), parse_mode=None)
                MESSAGES[id]['content'].append({'role': 'assistant', 'content': response})
            except Exception as ex:
                await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                await msg.reply(text=f'😢 К сожалению, возникла следующая ошибка:\n\n <i>{ex}</i>')


async def chatgpt_get(id, message, single=False):
    global MESSAGES
    if single:
        response = await openai_async.chat_complete(
            CHAT_TOKEN,
            timeout=60,
            payload={
                'model': "gpt-3.5-turbo",
                'messages': [{'role': 'user', 'content': message}],
                'max_tokens': MESSAGES[id]['max_tokens'],
                'stop': None,
                'temperature': MESSAGES[id]['temperature']
            }
        )
    else:
        MESSAGES[id]['content'].append({'role': 'user', 'content': message})
        text = ' '.join(v['content'] for v in MESSAGES[id]['content'])
        enc_text = await tiktoken_async.encoding_for_model('gpt-3.5-turbo')
        tokens = len(enc_text.encode(text))
        while tokens + MESSAGES[id]['max_tokens'] > 4000:
            del MESSAGES[id]['content'][0]
        response = await openai_async.chat_complete(
            CHAT_TOKEN,
            timeout=60,
            payload={
                'model': "gpt-3.5-turbo",
                'messages': MESSAGES[id]['content'],
                'max_tokens': MESSAGES[id]['max_tokens'],
                'stop': None,
                'temperature': MESSAGES[id]['temperature']
            }
        )

    response = response.json()

    return response['choices'][0]['message']['content']


def default_settings(id):
    global MESSAGES
    MESSAGES[id] = {
        'content': [],
        'temperature': 0.5,
        'max_tokens': 2000
    }
