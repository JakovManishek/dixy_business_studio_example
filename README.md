# Dixy-like Streamlit App

Мобильное grocery-приложение в духе клиентского приложения продуктовой сети:

- Streamlit-интерфейс под вертикальный экран смартфона
- SQLite-база и backend-слой для каталога, избранного, корзины и заказов
- сид-данные для демонстрации работы
- автотесты на `unittest`

## Запуск

```powershell
streamlit run app.py
```

## Репозиторий

GitHub-репозиторий проекта:

- `https://github.com/JakovManishek/dixy_business_studio_example`

## Что сделать дальше

Чтобы получить публичную ссылку и отправить ее другу:

1. Открой `https://share.streamlit.io/`.
2. Нажми `Create app`.
3. Выбери репозиторий `JakovManishek/dixy_business_studio_example`.
4. Выбери ветку `main`.
5. Укажи entrypoint-файл `app.py`.
6. Нажми `Deploy`.
7. После запуска получишь публичную ссылку вида `https://...streamlit.app/`.

Важно:

- база SQLite в этом проекте локальная и живет в файле `data/dixy_clone.db`;
- на Streamlit Community Cloud файловая система временная, поэтому данные могут сбрасываться после перезапуска или redeploy;
- для демо и показа другу этого обычно достаточно;
- если нужен постоянный прод-режим, лучше вынести данные в внешнюю БД.

## Тесты

```powershell
python -m unittest discover -s tests -v
```
