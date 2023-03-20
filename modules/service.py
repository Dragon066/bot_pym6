from botpackage import *

DAYS = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
DAYS_SHORT = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
MONTH = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

LESSONS = json.load(open('files/lessons.txt', 'r', encoding='utf-8'))


def update_config_file():
    config = yaml.safe_load(open('config.yaml', 'r', encoding='utf-8'))


def convert(date):
    date = str(date).replace('.', '-')
    result = f"{date.split('-')[2]}.{date.split('-')[1]}, " \
    f"{DAYS_SHORT[cal.weekday(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))]}"
    return result


def convert_dayhw(date):
    date = str(date).replace('.', '-')
    result = f"{int(date.split('-')[2])} {MONTH[int(date.split('-')[1]) - 1]}, " \
    f"{DAYS[cal.weekday(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))]}"
    return result


def convert_day_header(date):
    date = str(date).replace('.', '-')
    return f"{int(date.split('-')[2])} {MONTH[int(date.split('-')[1]) - 1]}"


def convert_lesson(lesson):
    if lesson in LESSONS.keys():
        return LESSONS[lesson]['name']
    return lesson


def header(date_start, date_stop):
    date_start, date_stop = str(date_start), str(date_stop)
    result = f"💫 <b>Домашнее задание</b>\n" \
             f"<i>{convert_day_header(date_start)} — " \
             f"{convert_day_header(date_stop)}</i>\n\n"
    return result


def header_ruz(date_start, date_stop):
    date_start, date_stop = str(date_start), str(date_stop)
    result = f"📅 <b>Расписание</b>\n" \
             f"<i>{convert_day_header(date_start)} — " \
             f"{convert_day_header(date_stop)}</i>\n\n"
    return result


def go_async(func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func)


def header_works(date_start, date_stop):
    date_start, date_stop = str(date_start), str(date_stop)
    result = f"🖍 <b>Ближайшие работы</b>\n<i>{convert_day_header(date_start)} — {convert_day_header(date_stop)}\n\n</i>"
    return result


def arguments(text):
    text = text.split()
    com = text[0][1:]
    args = {f'arg{i + 1}':arg for i, arg in enumerate(text[1:])}
    args['com'] = com
    args['args'] = text[1:]
    return args


def checkadmin(id):
    return str(id) in config['SECURITY']['main_admins'] or str(id) in str(config['SECURITY']['admins'])
