from botpackage import *
from bs4 import BeautifulSoup

@dp.message_handler(commands=['holidays', 'hd'])
async def com_get_holidays(msg):
    await msg.answer(get_holidays(), disable_web_page_preview=True)


def get_holidays_response():
    link = "https://my-calend.ru/holidays"
    res = requests.get(link).text
    soup = BeautifulSoup(res, 'lxml')
    holidays = soup.find('ul', class_='holidays-items').find_all('li')
    namedays = soup.find('section', class_='holidays-name-days').find_all('span')
    result_holidays, result_namedays = [], []
    for holiday in holidays:
        a = holiday.find('a')
        if a:
            result_holidays.append((a.text, a['href']))
        else:
            text = holiday.find('span').text
            result_holidays.append((text,))
    for nameday in namedays:
        text = nameday.find('a')
        if text:
            result_namedays.append(text.text)
    return result_holidays, result_namedays


def get_holidays():
    result = f"🖼 <b>Праздники сегодня, {convert_dayhw(dt.date.today())}</b>\n\n"
    try:
        holidays, namedays = get_holidays_response()
    except Exception as ex:
        log.exception('Ошибка получения списка праздников')
        return 'Ошибка получения списка праздников 😢'
    sign = ''
    for holiday in holidays:
        if len(holiday) > 1:
            holiday = f'<a href="{holiday[1]}">{holiday[0]}</a>'
        else:
            holiday = holiday[0]
        result += f"– {sign} {holiday} {'' if sign == '' else '</b>'}\n"
        sign = '' if sign != '' else '<b>'
    result += '\n🤟 <b>Именины отмечают:</b>\n'
    result += ', '.join(namedays)
    return result


log.info('Модуль holidays загружен')