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
            await msg.reply('История отчищена')
        else:
            message = msg.text[1:]
            if len(message) <= 1024:
                new_msg = await msg.reply('Минутку...')
                responce = chatgpt_get(message)
                await bot.edit_message_text(chat_id=new_msg.chat.id, message_id=new_msg.message_id, text=responce)
                MESSAGES.append({'role': 'assistant', 'content': responce})
            else:
                await msg.reply('К сожалению, вы превысили лимит запроса (1024 слов)')


def chatgpt_get(message):
    global MESSAGES
    MESSAGES.append({'role': 'user', 'content': message})
    length = 4096 - len(message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        messages=MESSAGES,  # The conversation history up to this point, as a list of dictionaries
        max_tokens=2048,  # The maximum number of tokens (words or subwords) in the generated response
        stop=None,  # The stopping sequence for the generated response, if any (not used here)
        temperature=0.7,  # The "creativity" of the generated response (higher temperature = more creative)
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content
