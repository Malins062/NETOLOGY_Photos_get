# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
import json
import pandas as pd
from progress.bar import IncrementalBar
from stdiomask import getpass
import api_services

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ФОТОМАТЕРИАЛОВ НА ОБЛАЧНЫЙ СЕРВИС ---'

# Список допустимых команд программы, их описание и назначение необходимых параметров для каждого пункта
commands = [['Выберите ресурс назначения копирования фотографий:',
             {'1': {'menu_cmd': 1, 'menu_title': 'Яндекс диск;', 'menu_api': 'YaDiskUser',
                    'name': 'Яндекс диск', 'url': 'https://cloud-api.yandex.net/v1/disk/resources/upload'},
              '2': {'menu_cmd': 2, 'menu_title': 'Google drive (в процессе разработки);',
                    'name': 'GoogleDrive API', 'url': ''},
              '0': {'menu_cmd': 0, 'menu_title': 'выход из программы.\n'}
              }],
            ['Выберите источник копирования фотографий:',
             {'1': {'menu_cmd': 1, 'menu_title': 'ВКонтакте;', 'menu_api': 'VKUser',
                    'name': 'ВКонтакте', 'url': 'https://api.vk.com/method/', 'version': '5.131'},
              '2': {'menu_cmd': 2, 'menu_title': 'Однокласники;', 'menu_api': 'OKUser',
                    'name': 'Одноклассники', 'url': 'https://api.ok.ru/fb.do', 'version': ''},
              '3': {'menu_cmd': 3, 'menu_title': 'Инстаграмм;', 'menu_api': 'InstagramUser',
                    'name': 'Инстаграмм', 'url': 'https://graph.instagram.com', 'version': 'v12.0'},
              '9': {'menu_cmd': 9, 'menu_title': 'возврат в предыдущее меню;'},
              '0': {'menu_cmd': 0, 'menu_title': 'выход из программы.\n'}
              }]
            ]

# Признак несуществующей команды меню
error_command = 'Invalid'

# Имя файла журнала загрузки файлов на диск
file_log_name = 'upload.log'


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


def input_menu_command(menu):
    """
    Функция ввода команды меню из словаря menu
    :param menu: список пунктов меню с командами
    :return: словарь: введенная команда и соответсвующие значения
    """
    # Вывод заголовка меню
    print(menu[0])
    # Вывод команд меню
    for key_command, name_command in menu[1].items():
        print(f'\t{key_command} – {name_command["menu_title"]}')

    print('Введите команду:', end=' ')
    code_command = str(input().strip()).lower()

    # Проверка на существование команды меню
    status_command = menu[1].get(code_command, {'error_command': code_command})

    # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
    if status_command.get('error_command', False):
        # Вывод ошибки
        invalid_command(status_command['error_command'])
        is_error = True
    else:
        is_error = False
    return status_command, is_error


def main(cmd):
    """
    Функция основного меню и подменю, с реагированием на команды поданного списка cmd
    :param cmd: команды меню и необходимые значения для реагирования к каждой команде
    """
    is_exit = False
    while not is_exit:
        # Параметры текущей, выбранной команды:
        #       destination - ресурс назначения копирования фотографий
        #       resource - ресурс откуда необходимо копировать фотографии
        status_command = {'destination': {},
                          'resource': {}
                          }

        # Очистка экрана, вывод навзания приложения
        init_screen()

        # Вызов ввода команды меню
        status_command['destination'], is_error = input_menu_command(cmd[0])

        # Проверка на ошибку команды меню
        if is_error:
            continue
        # Проверка команды подменю - выбран ли пункт ВЫХОД
        elif status_command['destination']['menu_cmd'] == 0:
            break

        # Второе подменю
        while True:
            # Очистка экрана, вывод навзания приложения
            init_screen()

            print(f'Хранилище импортируемых фотографий: {status_command["destination"]["name"]} - '
                  f'{status_command["destination"]["url"]}.')

            # Вызов ввода команды меню
            status_command['resource'], is_error = input_menu_command(cmd[1])

            # Проверка на ошибку команды меню
            if is_error:
                continue
            # Проверка команды подменю - выбран ли пункт ВЫХОД
            elif status_command['resource']['menu_cmd'] == 0:
                is_exit = True
                break
            # Проверка команды подменю - выбран ли пункт ВОЗВРАТ В ГЛАВНОЕ МЕНЮ
            elif status_command['resource']['menu_cmd'] == 9:
                break

            # Ввод необходимых данных ID-пользователя и ключа доступа к ресурсу
            if not input_data_for_read(status_command["resource"]):
                continue

            # Проверка на наличие и доступность списка фотографий
            if photos_get(status_command['resource']):

                # Ввод необходимых данных: ключа доступа к ресурсу на который загружать фотографии
                if not input_data_for_write(status_command):
                    continue

                # Проверка куда будут передоваться файлы, если на Google drive,
                # то через отдельное скачивание на локальный ресурс
                if status_command['destination']['menu_cmd'] == 2:
                    download_files(status_command['destination'])

                # Передача файлов на ресурс
                upload_files(status_command['destination'])

                # Вывод результатов на экран
                print('3. ВЫГРУЗКА ДАННЫХ НА СЕРВЕР.')
                print(f'Результаты загрузки файлов на ресурс '
                      f'{status_command["destination"]["name"]}:')
                print_list_files(status_command['destination']['files'],
                                 ['file_name', 'height', 'width', 'log_upload'])

                # Сохранение данных в журнал
                if save_file_json(status_command['destination']['files'], file_log_name):
                    print(f'Список обработанных файлов сохранен в json-файл: {file_log_name}.')
            else:
                print('\nНет доступных фотографий для скачивания!\n')

            input('Для продолжения работы нажмите клавишу "Enter"...')
    return print('\nДо встречи!')


def download_files(data):
    print('\nОжидайте, идет скачивание файлов с сетевого ресурса...')
    suffix = '%(percent)d%%.'
    bar = IncrementalBar('Процесс - ', color='red', suffix=suffix, max=len(data['resource']['files']))
    for f in data['resource']['files']:
        bar.suffix = '{sfx} Скачивается временный файл: {f_name} ...'.format(f_name=f["file_name"], sfx=suffix)
        api_services.download_photo(f['url'], 'TEMP')
        bar.next()
    bar.finish()
    print('Скачивание завершено.\n')


def upload_files(data):
    """
    Функция выгрузки списка файлов из словаря data на сетевой ресурс
    :param data:
    """
    print(f'\nОжидайте, идет передача файлов на конечный сетевой ресурс '
          f'{data["name"]}: {data["url"]}...')
    suffix = '%(percent)d%%.'
    bar = IncrementalBar('Процесс - ', color='green', suffix=suffix, max=len(data['files']) + 2)
    bar.suffix = '{sfx} Соединение с сервером...'.format(sfx=suffix)
    bar.next()

    #  Создание клиента API для импорта фотографий
    client = getattr(api_services, data["menu_api"])(data['url'], data['token'])

    # Загрузка файлов
    for f in data['files']:
        bar.suffix = '{sfx} Передается файл: {f_name} ...'.format(f_name=f["file_name"], sfx=suffix)
        status_upload = client.upload_url_to_disk(data['path_disk'] + '/' + f['file_name'], f['url'])
        if status_upload['code'] == 202:
            f['log_upload'] = 'Успешно загружен'
        else:
            f['log_upload'] = f'Ошибка загрузки {status_upload["code"]}: {status_upload["text"]}'
        bar.next()

    bar.suffix = '{sfx} Все файлы обработаны.'.format(sfx=suffix)
    bar.next()
    bar.finish()

    print('Выгрузка файлов завершена.\n')


def save_file_json(data, file_name):
    """
    Функция сохраения данных json data в в файл
    :param data: словарь который необходимо сохранить в файл
    :param file_name: имя сохраняемого файла
    :return: True - если сохранение файла успешно, иначе вывод текста, возникшего Exception
    """
    try:
        with open(file_name, 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as Ex:
        print(f'Ошибка сохранения результатов в журнал! Файл: {file_name}, ошибка - {Ex}')
        return Ex


def input_data_for_read(resource):
    """
    Функция ввода дополнительных необходмых параметров чтения с сетевого ресурса:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    :param resource: параметры источника импорта фотографий (name, url, id)
    :return: True - если пользователь ввел все необходимые данные + измененный словарь resource
            False - если пользователь ввел 0 - отмену (возврат в предыдущее меню)
    """
    # Очистка экрана, вывод навзания приложения
    init_screen()

    print(f'1. ВХОДНЫЕ ДАННЫЕ.\nРесурс импорта - {resource["name"]}\n')
    print('2. СВЕДЕНИЯ О ФАЙЛАХ НА СЕРВЕРЕ.')
    print(f'Источник импорта фотографий: {resource["name"]} - {resource["url"]}.')

    # Ввод ID пользовател
    resource["id"] = input('Введите ID пользователя (0 - для отмены): ').strip()
    if resource["id"] == '0':
        return False

    # Ввод ТОКЕНА
    resource["token"] = getpass(prompt='Введите TOKEN пользователя (0 - для отмены): ', mask='*')
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
    data["destination"]["token"] = getpass(prompt='Введите TOKEN пользователя (0 - для отмены): ', mask='*')
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
                data['destination']['files'] = [data['resource']['files'][f - 1] for f in files_for_download]
            return True
        # Проверка на возможные ошибки при вводе списка файлов (например номер несуществующего файла)
        except Exception as Ex:
            invalid_command(Ex)
            return False


def photos_get(resource, output=True) -> bool:
    """
    Функция считывания списка доступных файлов для скачивания с сетевых ресурсов
    :param resource: входные параметры выбранного сетевого ресурса
    :param output: параметр выводить на экран список файлов или ошибку - или нет
    :return: список доступных файлов для скачивания c заданного сетевого ресурса,
    если возникла ошибка - печать ошибки и возращает пустой список
    """
    #  Создание клиента API для экспорта фотографий
    client = getattr(api_services, resource["menu_api"])(resource['url'], resource['token'], resource['version'])

    # Вывод информации о клиенте API
    if output:
        print(f'\n{client}')

    # Получения списка доступных фотографий
    resource['files'] = client.get_photos(resource['id'])

    # Проверка на ошибки при получении списка файлов
    if isinstance(resource['files'][0], dict) and resource['files'][0].get('error_code', False):
        if output:
            print(f'Ошибка при чтении списка фотографий!\n '
                  f'Код ошибки: {resource["files"][0]["error_code"]} - {resource["files"][0]["error_msg"]}.')
        return False
    else:
        if output:
            print('\nСписок доступных фотографий для скачивания:')
            print_list_files(resource['files'], ['file_name', 'height', 'width', 'url'])
        return True


def print_list_files(list_files, columns):
    """
    Функция вывода списка list_files на экран в табличном формате с помощью библиотеки Pandas
    :param list_files: список файлов
    :param columns: список колонок которые необходимо выводить на экран
    :return: вывод данных в виде таблицы
    """
    frame = pd.DataFrame(list_files, columns=columns)
    # frame['url'] = frame['url'].str.slice(0, 20)
    frame.rename(columns={'file_name': 'Наименование файла',
                          'width': 'Ширина',
                          'height': 'Высота',
                          'url': 'URL-адрес',
                          'log_upload': 'Результат загрузки'}, inplace=True)
    frame.index = frame.index + 1
    frame.columns.name = '№'
    print(frame, '\n')


if __name__ == '__main__':
    main(commands)
