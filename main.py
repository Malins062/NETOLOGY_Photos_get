# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
from cloud_services import YaUpLoader

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ФОТОМАТЕРИАЛОВ НА ОБЛАЧНЫЙ СЕРВИС ---'


# Список допустимых команд программы, их описание и определение запускаемых функций
commands = [{'1': ['Яндекс диск;', 1, {'name': 'Яндекс диск', 'url': 'https://yandex.ru/dev/disk/poligon/'}],
             '2': ['Google drive;', 2, {'name': 'GoogleDrive API', 'url': ''}],
             '0': ['выход из программы.\n', 0]
             },
            {'1': ['ВКонтакте;', 1, {'name': 'ВКонтакте', 'url': 'https://vk.com/dev/photos.get'}],
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
    status_command = {'destination': [],
                      'resource': []
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
                    data_for_copy = input_data(status_command["destination"][2], status_command["resource"][2])
                    if isinstance(data_for_copy, dict):
                        print(data_for_copy)
                        input('press any key')

    return "До встречи!"


def input_data(destination, resource):
    """
    Функция ввода дополнительных необходмых параметров:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    :param destination: параметры хранилища фотографий (name, url, token)
    :param resource: параметры источника импорта фотографий (name, url, id)
    :return: dict - словарь с итоговыми параметрами destination и resource
    """
    print(f'Источник импорта фотографий: {resource["name"]} - {resource["url"]}.')
    print(f'Хранилище импортируемых фотографий: {destination["name"]} - {destination["url"]}.')
    destination["id"] = input('Введите ID пользователя (0 - для отмены): ').strip()
    if destination["id"] == '0':
        return False
    resource["token"] = input('Введите TOKEN пользователя (0 - для отмены): ').strip()
    if resource["token"].strip() == '0':
        return False
    else:
        return {'resource': resource, 'destination': destination}


def photos_get(resource):
    pass


def photo_download(file_name, token):
    token = ''
    uploader = YaUpLoader(token)
    uploader.upload_file_to_disk(path_disk + '/' + filename, filename)
    return None


if __name__ == '__main__':
    main(commands)
