from botpackage import *

def get_weather_raw():
    response = requests.get(
        'https://www.yandex.com/weather/segment/details?offset=0&lat=55.73182&lon=37.658581&geoid=213&limit=10',
        headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'lxml')

    res = []

    for card in soup.find_all('article', class_='card'):
        date = card.find('div', class_='a11y-hidden')
        if not date:
            continue
        date = date.text
        temp = []
        for row in card.find_all('tr', class_='weather-table__row'):
            temp.append([i.text.replace('−', '-') for i in row.find_all('div', class_='temp', role='text')][-1])
        weather = [i.text for i in card.find_all('td', class_='weather-table__body-cell weather-table__body-cell_type_condition')]
        wind = [i.text.replace(',', '.') for i in card.find_all('span', class_='wind-speed')]
        res.append({
            'day': int(date.split()[1]),
            'month': date.split()[2],
            'temp': temp,
            'weather': weather,
            'wind': list(map(float, wind))
        })

    return res[:7]


def get_weather_sign(weather_old):
    weather = weather_old.lower()
    if 'cloud' in weather:
        return ('Облачно', '⛅️')
    if 'overcast' in weather:
        return ('Дико облачно', '☁️')
    if 'rain' in weather:
        return ('Дождливо :(', '🌧')
    if 'clear' in weather:
        return ('Солнечно!!', '☀️')
    return weather_old


def get_weather_stat(stats):
    import matplotlib.pyplot as plt
    temp = [i['temp'] for i in stats]
    temp = [list(map(int, t)) for t in temp]
    names = [str(i['day']) + ' ' + i['month'] for i in stats]
    plt.subplots(figsize=(15, 5), dpi=300)
    plt.xlabel('Дни')
    plt.ylabel('Температура')
    colors = ['orange', 'red', 'blue', 'darkgray']
    import matplotlib.font_manager as mfm
    # a = mfm.FontManager()
    # print(a.get_font_names())
    # a.addfont('~/../../usr/share/fonts/segoe/segoe/segoeui.ttf')
    # prop = mfm.FontProperties(family='Segoe UI')
    for i in range(4):
        plt.plot([t[i] for t in temp], color=colors[i])
        for j in range(len(stats)):
            text = ('+' if temp[j][i] > 0 else '') + str(temp[j][i]) + ' ' + get_weather_sign(stats[j]['weather'][i])[0]
            plt.annotate(text, (j, temp[j][i] + (0.2 if i % 2 == 0 else 0.5)), color=colors[i])#, fontproperties=prop)
    for i in range(len(stats)):
        text = ' м/с\n'.join(map(str, stats[i]['wind'])) + ' м/с'
        plt.annotate(text, (i - 0.15, min([min(map(int, t)) for t in temp]) - 2.75))
    plt.legend(labels=['Утро', 'День', 'Вечер', 'Ночь'])
    plt.xticks(range(len(stats)), labels=names)
    plt.yticks(range(min([min(map(int, t)) for t in temp]) - 4, max([max(map(int, t)) for t in temp]) + 4))
    plt.grid(linestyle=':')
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return img


def get_weather_info(info):
    text = f"Утром <b>{info['temp'][0]}°</b>, {' '.join(get_weather_sign(info['weather'][0])[::-1])}, <i>{info['wind'][0]} м/с</i>\n" \
           f"Днём <b>{info['temp'][1]}°</b>, {' '.join(get_weather_sign(info['weather'][1])[::-1])}, <i>{info['wind'][1]} м/с</i>\n" \
           f"Вечером <b>{info['temp'][2]}°</b>, {' '.join(get_weather_sign(info['weather'][2])[::-1])}, <i>{info['wind'][2]} м/с</i>\n" \
           f"Ночью <b>{info['temp'][3]}°</b>, {' '.join(get_weather_sign(info['weather'][3])[::-1])}, <i>{info['wind'][3]} м/с</i>\n\n"
    return text

@dp.message_handler(commands=['weather'])
async def com_weather(msg):
    if checkright(msg):
        capt = '🌪 <b>Погодка на недельку, мяу</b>\n\n'
        info = get_weather_raw()[0]
        capt += f"<b>Сегодня</b>, {info['day']} {info['month']}\n\n"
        capt += get_weather_info(info)
        info = get_weather_raw()[1]
        capt += f"<b>Завтра</b>, {info['day']} {info['month']}\n\n"
        capt += get_weather_info(info)
        await msg.answer_photo(get_weather_stat(get_weather_raw()), caption=capt)