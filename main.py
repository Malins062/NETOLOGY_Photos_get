# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
from tabulate import tabulate
from pprint import pprint
import yadisk

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- ФОТОКОПИРОВАНИЕ НА СЕРВИС "ЯНДЕКС ДИСК" ---'


def command_l():
    """
    Отработка команды - "l", вывод списка документов в картотеке
    :return:
    """
    list_docs(documents, '- СПИСОК ВСЕХ ДОКУМЕНТОВ В КАРТОТЕКЕ -')


def command_p():
    """
    Отработка команды - "p", поиск владельца по номеру документа и вывод на экран
    :return:
    """
    print('\n- ПОИСК ВЛАДЕЛЬЦА ПО НОМЕРУ ДОКУМЕНТА -')
    number = input('Введите номер документа для поиска: ')
    filter_docs = search_value(documents, number)
    if len(filter_docs) > 0:
        list_docs(filter_docs, f'Результаты поиска в картотеке по номеру документа - "{number}":')
    else:
        print(f'Владелец документа с номером - {number}, в картотеке не найден!\n')


def command_s():
    """
    Отработка команды - "s", вывод на экран местоположения документа в архиве
    :return:
    """
    print('\n- ПОИСК МЕСТА РАСПОЛОЖЕНИЯ ДОКУМЕНТА В АРХИВЕ, ПО ЕГО НОМЕРУ -')
    number = input('Введите номер документа для поиска: ')
    filter_docs = search_value(directories, number)
    if len(filter_docs) > 0:
        for item in filter_docs:
            item[0] = 'Ячейка ' + item[0] + ' - '
            item[1] = '№ документа: ' + item[1]
        list_docs(filter_docs, f'Результаты поиска места расположения документа, по его номеру - "{number}":')
    else:
        print(f'Документ с номером - {number}, в архиве не найден!\n')


def command_a():
    """
    Отработка команды - "a", добавление нового документа в картотеку
    :return:
    """
    print('\n- ДОБАВЛЕНИЕ НОВОГО ДОКУМЕНТА В КАРТОТЕКУ -')
    name_shelf = input('Ввведите наименование ячейки, в которую будет помещен документ: ')
    if name_shelf not in directories.keys():
        print(f'\n*** Ячейки - {name_shelf}, в архиве не cуществует! ***\n')
        print(f'Введите соответствующую команду в основном меню для создания ячейки.\n')
    else:
        print('Ввведите сведения о документе, помещаемого в картотеку')
        doc_number = input('\t- номер: ')
        doc_type = input('\t- тип: ')
        doc_name = input('\t- имя владельца: ')
        documents.append({'type': doc_type, 'name': doc_name, 'number': doc_number})
        directories[name_shelf].append(doc_number)
        print('Данные в картотеку успешно внесены.\n')


def command_d():
    """
    Отработка команды - "d", полное удаление документа из картотеки
    :return:
    """
    print('\n- УДАЛЕНИЕ ДОКУМЕНТА ИЗ КАРТОТЕКИ -')
    number = input('Ввведите номер удаляемого документа: ')
    if len(search_value(documents, number)) == 0:
        print(f'\n*** Документ - "{number}", в картотеке не найден! ***\n')
    else:
        # Удаления документа из картотеки
        for value in documents:
            if value['number'] == number:
                documents.remove(value)
        # Удаление номера местоположения документа из архива
        del_doc_shelf(number)
        print(f'Документ "{number}" удален.\n')


def command_m():
    """
    Отработка команды - "m", перемещение документа из одной ячейки в другую
    :return:
    """
    print('\n- ПЕРЕМЕЩЕНИЕ ДОКУМЕНТА В АРХИВЕ -')
    number = input('Ввведите номер перемещаемого документа: ')
    if len(search_value(documents, number)) == 0:
        print(f'\n*** Документ - "{number}", в картотеке не найден! ***\n')
    else:
        shelf = input('Ввведите номер новой ячейки месторасположения документа: ')
        if shelf in directories:
            # Удаление номера местоположения документа из архива
            del_doc_shelf(number)
            # Добавление документа в другую ячейку
            directories[shelf].append(number)
            print(f'Документ "{number}" перемещен в ячейку {shelf}.\n')
        else:
            print(f'\n*** Ячейка - "{shelf}", в архиве не найдена! ***\n')


def command_as():
    """
    Отработка команды - "as", созданние новой ячейки в архиве для хранения документов
    :return:
    """
    print('\n- ДОБАВЛЕНИЕ НОВОЙ ЯЧЕЙКИ ДЛЯ ХРАНЕНИЯ ДОКУМЕНТОВ В АРХИВЕ -')
    shelf = input('Ввведите номер вновь создаваемой ячейки в архиве: ')
    if shelf not in directories:
        # Добавление новой ячейки
        directories[shelf] = []
        print(f'Новая ячейка - "{shelf}" в архиве успешно создана.\n')
    else:
        print(f'\n*** Ячейка - "{shelf}", уже существует в архиве! ***\n')


def del_doc_shelf(number):
    """
    Фушкция удаления документа с номером number из ячеек архива
    :param number: номер удаляемого документа
    :return: cnt - количество удаленных документов из ячеек архива
    """
    cnt = 0
    for value in directories.values():
        for num in value:
            if num == number:
                value.remove(num)
                cnt += 1
    return cnt


def list_docs(lst, title=''):
    """
    Вывод представленного списка на экран в табличном виде, c подсчетом общего количества записей в списке
    :param lst: список, выводимый в виде таблицы на экран командой print()
    :param title: заголовок списка, выводится перед таблицей
    :return:
    """
    count_records = len(lst)
    print(f'\n{title}')
    print(tabulate(lst))
    print(f'Всего записей: {count_records}.\n')


def search_value(lst_dict, value):
    """
    Функция поиска Value в словаре (списке словарей) lst_dict, по их значениям.
    :param lst_dict: словарь (список словарей), в котором осуществляется поиск value в значениях словаря
    :param value: искомое значение в преставленном списке значений
    :return: Возвращает список класса list, если Value не найдено возвращает пустой список
    """
    if isinstance(lst_dict, dict):
        filter_values = [[n, value] for n, num in lst_dict.items() if value in num]
    else:
        filter_values = [rec for rec in lst_dict if value in rec.values()]
    return filter_values


# Список допустимых команд программы, их описание и определение запускаемых функций
commands = {'p': ('вывести владельца документа, которому он принадлежит...;', command_p),
            's': ('вывести местоположения документа в архиве...;',  command_s),
            'l': ('вывод списка фотографий;', command_l),
            'a': ('добавление нового документа в каталог...;', command_a),
            'd': ('удаление документа из архива...;', command_d),
            'm': ('переместить документ на другое место в ахиве...;', command_m),
            'as': ('добавить новое место в архиве...;', command_as),
            'x': ('выход из программы.\n', exit)
            }


def main(cmd):
    """
    Функция основного меню, с реагирование на команды поданного списка cmd
    :param cmd: команды меню и функции реагирования к каждой команде
    :return:
    """

    def invalid_command():
        """
        Вывод ошибки на экран, при вводе неверной команды
        :return:
        """
        print(f'\n*** ОШИБКА! Выполнение команды "{command}" не допустимо! ***\n')

    while True:
        os.system('cls||clear')
        print(f'{TITLE_PROGRAM}\n')

        print('Команды пользователя:')
        for key_command, name_command in commands.items():
            print(f'\t{key_command} – {name_command[0]}')

        print('Введите команду:', end=' ')
        command = str(input().strip()).lower()
        cmd.get(command, [None, invalid_command])[1]()
        input('Для продолжения работы нажмите клавишу "Enter"...')


if __name__ == '__main__':
    main(commands)

