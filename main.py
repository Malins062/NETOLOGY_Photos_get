# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- ФОТОКОПИРОВАНИЕ НА СЕРВИС ОБЛАЧНЫЙ СЕРВИС ---'


# Список допустимых команд программы, их описание и определение запускаемых функций
commands = [{'1': ('Яндекс диск;', 1, 'https://yandex.ru/dev/disk/poligon/'),
             '2': ('Google drive;', 2, 'GoogleDrive API'),
             '0': ('выход из программы.\n', 0)
             },
            {'1': ('ВКонтакте;', 1, 'https://vk.com/dev/photos.get'),
             '2': ('Однокласники;', 2, 'https://apiok.ru/'),
             '3': ('Инстаграмм', 3, 'https://www.instagram.com/developer/'),
             '9': ('возврат в предыдущее меню;', 9, 'Up'),
             '0': ('выход из программы.\n', 0)
             }
            ]


def main(cmd):
    """
    Функция основного меню, с реагирование на команды поданного списка cmd
    :param cmd: команды меню и функции реагирования к каждой команде
    :return:
    """

    # Признак не существующей команды меню
    error_command = 'Invalid'

    def init_screen():
        """
        Функция очистки экрана пользователя и вывода заставки
        """
        os.system('cls||clear')
        print(f'{TITLE_PROGRAM}\n')

    def invalid_command(err_cmd):
        """
        Вывод ошибки на экран, при вводе неверной команды
        :return:
        """
        print(f'\n*** ОШИБКА! Выполнение команды "{err_cmd}" не допустимо! ***\n')
        input('Для продолжения работы нажмите клавишу "Enter"...')

    # Параметры текущей, выбранной команды:
    #       destination - ресурс назначения комирования фотографий
    #       resource - ресурс откуда необходимо копиравть фотографии
    status_command = {'destination': '',
                      'resource': ''
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
                    print(f'Источник импорта фотографий: {status_command["resource"][2]}.')
                    print(f'Хранилище фотографий: {status_command["destination"][2]}.')
                    exit(0)
    return "До встречи!"


if __name__ == '__main__':
    main(commands)
