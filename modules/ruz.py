from botpackage import *
from fa_api import FaAPI

table_old = {}
table = {}
try:
    with open(RUZ_path, 'r', encoding='utf-8') as f:
        table = json.load(f)
except Exception as err:
    log.exception('Ошибка при загрузке расписания')
fa = FaAPI()


@dp.message_handler(commands=['ruz'])
async def com_get_ruz(msg):
    if checkright(msg):
        args = arguments(msg.text)
        date_start, date_stop = dt.date.today(), dt.date.today() + dt.timedelta(days=7)
        date_stop = date_stop + dt.timedelta(days=(6 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
        if len(args['args']) > 0:
            line = args['arg1'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
            try:
                date_start = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
                date_stop = date_start + dt.timedelta(days=7)
                date_stop = date_stop + dt.timedelta(
                    days=(6 - cal.weekday(date_stop.year, date_stop.month, date_stop.day)))
            except:
                pass
        if len(args['args']) > 1:
            line = args['arg2'].replace(' ', '-').replace(',', '-').replace('.', '-').split('-')
            try:
                date_stop = dt.date(dt.date.today().year, int(line[1]), int(line[0]))
            except:
                pass
        await msg.answer(get_ruz(date_start, date_stop))


def backup_ruz():
    try:
        if not os.path.exists(config['PATH']['ruz_backup']):
            os.mkdir(config['PATH']['ruz_backup'])
        file = f"{ruz_backup_path}ruz_{str(dt.datetime.now())[:19].replace(' ', '_').replace(':', '_')}.txt"
        shutil.copy(RUZ_path, file)
    except Exception as err:
        log.exception('Ошибка при бэкапе расписания')


def save_ruz():
    global table
    backup_ruz()
    try:
        with open(RUZ_path, 'w', encoding='utf-8') as f:
            json.dump(table, f, ensure_ascii=False, indent=4)
        log.info('Расписание сохранено')
    except Exception as err:
        log.exception('Ошибка при сохранении расписания')


async def update_ruz(silence=False):
    global table
    global table_old
    table_old = table
    table = {}
    group = fa.search_group(GROUP_NAME)
    time_start = dt.date.today()
    time_start = f"{time_start.year}.{str(time_start.month).rjust(2,'0')}.{str(time_start.day).rjust(2,'0')}"
    time_stop = dt.date.today() + dt.timedelta(days=60)
    time_stop = f"{time_stop.year}.{str(time_stop.month).rjust(2,'0')}.{str(time_stop.day).rjust(2,'0')}"
    timetable = fa.timetable_group(group[0]["id"], time_start, time_stop)
    for lesson in timetable:
        await asyncio.sleep(0.001)
        text = {'discipline': lesson['discipline'], 'date': lesson['date'], 'auditorium': lesson['auditorium'],
                'lecturer': lesson['lecturer'], 'lecturer_fullname': lesson['lecturer_title'],
                'group': lesson['group'], 'stream': lesson['stream'], 'begin': lesson['beginLesson'],
                'end': lesson['endLesson'], 'work': lesson['kindOfWork']}
        date = text['date']
        time = text['begin']
        if date not in table.keys():
            table[date] = {}
        if time not in table[date]:
            table[date][time] = text
        else:
            d = {}
            lst_lec = table[date][time]['lecturer'].split(' || ')
            lst_aud = table[date][time]['auditorium'].split(' || ')
            lst_lec_full = table[date][time]['lecturer_fullname'].split(' || ')
            for i in range(len(lst_lec)):
                d[lst_lec[i]] = lst_aud[i]
            d[text['lecturer']] = text['auditorium']
            d = dict(sorted(list(d.items())))
            lst_lec_full.append(text['lecturer_fullname'])
            lst_lec_full = sorted(lst_lec_full)
            table[date][time]['auditorium'] = ' || '.join(list(d.values()))
            table[date][time]['lecturer'] = ' || '.join(list(d.keys()))
            table[date][time]['lecturer_fullname'] = ' || '.join(lst_lec_full)
    if table != table_old:
        time_ = dt.datetime.now().time()
        log.info(f'Расписание обновлено: {len(timetable)} пар загружено, {len(table) - len(table_old)} новых')
        if not silence:
            await send_ruz_diff()
        save_ruz()
        return True
    return False


async def send_ruz_diff():
    global table, table_old
    diff = ''
    for date in table:
        if dt.date.today() <= dt.date.fromisoformat(date.replace('.', '-')) <= dt.date.today() + dt.timedelta(days=14):
            date_ = convert_dayhw(date)
            if date in table_old.keys():
                if table_old[date] != table[date]:
                    diff += f"⚠ Изменено расписание <b>{date_}</b>:\n\n{highlight_diff(table[date], table_old[date])}\n"
            else:
                diff += f"⚠ Добавлено расписание на <b>{date_}</b>:\n\n{convert_ruz_date(date)}\n"
    for date in table_old:
        if dt.date.today() <= dt.date.fromisoformat(date.replace('.', '-')) <= dt.date.today() + dt.timedelta(days=14):
            date_ = convert_dayhw(date)
            if date not in table.keys():
                diff += f"⚠ Удалено расписание на <b>{date_}</b>:\n{convert_ruz_date(date, old=True)}\n"
    if len(diff) != 0 and SILENCE:
        if len(diff) < 4096:
            await bot.send_message(GROUP, diff)
        else:
            await bot.send_message(GROUP, '⚠ Расписание имеет огромное количество изменений. Уделите своё внимание 😑')


def get_ruz(date_start = dt.date.today(), date_stop = dt.date.today() + dt.timedelta(days=7), header=True):
    result = header_ruz(date_start, date_stop) if header else ''
    while date_start <= date_stop:
        flag = True
        if str(date_start).replace('-', '.') in table.keys():
            result += convert_ruz_date(str(date_start).replace('-', '.')) + '\n'
        date_start += dt.timedelta(days=1)
    if abs(len(result) - len(header_ruz(date_start, date_stop))) < 5:
        result += 'Расписания на данный период времени нет 😔'
    if len(result) > 4096:
        result = header_ruz(date_start, date_stop) if header else '' + '\n\n⚠ За данный промежуток времени слишком много пар 😱'
    return result


def convert_ruz_lesson(lesson):
    discipline = lesson['discipline']
    result = f"🔸 <b>{lesson['begin']}-{lesson['end']}, {convert_lesson(discipline)}</b>\n"
    if '||' in lesson['lecturer']:
        result += f"<i>{lesson['work']},</i>\n" if discipline in LESSONS.keys() and LESSONS[discipline]['show_kindofwork'] else ''
        lec_flag = ['<u>', '</u>'] if '<u>' in lesson['lecturer'] else ['', '']
        aud_flag = ['<u>', '</u>'] if '<u>' in lesson['auditorium'] else ['', '']
        lecs = lesson['lecturer'].replace('<u>', '').replace('</u>', '').split(' || ')
        auds = lesson['auditorium'].replace('<u>', '').replace('</u>', '').split(' || ')
        for i in range(len(lecs)):
            result += f"<i>{lec_flag[0]}{lecs[i]}{lec_flag[1]}, {aud_flag[0]}{auds[i][auds[i].find('/') + 1:]}{aud_flag[1]}</i>\n"
    else:
        if discipline in LESSONS.keys():
            to_add = []
            if LESSONS[discipline]['show_kindofwork']:
                to_add.append(lesson['work'])
            if LESSONS[discipline]['show_lecturer']:
                to_add.append(lesson['lecturer'])
            if LESSONS[discipline]['show_auditorium']:
                lesson_aud = lesson['auditorium'][lesson['auditorium'].find('/') + 1:].replace('ауд.', '')
                if '<u>' in lesson['auditorium']:
                    lesson_aud = f"<u>{lesson_aud}"
                to_add.append(lesson_aud)
            result += f"<i>{', '.join(to_add)}</i>\n"
        else:
            result += f"<i>{lesson['work']}, {lesson['lecturer']}, {lesson['auditorium']}</i>\n"
    return result


def convert_ruz_date(date, old=False, header=True):
    table_ = table_old if old else table
    result = f"🔻 <b>{convert_dayhw(str(date))}</b>:\n" if header else ''
    for time, lesson in table_[date].items():
        result += convert_ruz_lesson(lesson)
    return result


def highlight_diff(new, old):
    diff_count = sum([0 if new[key] == old[key] else 1 for key in new.keys()]) if len(new) == len(old) else 2
    diff_old = diff_new = '...\n' if diff_count == 1 and len(new) > 0 else ''
    for time, lesson in new.items():
        if new[time] != old[time]:
            if time in old.keys():
                d_old, d_new = {}, {}
                for key, value in lesson.items():
                    d_new[key] = value if value == old[time][key] else f"<u>{value}</u>"
                    d_old[key] = value if value == old[time][key] else f"<u>{old[time][key]}</u>"
                diff_old += convert_ruz_lesson(d_old)
                diff_new += convert_ruz_lesson(d_new)
            else:
                diff_new += f"🔸 <b>{lesson['begin']}-{lesson['end']}, {lesson['discipline']}</b>\n" \
                      f"<i>{lesson['work']}, {lesson['lecturer']}, {lesson['auditorium']}</i>\n"
    if diff_count == 1:
        diff_old += '...\n'
        diff_new += '...\n'
    diff = f"⭕ <i>Было:</i>\n{diff_old}" \
           f"♻ <i>Cтало:</i>\n{diff_new}\n"
    return diff


log.info('Модуль ruz загружен')