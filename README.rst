============
GURGEN TESTS
============


NOTES
=====

Я работаю на OS X, поэтому задание делал на docker с ubuntu, отсюда и два варианта запуска тестов

Фреймворк запуска тестов - py.test

Так как нет доступа к коду приложения, тесты писались исходя из подхода blackbox. Поэтому тесты на алгоритм подсчета
очков за броски ("test_that_app_should_calculate_the_result_of_the_throws_right") проверяются на основе тестового
оракула, реализующего такой же алгоритм  - что является очень плохой практикой для тестов. Рекомендуется тесты
на эту функциональность сделать на уровне unit тестов. Так как на текущем уровне я не могу гарантировать что среди
тестов, например выпадет последовательность приносящая 150 очков (хотя вероятность этого приблежается к 100% c ростом
кол-ва бросков)

Среди тестов, есть тесты с полностью рандомными входными параметрами - как попытка (a)найти больше ошибок,
внесенных искусственно и не выявляемыми эвристиками тест-дизайна, (b) из-за невозможности влиять на значения выпавших граней,
которые генерятся рандомно. Такие тесты по-умолчанию будут пропущены, но их можно запустить добавив в строку запуска
"--run_with_random_tests"




RUN IN DOCKER
=============

1. Выполнить сборку образа

.. code-block:: console

    cd gurgen_tests
    docker build -t gurgen_tests .

При этом, до сборки контейнера в него нужно положить тестируемое приложение (по умолчанию папка /src)

2. Запустить тесты в контейнере

.. code-block:: console

    docker run -it gurgen_tests /usr/local/bin/py.test -v -l test_gurgen_app.py --path <PATH_TO_APP>

    <PATH_TO_APP> -  путь до тестируемого файла программы gurgen.
    Если запустить без атрибута "--path" - то тесты запустятся на эталонной версии приложения "gurgen_0"

    Пример:
    docker run -it gurgen_tests /usr/local/bin/py.test -v -l  test_gurgen_app.py --path /app/src/gurgen_0

    docker run -it gurgen_tests /usr/local/bin/py.test -v -l  test_gurgen_app.py --path /app/src/gurgen_0 --run_with_random_tests


LOCAL RUN
=========

1. Установить зависимости проекта

.. code-block:: console

    cd gurgen_tests
    pip install --upgrade -r requirements.txt

2. Запустить тесты коммандой:

.. code-block:: console

    py.test -v -l test_gurgen_app.py --path <PATH_TO_APP>

    <PATH_TO_APP> -  абсолютный путь до тестируемого файла программы gurgen.
    Если запустить без атрибута "--path" - то тесты запустятся на эталонной версии приложения "gurgen_0"

    Пример:
    py.test -v -l test_gurgen_app.py --path ./src/gurgen_0


Если путь до py.test не прописан в PATH, то его следует указать в комманде запуска (узнать его можно командой "which py.test"):

.. code-block:: console

    Пример:
    /usr/local/bin/py.test -v -l test_gurgen_app.py ./src/gurgen_0


RESULTS
=======

Результаты прохождения тестов PASSED или FAILED (+ трейс и AssertionError).
Если нужно сохранить результаты выполнения тестов, следует запустить py.test c атрибутом "--pastebin=all"

.. code-block:: console

    Пример:
    docker run -it gurgen_tests /usr/local/bin/py.test -v -l --pastebin=all test_gurgen_app.py --path /app/src/gurgen_0


BUGS
====

gurgen_1
--------
* Приложение возвращает exitcode = 35072 при больших значениях количества бросков
Воспроизводится на комманде: '/app/src/gurgen_1 999999 1 1'

gurgen_2
--------
* Приложение некорректно подсчитывает набранные очки при больших значениях количества бросков (>10000)
Пример:
- Incorrect Result = 5 for Dice = 3 4 3 6. Expected Result: 0
- Incorrect Result = 5 for Dice = 3 4. Expected Result: 0
- Incorrect Result = 15 for Dice = 4 1 3 3. Expected Result: 10

Есть подозрения, что за 4 дают 5ть очков, хотя должны давать 0

gurgen_3
--------
* Приложение некорректно подсчитывает набранные очки при больших значениях количества бросков (не учитывает что за
бонусную комбинацию 1 2 3 4 5 должны давать 150 очков а не 15)

Пример:
Incorrect Result = 15 for Dice = 1 3 2 5 4. Expected Result: 150

gurgen_4
--------
* При больших значениях количества бросков (> 10000), приложение производит больше бросков чем передано пользователем в max_dice

Пример:
Real numder of dices = 6, is greater than max_dices = 5 for Dice = {'Dices': '3 1 4 1 3 6', 'Result': '20'}

gurgen_5
--------
* При больших значениях кол-ва бросков (> 1000), на некоторых костях выпадает 7ка, хотя граней всего 6ть.


gurgen_6
--------
* При больших значениях кол-ва бросков, приложение производит меньше бросков чем передано польователем (меньше на 8мь)

Воспроизводится на комманде: '/app/src/gurgen_6 1000 1 1'
Пример: 992 вместо 1000
