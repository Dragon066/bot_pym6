from botpackage import *

STATS = {}


@dp.message_handler(commands=['stats'])
async def com_get_stats(msg):
    if checkright(msg):
        await msg.answer(get_stats())
        await msg.answer_photo(get_stat_plot())


def stat(command):
    if command in STATS:
        STATS[command] += 1
    else:
        STATS[command] = 1


def clear_stats():
    global STATS
    STATS = {}


def get_stat_plot():
    import matplotlib.pyplot as plt
    items = dict(sorted(STATS.items(), key=lambda x: x[1], reverse=True))
    values = list(items.values())
    keys = ['/' + val for val in list(items.keys())]
    fig, ax = plt.subplots(figsize=(10, 10), dpi=80)
    fig.set_facecolor('#DCDCDC')
    ax.pie(values, labels=keys, autopct=lambda p : '{:.1f}%  ({:,.0f})'.format(p,p * sum(values)/100),
           textprops={'fontsize': 16})
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    return img


def get_stats():
    text = f'📊 <b>Статистика</b>\n<i>за прошедший день</i>\n\n'
    if len(STATS) > 0:
        items = sorted(STATS.items(), key=lambda x: x[1], reverse=True)
        for command, value in items:
            text += f"<b>/{command}</b> - {value}\n"
    else:
        text += 'Статистика отсутствует'
    return text

log.info('Модуль statistics загружен')
