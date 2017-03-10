# -*- coding: utf-8 -*-
import subprocess
import commands
import pytest
from hamcrest import *
import random
from conftest import *


def parse_header(stdoutput):
    ''' Распарсить в dict заголовочную часть вывода программы (первые 3и строчки)
    '''
    return {i.split(":")[0]:i.split(":")[1].strip() for i in stdoutput[:3]}


def parse_body(stdoutput):
    ''' Распарсить в list of dictionaries теловывода программы
    '''
    body = tuple(stdoutput[3:])
    result = []
    i = 0
    while len(body) > i:
        result.append({j.split(":")[0]:j.split(":")[1].strip() for j in body[i:i+2]})
        i = i + 2
    return result


def return_result(dies):
    ''' Тестовый оракул алгоритма подсчета очков за бросок
    '''
    list = dies.split()
    if set(list) == set(["1", "2", "3", "4", "5"]):
        return 150
    dices = [int(i)*10 for i in list if i in ["1"]] + \
            [int(i) for i in list if i in ["5"]]
    return sum(dices)


def exec_cmd(cmd):
    (exitcode, stdoutput) = commands.getstatusoutput(cmd)
    if exitcode == 0:
        return stdoutput.split("\n")
    else:
        raise Exception("Command %s return exitcode %s " % (cmd, exitcode))





@pytest.mark.parametrize('arguments, error_text',
                         [('', "Wrong arguments count: 0"),
                          ('16', 'Wrong arguments count: 1'),
                          ('16 1', 'Wrong arguments count: 2'),
                          ('3 3 5 6', 'Wrong arguments count: 4'),
                          ('0 1 1', 'Wrong arguments'),
                          ('1 0 1', 'Wrong arguments'),
                          ('1 1 0', 'Wrong arguments'),
                          ('a b c', 'Wrong arguments'),
                          ('1000000 4 5', 'Error: number of turns > 999999'),
                          ('1 2 1', 'Error: minDiceCount > maxDiceCount'),
                          ('1 6 5', 'minDiceCount range error [1..5]'),
                          ('1 5 6', 'maxDiceCount range error [1..5]'),
                          ('1 1 20', 'maxDiceCount range error [1..5]'),
                          ('-5 1 20', 'Wrong arguments'),
                          ('5 -1 5', 'Wrong arguments'),
                          ('5 1 -5', 'Wrong arguments')])
def test_that_app_should_return_error_msg_if_arguments_incorrect(app, arguments, error_text):
    ''' Прогрмма на вход принимает 3и аргумента (кол-во бросков, min и max кол-во участвующих в броске кубиков).
    Если аргументы заданы неверно, отображается сообщение ош ошибке
    Tests: Сообщение об ошибке отображается:
        * если не задан ни одного аргумента
        * если не задан один или несколько аргументов
        * если задано больше чем требуется аргументов
        * если кол-во бросков = 0
        * если кол-во бросков = 1000000 или больше
        * если min или max кол-во кубиков = 0
        * если min кол-во кубиков = 6 или больше
        * если max кол-во кубиков = 6 или больше
        * если min кол-во бросков > max кол-во бросков
        * если переданы строки, которые нельзя привести к int
        - если переданы числа не в двоичной системе
        * если какой-либо из аргументов = отрицательному числу
    '''
    cmd = "%s %s" % (app, arguments)
    (exitcode, stdoutput) = commands.getstatusoutput(cmd)

    assert stdoutput == error_text


@pytest.mark.parametrize('arguments',
                         ['"10" "2" "5"',
                          '10.1 2.9 5.0',
                          '010 02 05',
                          '10, 2, 5'])
def test_that_app_should_parse_valid_arguments(app, arguments):
    ''' Прогрмма на вход принимает 3и аргумента типа int разделенных пробелом
    Tests:
        * Прогрмаау приимает аргументы в строковом виде, если их можно привести к int
        * Прогрмаау приимает аргументы в десятичном виде, округляя их к нижней границе
        * Программа принимает аргументы перечисленые через  пробел и запятую
    '''
    output = exec_cmd("%s %s" % (app, arguments))
    output_header = parse_header(output)
    output_body = parse_body(output)

    assert_that(output_header["Number of turns"], equal_to('10'))
    assert_that(output_header["Minimum number of dices"], equal_to('2'))
    assert_that(output_header["Maximum number of dices"], equal_to('5'))
    assert_that(output_body, has_length(10))


@pytest.mark.parametrize('number_of_throw',
                         [1, 10, 1000, 999999])
def test_that_number_of_throw_equal_number_of_result_pairs(app, number_of_throw):
    '''
    Tests:
        * Программа выводит переданное ей кол-во бросков в заголовочной части
        * Кол-во пар результатов бросков в выводе = переданному кол-ву бросков
        * Минимальное кол-во бросков = 1, максимальное = 999999
        * Выделен 1 класс эквивалентности [1 - 999999]
    '''
    output = exec_cmd("%s %s 1 1" % (app, number_of_throw))
    output_header = parse_header(output)
    output_body = parse_body(output)

    assert_that(output_header["Number of turns"], equal_to(str(number_of_throw)))
    assert len(output_body) == number_of_throw


@pytest.mark.parametrize('number_of_throw, min_dices, max_dices',
                         [(1, 1, 1),
                          (1, 5, 5),
                          (100000, 1, 5),
                          (100, 2, 4)])
def test_that_number_of_dices_should_greater_than_min_dices_but_less_than_max_dices(app, number_of_throw, min_dices, max_dices):
    '''Для каждого броска приложение выводит в консоль выпавшие грани на кубиках
    Tests:
        * Программа выводит переданные min_dices и max_dices в заголовочной части
        * Минимальное кол-во участвующих кубиков 1
        * Максимальное кол-во участвующих кубиков 5
        * Кол-во кубиков в броске не может быть меньше min_dices
        * Кол-во кубиков в броске не может быть больше max_dices
    '''
    output = exec_cmd("%s %s %s %s" % (app, number_of_throw, min_dices, max_dices))
    output_header = parse_header(output)
    output_body = parse_body(output)

    assert_that(output_header["Minimum number of dices"], equal_to(str(min_dices)))
    assert_that(output_header["Maximum number of dices"], equal_to(str(max_dices)))

    for i in output_body:
        assert_that(i['Dices'].split(), has_length(greater_than_or_equal_to(min_dices)),
                    'Real numder of dices = %s, is less than min_dices = %s for Dice = %s' % (len(i['Dices'].split()), min_dices, i))
        assert_that(i['Dices'].split(), has_length(less_than_or_equal_to(max_dices)),
                    'Real numder of dices = %s, is greater than max_dices = %s for Dice = %s' % (len(i['Dices'].split()), max_dices, i))


@pytest.mark.parametrize('number_of_throw, min_dices, max_dices',
                         [(100, 1, 5),
                          (1000, 1, 5),
                          (100000, 1, 5)])
def test_that_every_dices_only_contains_any_of_1_2_3_4_5_6(app, number_of_throw, min_dices, max_dices):
    '''Для каждого броска приложение выводит в консоль выпавшие грани на кубиках
    Tests:
        * Значения выпавшее на кубиках могут быть только  "1", "2", "3", "4", "5" или "6"
    '''
    output = exec_cmd("%s %s %s %s" % (app, number_of_throw, min_dices, max_dices))
    output_body = parse_body(output)
    for i in output_body:
        assert i['Result'] != None
        assert_that(i['Dices'].split(), only_contains(any_of("1", "2", "3", "4", "5", "6")))


@pytest.mark.parametrize('number_of_throw, min_dices, max_dices',
                         [('10', "1", "1"),
                          ('10', "1", "2"),
                          ('10', "1", "3"),
                          ('10', "1", "4"),
                          ('10', '1', "5"),
                          ('10000', '1', "5"),
                          ('999999', '1', "5")])
def test_that_app_should_calculate_the_result_of_the_throws_right(app, number_of_throw, min_dices, max_dices):
    ''' Для каждого броска приложение выводит в консоль результат броска (набранные очки)
    Tests:
        * 1 - приносит 10 очков, 5 - приности 1 очко, остальные грани не приносят очков (2,3,4,6)
        * если выпала специальная комбинация (1,2,3,4,5) - 150 очков (порядок не учитывается)
    '''
    output = exec_cmd("%s %s %s %s" % (app, number_of_throw, min_dices, max_dices))
    output_body = parse_body(output)
    for i in output_body:
        assert_that(int(i['Result']), equal_to(return_result(i['Dices'])),
                    'Incorrect Result = %s for Dice = %s. Expected Result: %s' % (i['Result'], i['Dices'], return_result(i['Dices'])))



def random_arguments():
    ''' Рандомные аргументы коммандной строки запуска программы
    (кол-во бросков, min и max кол-во участвующих в броске кубиков)
    '''
    count = random.randrange(1, 100000)
    min_dices = random.randrange(1, 5)
    max_dices = random.randrange(min_dices, 5)
    return (count, min_dices, max_dices)


@random_test
@pytest.mark.parametrize('number_of_throw, min_dices, max_dices', [random_arguments() for i in xrange(20)])
def test_full_e2e_blackbox_scenario(app, number_of_throw, min_dices, max_dices):
    '''
    '''
    output = exec_cmd("%s %s %s %s" % (app, number_of_throw, min_dices, max_dices))
    output_header = parse_header(output)
    output_body = parse_body(output)

    assert_that(output_header["Number of turns"], equal_to(str(number_of_throw)))
    assert len(output_body) == number_of_throw
    assert_that(output_header["Minimum number of dices"], equal_to(str(min_dices)))
    assert_that(output_header["Maximum number of dices"], equal_to(str(max_dices)))

    for i in output_body:
        assert_that(i['Dices'].split(), has_length(greater_than_or_equal_to(min_dices)),
                    'Real numder of dices = %s, is less than min_dices = %s for Dice = %s' % (len(i['Dices'].split()), min_dices, i))
        assert_that(i['Dices'].split(), has_length(less_than_or_equal_to(max_dices)),
                    'Real numder of dices = %s, is greater than max_dices = %s for Dice = %s' % (len(i['Dices'].split()), max_dices, i))
        assert_that(i['Dices'].split(), only_contains(any_of("1", "2", "3", "4", "5", "6")))
        assert_that(int(i['Result']), equal_to(return_result(i['Dices'])),
                    'Incorrect Result = %s for Dice = %s. Expected Result: %s' % (i['Result'], i['Dices'], return_result(i['Dices'])))

