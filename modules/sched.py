from botpackage import *
if config['MODULES']['holidays']:
    from modules.holidays import get_holidays
if config['MODULES']['ruz']:
    from modules.ruz import update_ruz
if config['MODULES']['gmail']:
    from modules.gmail import gmail_update_msgs


try:
    if config['MODULES']['ruz']:
        scheduler.add_job(update_ruz, 'interval', minutes=10)
    if config['MODULES']['gmail']:
        scheduler.add_job(gmail_update_msgs, 'interval', minutes=10)

    async def sched_holidays():
        await bot.send_message(ADM_GROUP, get_holidays())

    if SEND_HD:
        if config['MODULES']['holidays']:
            scheduler.add_job(sched_holidays, 'cron', hour=0, minute=1)

    log.info('Планировщик запущен')
except Exception as err:
    log.exception('Ошибка при подключении планировщика')