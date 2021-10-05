# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- ФОТОКОПИРОВАНИЕ НА СЕРВИС ОБЛАЧНЫЙ СЕРВИС ---'


# Список допустимых команд программы, их описание и определение запускаемых функций
commands = [{'1': ('Яндекс диск;', ''),
             '2': ('Google drive;', 'command_s'),
             '0': ('выход из программы.\n', exit)
             },
            {'1': ('ВКонтакте;', 'https://vk.com/dev/photos.get'),
             '2': ('Однокласники;', 'https://apiok.ru/'),
             '3': ('Инстаграмм', 'https://www.instagram.com/developer/'),
             '9': ('возврат в предыдущее меню;', 'command_q'),
             '0': ('выход из программы.\n', exit)
             }
            ]


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
        input('Для продолжения работы нажмите клавишу "Enter"...')

    is_menu_1 = True
    while is_menu_1:
        os.system('cls||clear')
        print(f'{TITLE_PROGRAM}\n')

        print('Выберите ресурс назначения копирования фотографий:')
        for key_command, name_command in cmd[0].items():
            print(f'\t{key_command} – {name_command[0]}')

        print('Введите команду:', end=' ')
        command = str(input().strip()).lower()
        cmd.get(command, [None, invalid_command])[1]()

        is_menu_2 = True
        while not is_menu_2:
            print('Выберите источник копирования фотографий:')
            for key_command, name_command in cmd[1].items():
                print(f'\t{key_command} – {name_command[0]}')

            print('Введите команду:', end=' ')
            command = str(input().strip()).lower()
            cmd.get(command, [None, invalid_command])[1]()


if __name__ == '__main__':
    main(commands)
