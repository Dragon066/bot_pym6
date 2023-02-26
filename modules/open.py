from botpackage import *
from pdf2image import convert_from_path, pdfinfo_from_path
import aspose.words as aw


@dp.message_handler(commands=['open'])
async def com_open(msg):
    if checkright(msg) and msg.reply_to_message:
        if 'document' in msg.reply_to_message:
            available = ['doc', 'docx', 'pdf']
            filename = msg.reply_to_message.document.file_name
            ext = filename[filename.rfind('.') + 1:]
            path = ''
            if ext in available:
                gen_msg = await msg.answer(f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\nКоличество страниц: <i>вычисление...</i>')
            else:
                await msg.answer(f'К сожалению, я не работаю с форматом {ext.upper()}')
                return None
            try:
                from modules.files import FILES
                for key, value in FILES.items():
                    if value['id'] == msg.reply_to_message.document.file_id:
                        path = key
                        break
                if not path:
                    if not os.path.exists('media/temp'):
                        os.mkdir('media/temp')
                    path = f'media/temp/{filename}'
                    file = await bot.get_file(msg.reply_to_message.document.file_id)
                    await bot.download_file(file.file_path, path)
                    from modules.files import update_files
                    FILES[path]['id'] = msg.reply_to_message.document.file_id
                    update_files()
                if ext == 'pdf':
                    imgs = []
                    pages = pdfinfo_from_path(path)['Pages']
                    await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                                                text=f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\nКоличество страниц: <i>{pages}</i>')
                    images = convert_from_path(path)#, poppler_path=r'C:\Program Files\poppler-23.01.0\Library\bin')
                    for i, image in enumerate(images[:10]):
                        await asyncio.sleep(0.0001)
                        imgs.append(BytesIO())
                        image.save(imgs[i], 'PNG')
                        imgs[i].seek(0)
                    media = types.MediaGroup()
                    caption = f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\nКоличество страниц: {pages}'
                    for i, image in enumerate(imgs[:10]):
                        media.attach_photo(image, caption=caption if i == 0 else None)
                    await bot.send_chat_action(msg.chat.id, types.ChatActions.UPLOAD_DOCUMENT)
                    await bot.send_media_group(media=media, chat_id=msg.chat.id)
                    await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                elif ext == 'docx' or ext == 'doc':
                    imgs = []
                    doc = aw.Document(path)
                    options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)
                    await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                                                text=f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\nКоличество страниц: <i>{doc.page_count}</i>')
                    for page in range(doc.page_count):
                        await asyncio.sleep(0.0001)
                        imgs.append(BytesIO())
                        options.page_set = aw.saving.PageSet(page)
                        doc.save(imgs[page], options)
                        imgs[page].seek(0)
                    media = types.MediaGroup()
                    caption = f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\nКоличество страниц: {doc.page_count}'
                    for i, image in enumerate(imgs[:10]):
                        media.attach_photo(image, caption=caption if i == 0 else None)
                    await bot.send_chat_action(msg.chat.id, types.ChatActions.UPLOAD_DOCUMENT)
                    await bot.send_media_group(media=media, chat_id=msg.chat.id)
                    await bot.delete_message(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id)
                else:
                    await msg.answer('К сожалению, я не работаю с этим форматом')
            except Exception as ex:
                await bot.edit_message_text(chat_id=gen_msg.chat.id, message_id=gen_msg.message_id,
                                            text=f'<b>{filename}</b>, <i>{ext.upper()} -> PNG</i>\n'
                                                 f'Количество страниц: <i>-</i>\n'
                                                 f'К сожалению, возникла ошибка при преобразовании файла:\n'
                                                 f'<i>{ex}</i>')
                log.exception('Ошибка open')


log.info('Модуль open загружен')