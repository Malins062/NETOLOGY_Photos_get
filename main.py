# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
import time
import pandas as pd
# from pprint import pprint
from vk_api import VKUser
from ya_disk_api import YaDiskUser
from progress.bar import IncrementalBar

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ФОТОМАТЕРИАЛОВ НА ОБЛАЧНЫЙ СЕРВИС ---'

# Список допустимых команд программы, их описание и назначение необходимых параметров для каждого пункта
commands = [{'1': {'menu_cmd': 1, 'menu_title': 'Яндекс диск;',
                   'name': 'Яндекс диск', 'url': 'https://yandex.ru/dev/disk/poligon/'},
             '2': {'menu_cmd': 2, 'menu_title': 'Google drive;',
                   'name': 'GoogleDrive API', 'url': ''},
             '0': {'menu_cmd': 0, 'menu_title': 'выход из программы.\n'}
             },
            {'1': {'menu_cmd': 1, 'menu_title': 'ВКонтакте;',
                   'name': 'ВКонтакте', 'url': 'https://api.vk.com/method/', 'version': '5.131'},
             '2': {'menu_cmd': 2, 'menu_title': 'Однокласники;',
                   'name': 'Одноклассники', 'url': 'https://api.ok.ru/api/'},
             '3': {'menu_cmd': 3, 'menu_title': 'Инстаграмм;',
                   'name': 'Инстаграмм', 'url': 'https://www.instagram.com/developer/'},
             '9': {'menu_cmd': 9, 'menu_title': 'возврат в предыдущее меню;'},
             '0': {'menu_cmd': 0, 'menu_title': 'выход из программы.\n'}
             }
            ]


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


def main(cmd):
    """
    Функция основного меню и подменю, с реагированием на команды поданного списка cmd
    :param cmd: команды меню и необходимые значения для реагирования к каждой команде
    """

    # Признак несуществующей команды меню
    error_command = 'Invalid'

    # Параметры текущей, выбранной команды:
    #       destination - ресурс назначения копирования фотографий
    #       resource - ресурс откуда необходимо копировать фотографии
    status_command = {'destination': {},
                      'resource': {}
                      }
    is_exit = False
    while not is_exit:
        init_screen()
        print('Выберите ресурс назначения копирования фотографий:')
        for key_command, name_command in cmd[0].items():
            print(f'\t{key_command} – {name_command["menu_title"]}')

        print('Введите команду:', end=' ')
        command = str(input().strip()).lower()
        status_command['destination'] = cmd[0].get(command, error_command)

        # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
        if status_command['destination'] == error_command:
            invalid_command(command)
        # Проверка команды подменю - выбран ли пункт ВЫХОД
        elif status_command['destination']['menu_cmd'] == 0:
            is_exit = True
        else:
            is_menu_out = False
            while not is_menu_out:
                init_screen()
                print(f'Хранилище импортируемых фотографий: {status_command["destination"]["name"]} - '
                      f'{status_command["destination"]["url"]}.')
                print('Выберите источник копирования фотографий:')
                for key_command, name_command in cmd[1].items():
                    print(f'\t{key_command} – {name_command["menu_title"]}')

                print('Введите команду:', end=' ')
                command = str(input().strip()).lower()
                status_command['resource'] = cmd[1].get(command, error_command)

                # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
                if status_command['resource'] == error_command:
                    invalid_command(command)
                # Проверка команды подменю - выбран ли пункт ВЫХОД
                elif status_command['resource']['menu_cmd'] == 0:
                    is_exit = True
                    is_menu_out = True
                # Проверка команды подменю - выбран ли пункт ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
                elif status_command['resource']['menu_cmd'] == 9:
                    is_menu_out = True
                else:
                    init_screen()

                    # Ввод необходимых данных ID-пользователя и ключа доступа к ресурсу
                    if input_data_for_read(status_command["resource"]):
                        print(f'\n1. ВХОДНЫЕ ДАННЫЕ.\nРесурс импорта - {status_command["resource"]["name"]}\n')
                        files_to_download = photos_get(status_command['resource'])

                        print('2. СВЕДЕНИЯ О ФАЙЛАХ НА СЕРВЕРЕ.')
                        if len(files_to_download) > 0:
                            print('\nСписок доступных фотографий для скачивания:')
                            print_list_files(files_to_download)

                            # Ввод необходимых данных: ключа доступа к ресурсу на который загружать фотографии
                            if input_data_for_write(status_command):
                                # Проверка куда будут передоваться файлы, если на Яндекс диск, то напрямую
                                if status_command['destination']['menu_cmd'] == 1:
                                    upload_files(status_command)
                                # если на Google drive, то через отдельное скачивание на локальный ресурс
                                if status_command['destination']['menu_cmd'] == 2:
                                    download_files(status_command)
                                    upload_files(status_command)

                                print(f'Результаты загрузки файлов на ресурс {status_command["destination"]["name"]}:')
                                print_list_files(status_command['destination']['files'])
                                input('\nДля продолжения работы нажмите клавишу "Enter"...')

                        else:
                            print('\nНет доступных фотографий для скачивания!\n')
                            input('Для продолжения работы нажмите клавишу "Enter"...')
    return "До встречи!"


def download_files(data):
    client_vk = VKUser(data['resource']['url'], data['resource']['token'], data['resource']['version'])

    print('Ожидайте, идет скачивание файлов с сетевого ресурса...')
    bar = IncrementalBar('Скачивание: ', max=len(data['resource']['files']))
    # for f in range(len(data['resource']['files'])):
    for f in data['resource']['files']:
        client_vk.download_photo(f['url'], 'TEMP')
        time.sleep(5)
        bar.next()
    bar.finish()
    print('Скачивание завершено.')
    return True


def upload_files(data):
    print(f'\nОжидайте, идет передача файлов на конечный сетевой ресурс '
          f'{data["destination"]["name"]}: {data["destination"]["url"]}...')
    suffix = '%(percent)d%%.'
    bar = IncrementalBar('Загрузка: ', color='green', suffix=suffix, max=len(data['destination']['files']) + 1)
    bar.next()

    token = 'AQAAAAACs0c5AADLW8Q8CcqRaU41gHCd6u19yBk'
    # data['destination']['path_disk'] = 'NETOLOGY/PHOTO'

    # # Проверка на какой ресурся загружать файлы 1 - Яндекс диск, 2 - Google drive
    # if data['destination']['menu_cmd'] == 1:
    #     client = YaDiskUser(token)
    # elif data['destination']['menu_cmd'] == 2:
    #     client = 'google'

    client = YaDiskUser(token)

    # Загрузка файлов
    for f in data['destination']['files']:
        bar.suffix = '{sfx} Файл - {f_name}'.format(f_name=f["file_name"], sfx=suffix)
        status_upload = client.upload_url_to_disk(data['destination']['path_disk'] + '/' + f['file_name'], f['url'])
        if status_upload['code'] == 201:
            f['log_upload'] = 'Успешно загружен'
        else:
            f['log_upload'] = f'Ошибка загрузки {status_upload["code"]}: {status_upload["text"]}'
        bar.next()
    bar.finish()

    print(f'Загрузка завершена.\n')
    return True


def input_data_for_read(resource):
    """
    Функция ввода дополнительных необходмых параметров чтения с сетевого ресурса:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    :param resource: параметры источника импорта фотографий (name, url, id)
    :return: True - если пользователь ввел все необходимые данные + измененный словарь resource
            False - если пользователь ввел 0 - отмену (возврат в предыдущее меню)
    """
    print(f'Источник импорта фотографий: {resource["name"]} - {resource["url"]}.')
    resource["id"] = input('Введите ID пользователя (0 - для отмены): ').strip()
    if resource["id"] == '0':
        return False
    resource["token"] = input('Введите TOKEN пользователя (0 - для отмены): ').strip()
    if resource["token"].strip() == '0':
        return False
    else:
        return True


def input_data_for_write(data):
    """
    Функция ввода дополнительных необходмых параметров для загрузки на сетевой ресурс:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
     3) каталог на сетевом ресурсе, куда будут выгружаться фотографии
    :param data: параметры хранилища фотографий раздел - destination (name, url, token, path_disk)
    :return: True - если пользователь ввел все необходимые данные + измененный словарь data
            False - если пользователь ввел 0 - отмену (возврат в предыдущее меню)
    """
    print(f'Хранилище импортируемых фотографий: {data["destination"]["name"]} - {data["destination"]["url"]}.')
    data["destination"]["token"] = input('Введите TOKEN пользователя (0 - для отмены): ').strip()
    if data["destination"]["token"].strip() == '0':
        return False
    data["destination"]["path_disk"] = input('Введите каталог загрузки файлов (0 - для отмены): ').strip()
    if data["destination"]["path_disk"].strip() == '0':
        return False

    # Ввод номеров файлов или общего количества скачиваемых файлоы
    print('Введите количество фотографий для загрузки с ресурса (0 - для отмены)')
    print('< примечание: список номеров фото через пробел [пример: 1, 2, 5],')
    print(' или общее количество фото [пример: -5]>:', end=' ')
    try:
        files_for_download = []
        while not files_for_download:
            files_for_download = list(map(int, input().strip().split()))
    # При ошибке ввода - вывод ошибки и переход в предыдующее меню
    except Exception as Ex:
        invalid_command(Ex)
        return False

    # Прверка захотел ли пользователь выйти из диалога, вернуться в предыдущее меню
    if files_for_download[0] == 0:
        return False
    # если нет, то
    else:
        try:
            # Если пользователь ввел значение с минусом, то берутся первые -n файлов
            if files_for_download[0] < 0:
                data['destination']['files'] = [data['resource']['files'][f] for f in range(abs(files_for_download[0]))]
            # иначе выбирается список файлов который ввел пользователь
            else:
                data['destination']['files'] = [data['resource']['files'][f-1] for f in files_for_download]
            return True
        # Проверка на возможные ошибки при вводе списка файлов (например номер несуществующего файла)
        except Exception as Ex:
            invalid_command(Ex)
            return False


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
        resource['files'] = client_vk.get_photos(resource['id'])
        return resource['files']
    return []


def print_list_files(list_files):
    """
    Функция вывода списка list_files на экран в табличном формате с помощью библиотеки Pandas
    :param list_files: список файлов
    :return:
    """
    frame = pd.DataFrame(list_files, columns=['file_name', 'height', 'width', 'log_upload'])
    # frame['url'] = frame['url'][:20]
    frame.rename(columns={'file_name': 'Наименование файла',
                          'width': 'Ширина',
                          'height': 'Высота',
                          'url': 'Ссылка на скачинвание',
                          'log_upload': 'Результат загрузки'}, inplace=True)
    frame.index = frame.index + 1
    frame.columns.name = '№'
    print(frame, '\n')


if __name__ == '__main__':
    main(commands)
