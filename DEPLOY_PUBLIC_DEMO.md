# Публичная демонстрация сайта

В проект добавлены `render.yaml` и `Procfile` для развёртывания отдельной публичной демо-версии.

## Почему отдельная база

Публичная демо-версия запускается с `PUBLIC_DEMO_MODE=True` и отдельной PostgreSQL-базой. Она не показывает приватные Telegram-профили и не использует локальную `fitness_bot.db`.

## Быстрый запуск

1. Создай репозиторий из этой папки на GitHub/GitLab.
2. В Render выбери **New → Blueprint** и укажи репозиторий.
3. Render прочитает `render.yaml`, создаст web service и отдельную demo database.
4. Дождись deploy и отправь человеку URL вида `https://gym-helper-public-demo.onrender.com`.

Демо URL создаётся самим Render после deploy, поэтому заранее вписать его в проект нельзя.

## Приватная рабочая версия

Для боевой версии используй отдельный сервис с:

- `PUBLIC_DEMO_MODE=False`;
- PostgreSQL с приватными данными;
- `BOT_TOKEN` и `OPENAI_API_KEY` только в секретах Render;
- отдельным постоянным HTTPS-адресом Mini App.
