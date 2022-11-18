# api_yamdb

## Технологии:
![Python](https://img.shields.io/badge/Python-3.7-green)
![Django](https://img.shields.io/badge/Django-2.2.12-green)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
https://github.com/SleekHarpy/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```Python
python manage.py makemigrations reviews
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```



### Авторы
- [Влад Шевцов](https://github.com/SleekHarpy)
- [Павлов-Теремок Дмитрий](https://github.com/LunarBirdMYT)
- [Иван Шайнога](https://github.com/IvanShaynoga)
