# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
import pandas as pd
from pprint import pprint
from vk_api import VKUser

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ФОТОМАТЕРИАЛОВ НА ОБЛАЧНЫЙ СЕРВИС ---'

# Список допустимых команд программы, их описание и назначение необходимых параметров для каждого пункта
commands = [{'1': ['Яндекс диск;', 1, {'name': 'Яндекс диск', 'url': 'https://yandex.ru/dev/disk/poligon/'}],
             '2': ['Google drive;', 2, {'name': 'GoogleDrive API', 'url': ''}],
             '0': ['выход из программы.\n', 0]
             },
            {'1': ['ВКонтакте;', 1, {'name': 'ВКонтакте', 'url': 'https://api.vk.com/method/', 'version': '5.131'}],
             '2': ['Однокласники;', 2, {'name': 'Одноклассники', 'url': 'https://api.ok.ru/api/'}],
             '3': ['Инстаграмм', 3, {'name': 'Инстаграмм', 'url': 'https://www.instagram.com/developer/'}],
             '9': ['возврат в предыдущее меню;', 9, 'Up'],
             '0': ['выход из программы.\n', 0]
             }
            ]


def init_screen():
    """
    Функция очистки экрана пользователя и вывода заставки
    """
    os.system('cls||clear')
    print(f'{TITLE_PROGRAM}\n')


def main(cmd):
    """
    Функция основного меню и подменю, с реагированием на команды поданного списка cmd
    :param cmd: команды меню и необходимые значения для реагирования к каждой команде
    """

    # Признак не существующей команды меню
    error_command = 'Invalid'

    def invalid_command(err_cmd):
        """
        Вывод ошибки на экран, при вводе неверной команды
        :return:
        """
        print(f'\n*** ОШИБКА! Выполнение команды "{err_cmd}" не допустимо! ***\n')
        input('Для продолжения работы нажмите клавишу "Enter"...')

    # Параметры текущей, выбранной команды:
    #       destination - ресурс назначения комирования фотографий
    #       resource - ресурс откуда необходимо копировать фотографии
    status_command = {'destination': {},
                      'resource': {}
                      }
    is_exit = False
    while not is_exit:
        init_screen()
        print('Выберите ресурс назначения копирования фотографий:')
        for key_command, name_command in cmd[0].items():
            print(f'\t{key_command} – {name_command[0]}')

        print('Введите команду:', end=' ')
        command = str(input().strip()).lower()
        status_command['destination'] = cmd[0].get(command, error_command)

        # Проверка команды подменю - выбран ли пункт ВЫХОД
        if status_command['destination'][1] == 0:
            is_exit = True
        # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
        elif status_command['destination'] == error_command:
            invalid_command(command)
        else:
            is_menu_out = False
            while not is_menu_out:
                init_screen()
                print(f'Хранилище импортируемых фотографий: {status_command["destination"][2]["name"]} - '
                      f'{status_command["destination"][2]["url"]}.')
                print('Выберите источник копирования фотографий:')
                for key_command, name_command in cmd[1].items():
                    print(f'\t{key_command} – {name_command[0]}')

                print('Введите команду:', end=' ')
                command = str(input().strip()).lower()
                status_command['resource'] = cmd[1].get(command, error_command)

                # Проверка команды подменю - выбран ли пункт ВЫХОД
                if status_command['resource'][1] == 0:
                    is_exit = True
                    is_menu_out = True
                # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
                elif status_command['resource'] == error_command:
                    invalid_command(command)
                # Проверка команды подменю - выбран ли пункт ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
                elif status_command['resource'][1] == 9:
                    is_menu_out = True
                else:
                    init_screen()

                    # Ввод необходимых данных ID-пользователя и ключа доступа к ресурсу
                    # data_for_copy = input_data_for_read(status_command["resource"][2])

                    if isinstance(input_data_for_read(status_command["resource"][2]), dict):
                        print(f'\n1. ВХОДНЫЕ ДАННЫЕ.\nРесурс импорта - {status_command["resource"][2]["name"]}\n')
                        files_to_download = photos_get(status_command['resource'][2])

                        print('2. СЧИТАННЫЕ ДАННЫЕ.')
                        if len(files_to_download) > 0:
                            print('\nСписок доступных фотографий для скачивания:')
                            print_list_files(files_to_download)
                        else:
                            print('\nНет доступных фотографий для скачивания!\n')
                            input('Для продолжения работы нажмите клавишу "Enter"...')
    return "До встречи!"


def input_data_for_read(resource):
    """
    Функция ввода дополнительных необходмых параметров чтения с сетевого ресурса:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    :param resource: параметры источника импорта фотографий (name, url, id)
    :return: dict - словарь с итоговыми параметрами resource
    """
    print(f'Источник импорта фотографий: {resource["name"]} - {resource["url"]}.')
    resource["id"] = input('Введите ID пользователя (0 - для отмены): ').strip()
    if resource["id"] == '0':
        return False
    resource["token"] = input('Введите TOKEN пользователя (0 - для отмены): ').strip()
    if resource["token"].strip() == '0':
        return False
    else:
        return {'resource': resource}


def input_data_for_write(destination):
    """
    Функция ввода дополнительных необходмых параметров для загрузки на сетевой ресурс:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    :param destination: параметры хранилища фотографий (name, url, token)
    :return: dict - словарь с итоговыми параметрами destination
    """
    print(f'Хранилище импортируемых фотографий: {destination["name"]} - {destination["url"]}.')
    destination["token"] = input('Введите TOKEN пользователя (0 - для отмены): ').strip()
    if destination["token"].strip() == '0':
        return False
    else:
        return {'destination': destination}


def photos_get(resource) -> list:
    """
    Функция считывания списка доступных файлов для скачивания с сетевых ресурсов
    :param resource: входные параметры выбранного сетевого ресурса
    :return: список доступных файлов для скачивания c заданного сетевого ресурса,
    если ресурс не в спсике допустимых - возращаект пустой список
    """

    if resource["name"] == 'ВКонтакте':
        resource['id'] = 552934290
        resource['token'] = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'

        client_vk = VKUser(resource['url'], resource['token'], resource['version'])
        print(client_vk)
        return client_vk.get_photos(resource['id'])
    return []


def print_list_files(list_files):
    """
    Функция вывода списка list_files на экран в табличном формате с помощью библиотеки Pandas
    :param list_files: список файлов
    :return:
    """
    frame = pd.DataFrame(list_files, columns=['file_name', 'height', 'width'])
    # frame['url'] = frame['url'][:20]
    frame.rename(columns={'file_name': 'Наименование файла',
                          'width': 'Ширина',
                          'height': 'Высота',
                          'url': 'Ссылка на скачинвание'}, inplace=True)
    frame.index = frame.index + 1
    frame.columns.name = '№'
    print(frame, '\n')


def photo_download(file_name, token):
    pass


if __name__ == '__main__':
    main(commands)
