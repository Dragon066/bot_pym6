from botpackage import *


async def on_startup(dp):
    scheduler.start()
    log.info('Запуск long-polling')
    print(f'Бот запущен за {dt.datetime.now() - UPTIME}')

async def on_shutdown(dp):
    save_hw()
    save_ruz()
    save_mail()
    save_files()
    save_sperm()
    log.info('Отключение')
    print('Бот отключён')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
