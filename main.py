# Курсовая работа «Резервное копирование» первого блока «Основы языка программирования Python».
import os
import json
import pandas as pd
from progress.bar import IncrementalBar
from stdiomask import getpass
import api_services

# Название программы, выводимое на экран
TITLE_PROGRAM = '--- РЕЗЕРВНОЕ КОПИРОВАНИЕ ФОТОМАТЕРИАЛОВ НА ОБЛАЧНЫЙ СЕРВИС (вресия 1.0) ---'

# Список допустимых команд программы, их описание и назначение необходимых параметров для каждого пункта
commands = [['Выберите ресурс назначения копирования фотографий:',
             {'1': {'menu_cmd': 1, 'menu_title': 'Яндекс диск;', 'menu_api': 'YaDiskUser',
                    'upload': 'upload_url_to_disk', 'version': 'v1',
                    'name': 'Яндекс диск', 'url': 'https://cloud-api.yandex.net'},
              '2': {'menu_cmd': 2, 'menu_title': 'Google drive;', 'menu_api': 'GoogleDriveUser',
                    'upload': 'upload_file_to_disk', 'version': 'v3',
                    'name': 'GoogleDrive API', 'url': 'https://www.googleapis.com/auth/drive'},
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
# Временная папка для скачивания файлов
temp_path = 'TEMP'


def init_screen():
    """
    Функция очистки экрана пользователя и вывода заставки
    """
    os.system('cls||clear')
    print(f'{TITLE_PROGRAM}\n')


def invalid_command(err_cmd):
    """
    Вывод ошибки на экран, при вводе неверной команды
    @return:
    """
    print(f'\n*** ОШИБКА! Выполнение команды "{err_cmd}" не допустимо! ***\n')
    input('Для продолжения работы нажмите клавишу "Enter"...')


def input_menu_command(menu, command: dict, appointment):
    """
    Функция ввода команды меню из словаря menu
    @param menu: список пунктов меню с командами
    @param command: введенная команда и соответсвующие значения или сообщение об обибке
    @param appointment: имя параметра словая command, куда будут сохранятся реузльтаты
    @return: True если ошибочная команда меню, иначе False
    """
    # Вывод заголовка меню
    print(menu[0])
    # Вывод команд меню
    for key_command, name_command in menu[1].items():
        print(f'\t{key_command} – {name_command["menu_title"]}')

    print('Введите команду:', end=' ')
    code_command = ''
    while not code_command:
        code_command = str(input().strip()).lower()

    # Проверка на существование команды меню
    command[appointment] = menu[1].get(code_command, {'error_command': code_command})

    # Проверка команды подменю - СУЩЕСТВУЕТ ЛИ ВЫБРАННАЯ КОМАНДА
    if command[appointment].get('error_command', False):
        # Вывод ошибки
        invalid_command(command[appointment]['error_command'])
        return True
    else:
        return False


def main(cmd):
    """
    Функция основного меню и подменю, с реагированием на команды поданного списка cmd
    @param cmd: команды меню и необходимые значения для реагирования к каждой команде
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

        # Вызов ввода команды меню и проверка на ошибку команды меню
        if input_menu_command(cmd[0], status_command, 'destination'):
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

            # Вызов ввода команды подменю и проверка на ошибку команды подменю
            if input_menu_command(cmd[1], status_command, 'resource'):
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

                # Вывод результатов на экран
                print('\n3. ВЫГРУЗКА ДАННЫХ НА СЕРВЕР.')

                # Проверка куда будут передоваться файлы, если на Google drive,
                # то через отдельное скачивание на локальный ресурс
                if status_command['destination']['menu_cmd'] == 2 and not download_files(status_command['destination']):
                    continue

                # Передача файлов на ресурс
                upload_files(status_command['destination'])

                # Проверка если файлы,передавались на Google drive,
                # то очистить папку TEMP
                if status_command['destination']['menu_cmd'] == 2:
                    delete_files_in_dir(temp_path)

                # Сохранение данных в журнал
                if save_file_json(status_command['destination']['files'], file_log_name):
                    print(f'Список обработанных файлов сохранен в json-файл: {file_log_name}.')
            else:
                print('\nНет доступных фотографий для скачивания!\n')

            input('\nДля продолжения работы нажмите клавишу "Enter"...')
    return print('\nДо встречи!')


def delete_files_in_dir(folder):
    """
    Функция очистки директории folder
    :param folder: папка для удаления в ней всех файлов
    :return:
    """
    if folder == '/' or folder == "\\":
        return
    else:
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))


def download_files(data):
    """
    Функция скачивания списка файлов из словаря data локально на рабочую станцию и вывод журнала на экран
    @param data: словарь со списков файлов для скачивания по ключу files
    @return: вывод на экран журнала скачивания файлов, а также True если пользователь нажал Enter после вывода на экран
    и False если пользователь нажал 0 для отмены
    """
    print(f'Скачивание файлов с сетевого ресурса - {data["name"]}:')
    suffix = '%(percent)d%%.'
    bar = IncrementalBar('Процесс - ', color='yellow', suffix=suffix, max=len(data['files'])+2)
    bar.next()

    for f in data['files']:
        bar.suffix = '{sfx} Скачивается временный файл: {f_name} ...'.format(f_name=f["file_name"], sfx=suffix)

        # Скачивание файла на компьютер
        f['url'], f['log_upload'] = api_services.download_photo(f['url'], temp_path)

        bar.next()

    bar.suffix = '{sfx} Все файлы обработаны.'.format(sfx=suffix)
    bar.next()
    bar.finish()

    print(f'\nРезультаты скачивания файлов локально в папку - {temp_path}:')
    print_list_files(data['files'], ['file_name', 'height', 'width', 'log_upload'])

    return input_value(data, 'temp', 'Для выгрузки файлов в сетевой ресурс нажмите Enter ')


def upload_files(data):
    """
    Функция выгрузки списка файлов из словаря data на сетевой ресурс
    @param data: словарь данных со списком файлов которые необходимо загрузить в облако
    """
    print(f'Передача файлов на конечный сетевой ресурс - {data["name"]}:')
    suffix = '%(percent)d%%.'
    bar = IncrementalBar('Процесс - ', color='green', suffix=suffix, max=len(data['files']) + 2)
    bar.suffix = '{sfx} Соединение с сервером...'.format(sfx=suffix)
    bar.next()

    #  Создание клиента API для импорта фотографий
    client = getattr(api_services, data["menu_api"])(data['url'], data['token'], data['version'])

    # Загрузка файлов
    for f in data['files']:
        bar.suffix = '{sfx} Передается файл: {f_name} ...'.format(f_name=f["file_name"], sfx=suffix)

        # Загрузка файла на сетевой ресурс и выбор функции загрузки взависимости от выбораэ
        # конечного сетевого ресурса
        status_upload = getattr(client, data['upload'])(data['path_disk'] + '/' + f['file_name'], f['url'])

        # Проверка на ошибку и запись реультата в журнал
        f['log_upload'] = 'Успешно загружен' if 200 <= status_upload['code'] < 300 else \
            f'Ошибка загрузки {status_upload["code"]}: {status_upload["text"]}'
        bar.next()

    bar.suffix = '{sfx} Все файлы обработаны.'.format(sfx=suffix)
    bar.next()
    bar.finish()

    print(f'\nРезультаты загрузки файлов на ресурс - {data["name"]}:')
    print_list_files(data['files'], ['file_name', 'height', 'width', 'log_upload'])


def save_file_json(data, file_name):
    """
    Функция сохраения данных json data в в файл
    @param data: словарь который необходимо сохранить в файл
    @param file_name: имя сохраняемого файла
    @return: True - если сохранение файла успешно, иначе вывод текста, возникшего Exception
    """
    try:
        with open(file_name, 'w', encoding='UTF-8') as f:
            json.dump(data, f, ensure_ascii=False)
        return True
    except Exception as Ex:
        print(f'Ошибка сохранения результатов в журнал! Файл: {file_name}, ошибка - {Ex}')
        return Ex


def input_value(data, param, title='', mask='', value='0') -> bool:
    """
    Функция пользоватлеьского ввода значения и помещения его в словарь data с ключом param
    @param data: словарь данных
    @param param: ключ словарь для данных
    @param title: заголовок ввода
    @param mask: символ ввода информации для скрытия данных, если параметр не задан то простой ввод
    @param value: значение с которым сравнивается значение вводимое пользователем
    @return: True если value совпадает с введенным значением пользователя, иначе False
    """
    title = f'{title} ({value} - для отмены): '
    data[param] = (getpass(prompt=title, mask=mask) if mask else input(title).strip())
    return not data[param] == value


def input_data_for_read(resource):
    """
    Функция ввода дополнительных необходмых параметров чтения с сетевого ресурса:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
    @param resource: параметры источника импорта фотографий (name, url, id)
    @return: True - если пользователь ввел все необходимые данные + измененный словарь resource
            False - если пользователь ввел 0 - отмену (возврат в предыдущее меню)
    """
    # Очистка экрана, вывод навзания приложения
    init_screen()

    print(f'1. ВХОДНЫЕ ДАННЫЕ.\nРесурс импорта - {resource["name"]}\n')
    print('2. СВЕДЕНИЯ О ФАЙЛАХ НА СЕРВЕРЕ.')
    print(f'Источник импорта фотографий: {resource["name"]} - {resource["url"]}.')

    # Ввод ID пользователя
    if not input_value(resource, 'id', 'Введите ID пользователя'):
        return False
    
    # Ввод ТОКЕНА пользователя
    if not input_value(resource, 'token', 'Введите TOKEN пользователя', '*'):
        return False

    return True


def input_data_for_write(data):
    """
    Функция ввода дополнительных необходмых параметров для загрузки на сетевой ресурс:
     1) ID пользователя, от которого будет производится импорт фотографий;
     2) TOKEN пользователя, кому будут сохраняться фотографии
     3) каталог на сетевом ресурсе, куда будут выгружаться фотографии
    @param data: параметры хранилища фотографий раздел - destination (name, url, token, path_disk)
    @return: True - если пользователь ввел все необходимые данные + измененный словарь data
             False - если пользователь ввел 0 - отмену (возврат в предыдущее меню)
    """
    print(f'Хранилище импортируемых фотографий: {data["destination"]["name"]} - {data["destination"]["url"]}.')

    # Ввод ТОКЕНА пользователя
    if not input_value(data["destination"], 'token', 'Введите TOKEN пользователя ', '*'):
        return False

    # Ввод каталога на конечном ресурсе для загрузки фотографий
    if not input_value(data["destination"], 'path_disk', 'Введите каталог загрузки файлов '):
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
    @param resource: входные параметры выбранного сетевого ресурса
    @param output: параметр выводить на экран список файлов или ошибку - или нет
    @return: список доступных файлов для скачивания c заданного сетевого ресурса,
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
    @param list_files: список файлов
    @param columns: список колонок которые необходимо выводить на экран
    @return: вывод данных в виде таблицы
    """
    frame = pd.DataFrame(list_files, columns=columns)
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
