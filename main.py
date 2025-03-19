import random
from . import chat
from pyrogram import Client, filters
from string import Template
from utils import dirs, json_helper


def launch(bot, module_name):
    config = json_helper.read(dirs.MODULES_PATH + module_name + '/config.json')

    if 'api_key' in config:
        subconscious = chat.Subconscious(config['api_key'])

    @bot.app.on_message(filters.command('autoreply', prefixes='.') & filters.me)
    def autoreply(client, message):
        data = message.text.split(' ', maxsplit=2)
        mode = data[1]

        if mode == 'on':
            prompt = data[2]
            
            config['chats'][str(message.chat.id)] = {'prompt': prompt}
            json_helper.write(dirs.MODULES_PATH + module_name + '/config.json', config)

            message.delete()
        elif mode == 'off':
            config['chats'].pop(str(message.chat.id))
            json_helper.write(dirs.MODULES_PATH + module_name + '/config.json', config)

            message.delete()
        elif mode == 'set_api_key':
            api_key = data[2]

            config['api_key'] = api_key
            json_helper.write(dirs.MODULES_PATH + module_name + '/config.json', config)

            subconscious = chat.Subconscious(config['api_key'])

            with open(dirs.MODULES_PATH + module_name + '/templates/success.html', encoding='utf-8') as f:
                message.edit(f.read())
    
    @bot.app.on_message(group=random.randint(1, 9999))
    def on_message(client, message):
        print(message.text)
        for i in config['chats']:
            if str(message.from_user.id) == str(i) and message.from_user.id != client.me.id:
                try:
                    template = config['chats'][str(message.from_user.id)]['prompt']
                    prompt = f'''
                    Ты автоответчик, твоего собеседника зовут {message.from_user.first_name}
                    Тебе задали следующую инструкцию: {template}. Пришло сообщение: {message.text}, твой собеседник ждет ответа!
                    Как бы ты ответил на данное сообщение?
                    Если тебя спросят кто ты, отвечай, что ты - автоответчик
                    '''

                    response = subconscious.stream(prompt, subconscious)
                    
                    message.reply(response)
                except Exception as e:
                    print(e)
