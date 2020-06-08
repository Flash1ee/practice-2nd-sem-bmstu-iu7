import asyncio
from telethon import TelegramClient, events

import json

cfg = json.load(open("config.json", encoding="UTF-8"))

# Настраиваем прокси и клиента
client = None
if "http_proxy" in cfg.keys() and cfg["http_proxy"]:
    import socks
    client = TelegramClient('session', cfg["api_id"], cfg["api_hash"],
                            proxy=(socks.HTTP, cfg["http_proxy_url"]["host"], cfg["http_proxy_url"]["port"]))
else:
    client = TelegramClient('session', cfg["api_id"], cfg["api_hash"])

# Загружаем тесты
tests = json.load(open("tests.json", encoding="UTF-8"))
# текущий тест
current_test = 0


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def message_handler(event):
    """
        обработка входящих сообщений
    """
    global current_test
    tests[current_test].append(event.message.message)
    tests[current_test].append(
        tests[current_test][1].lower() in event.message.message.lower())


async def main():
    """
        основной цикл тестирования
    """
    global current_test
    while current_test < len(tests):
        await client.send_message(cfg["bot_user_name"], tests[current_test][0])
        await asyncio.sleep(cfg["bot_wait_time"])
        current_test += 1

# запускаем тестирование
client.start()
client.loop.run_until_complete(main())

# Считаем тикеты
len_tests = len(tests)
passed_tests = len(list(filter(lambda x: len(x) == 4 and x[3], tests)))

# Выводим тесты
filtered_tests = tests
if cfg['show_commands'] == "no":
    filtered_tests = []
elif cfg['show_commands'] == "failed":
    filtered_tests = list(filter(lambda x: len(x) != 4 or not x[3], tests))
elif cfg['show_commands'] == "all":
    filtered_tests = tests
else:
    print("UNDEFINED show_commands parametr")

for test in filtered_tests:
    print("======================")
    print(f"Комманда бота: {test[0]}")
    print(f"Ожидается: {test[1]}")
    if len(test) == 4:
        print(f"Ответ бота: {test[2]}")
        print(f"Успешно: {test[3]}")
    else:
        print("Бот отказался отвечать")
    print("======================")


print()
print(f"Пройдено {passed_tests} из {len_tests}")
