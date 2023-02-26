from botpackage import *

if config['MODULES']['homework']:
    from modules.homework import *
    update_hw_file()

if config['MODULES']['holidays']:
    from modules.holidays import *

if config['MODULES']['commands']:
    from modules.commands import *

if config['MODULES']['files']:
    from modules.files import *
    update_files()
    
if config['MODULES']['ruz']:
    from modules.ruz import *
    
if config['MODULES']['gmail']:
    from modules.gmail import *
    load_mail()
    
if config['MODULES']['code']:
    from modules.code import *
    
if config['MODULES']['open']:
    from modules.open import *

if config['MODULES']['sched']:
    from modules.sched import *


async def on_startup(dp):
    scheduler.start()
    log.info('Запуск long-polling')
    print(f'Бот запущен за {dt.datetime.now() - UPTIME}')

async def on_shutdown(dp):
    save_hw()
    save_ruz()
    save_mail()
    save_files()
    log.info('Отключение')
    print('Бот отключён')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
