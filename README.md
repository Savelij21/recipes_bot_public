### Телеграм бот с рецептами

Ссылка на бота: https://t.me/zhzhgis_recipes_bot

На ноябрь 2024 - 1260 пользователей в базе (~1000 активных)  

Телеграм бот на фреймворке aiogram, используется надстройка aiogram_dialog для более удобного конструктора меню, 
бэкенд для работы с базой рецептов - Django + DRF. Получение данных в боте из Django - через http запросы.

Доступ к самим рецептам открыт только для участников закрытого канала, но посмотреть само меню может любой пользователь.
Новые рецепты, ингредиенты добавляются через админ панель Django. Реализована возможность рассылать контент пользователям. 

Реализовано резервное копирование БД и сохранение
копии на удаленное файловое хранилище YandexObjectStorage.

В истории отсутствуют коммиты, так как проект разрабатывался в другом репозитории, на этот репозиторий был перенесен для 
сокрытия потенциально открытых во время разработки данных.