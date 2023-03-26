from botpackage import *
import openai

openai.api_key = config['SECURITY']['openai_token']
MESSAGES = []


@dp.message_handler(Text(startswith='!'))
async def chatgpt_call(msg):
    if checkright(msg, 'chatgpt'):
        global MESSAGES
        if msg.text == '!clear':
            MESSAGES = []
            await msg.reply('💨 История отчищена')
        else:
            message = msg.text[1:]
            if len(message) <= 1024:
                new_msg = await msg.reply('⏳ Обрабатываю...')
                try:
                    responce = chatgpt_get(message)
                    await bot.edit_message_text(chat_id=new_msg.chat.id, message_id=new_msg.message_id, text=responce,
                                                parse_mode=None)
                    MESSAGES.append({'role': 'assistant', 'content': responce})
                except Exception as ex:
                    await bot.edit_message_text(chat_id=new_msg.chat.id, message_id=new_msg.message_id,
                                                text='😢 К сожалению, возникла следующая ошибка:\n\n' + ex)
            else:
                await msg.reply('😢 К сожалению, вы превысили лимит запроса (1024 слов)')


def chatgpt_get(message):
    global MESSAGES
    MESSAGES.append({'role': 'user', 'content': message})
    length = 4096 - len(message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=MESSAGES,
        max_tokens=2048,
        stop=None,
        temperature=0.7,
    )

    for choice in response.choices:
        if "text" in choice:
            return choice.text

    return response.choices[0].message.content
