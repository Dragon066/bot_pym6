from botpackage import *
if config['MODULES']['holidays']:
    from modules.holidays import get_holidays
if config['MODULES']['ruz']:
    from modules.ruz import update_ruz
if config['MODULES']['gmail']:
    from modules.gmail import gmail_update_msgs


try:
    if config['MODULES']['ruz']:
        scheduler.add_job(update_ruz, 'interval', minutes=5)
    if config['MODULES']['gmail']:
        scheduler.add_job(gmail_update_msgs, 'interval', minutes=1)

    async def sched_holidays():
        await bot.send_message(ADM_GROUP, get_holidays())

    async def get_stats_():
        await bot.send_photo(chat_id=ADM_GROUP, photo=get_stat_plot(), caption=get_stats())
        clear_stats()

    async def get_facts_():
        text = '<b>❔ А вы знали, что...</b>\n\n➡️ ' + get_random_fact(1)[0]
        await bot.send_message(ADM_GROUP, text)

    async def get_sperm_top():
        await bot.send_message(ADM_GROUP, sperm_get_top())

    async def get_weather():
        capt = '🌪 <b>Погодка на недельку, мяу</b>\n\n'
        info = get_weather_raw()[0]
        capt += f"<b>Сегодня</b>, {info['day']} {info['month']}\n\n"
        capt += get_weather_info(info)
        info = get_weather_raw()[1]
        capt += f"<b>Завтра</b>, {info['day']} {info['month']}\n\n"
        capt += get_weather_info(info)
        await bot.send_photo(chat_id=ADM_GROUP, photo=get_weather_stat(get_weather_raw()), caption=capt)

    async def sched_funcs_00():
        if SEND_HD:
            if config['MODULES']['holidays']:
                await sched_holidays()
        if SEND_STATS:
            await get_stats_()
        if SEND_TOPS:
            await get_sperm_top()

    if SEND_WEATHER:
        scheduler.add_job(get_weather, 'cron', hour=6, minute=0)

    if SEND_FACTS:
        scheduler.add_job(get_facts_, 'interval', hours=5)


    scheduler.add_job(sched_funcs_00, 'cron', hour=0, minute=0)

    log.info('Планировщик запущен')
except Exception as err:
    log.exception('Ошибка при подключении планировщика')
