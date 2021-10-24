import requests
import hashlib
import os

from google.oauth2 import service_account


class ClientApi:
    """
    Общий класс для API клиента
    """
    def __init__(self, url, token, version=''):
        self.url = url
        self.token = token
        self.version = version
        self.error_list = []

    def __str__(self):
        version = (self.version if self.version else 'отстутсвует')
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* версия протокола - {version};\n' \
               f'\t* ключ доступа - {self.token[:5]}...' \
               f'{self.token[len(self.token) - 5:]}'


def _verify_error(res) -> dict:
    """
    Функция перевода res в формат json.
    Проверка на ошибки в res и возврат словаря ошибок или полученный ответ res.json()
    @param res: ответ от сервера полученный get запросом
    @return: res.json() или словарь с ошибками
    """
    try:
        res.raise_for_status()
        res = res.json()
        if 'error' in res:
            error_list = {
                'error_code': f'{res["error"].get("error_code", "-1")}',
                'error_msg': res["error"].get("error_msg", "-2")
            }
            return error_list
        elif 'error_message' in res:
            error_list = {
                'error_code': f'{res["error_message"].get("code", "-2")} - '
                              f'{res["error_message"].get("error_type", "-1")}',
                'error_msg': res['error_message']
            }
            return error_list
    except Exception as Ex:
        error_list = {
            'error_code': '-1',
            'error_msg': Ex
        }
        return error_list
    return res


class VKUser(ClientApi):
    """
    Класс для работы с API Вконтакте
    """
    def __init__(self, url, token, version=''):
        super().__init__(url, token, version)
        self.params = {
            'access_token': token,
            'v': version,
        }

    def get_photos(self, owner_id=None, album_id='profile') -> list:
        """
        Метод создания запроса к странице ВКонтакте для получения списка доступных фотографий
        @param owner_id: id пользователя страницы ВКонтакте
        @param album_id: profile, saved или
        @return: список найденных фотографий или ошибку
        """
        # URL запроса
        photos_url = self.url + 'photos.get'
        # Параметры запроса
        photos_params = {
            'extended': 1,
            'owner_id': owner_id,
            'album_id': album_id
        }

        # Запрос к ресурсу
        res = requests.get(photos_url, params={**self.params, **photos_params})

        # Проверка результата ответа сервера на ошибку
        res = _verify_error(res)
        if res.get('error_code', False):
            return [res]
        # Проверка на наличие необходимых данных в ответе сервера
        elif 'response' in res and 'items' in res['response']:
            list_files = []

            # Создание словаря лайков фотографий, у которых совпадает количество лайков
            repeat_likes = {}
            for value in res['response']['items']:
                if value['likes']['count'] in repeat_likes:
                    repeat_likes[value['likes']['count']] += 1
                else:
                    repeat_likes[value['likes']['count']] = 1

            # Перебор всех данных по ключу 'items'
            for value in res['response']['items']:
                # Определение самой большой фотографии: сортировка списка фотографий по высоте и ширине
                file_params = sorted(value['sizes'], key=lambda x: x['height'] + x['width'], reverse=True)[0]

                # Создание имени фотографии в формате: id_likes.jpg
                if repeat_likes.get(value['likes']['count'], 0) > 1:
                    file_params['file_name'] = str(value['likes']['count']) + '_' + str(value['date']) + '.jpg'
                else:
                    file_params['file_name'] = str(value['likes']['count']) + '.jpg'

                # Добавление фото в результирующий список
                list_files.append(file_params)
            return list_files
        else:
            return [res]


class OKUser(ClientApi):
    """
    Класс для работы с API Одноклассники
    """
    def __init__(self, url, token, version=''):
        super().__init__(url, token, version)
        self.session_secret_key = token
        self.application_key = 'CNFODDKGDIHBABABA'
        self.access_token = 'tkn1sj0BQ94qGFESvnA8kwIa7QQTy2whiRrCVzoNi9EMx62anC9vAXjPXCNIYgi21W1Zd'

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Одноклассники для получения списка доступных фотографий
        @param owner_id: id пользователя страницы Одноклассники
        @return: список найденных фотографий или ошибку
        """
        # Параметры запроса
        photos_params = {
            'application_key': self.application_key,
            'fid': owner_id,
            'fields': 'photo.like_count, photo.pic_max, photo.text, photo.standard_height, '
                      'photo.standard_width, photo.preview_data, photo.type, user_photo.created_ms',
            'format': 'json',
            'method': 'photos.getPhotos',
        }

        # Вычисление необходимого параметра sig
        sig = ''.join([key + '=' + str(value) for key, value in photos_params.items()])
        sig = sig + self.session_secret_key
        sig = hashlib.md5(sig.encode('utf-8')).hexdigest()

        sig_params = {
            'sig': sig,
            'access_token': self.access_token
        }

        # Запрос к ресурсу
        res = requests.get(self.url, params={**photos_params, **sig_params})

        # Проверка результата ответа сервера на ошибку
        res = _verify_error(res)
        if res.get('error_code', False):
            return [res]

        # Проверка на наличие необходимых данных в ответе сервера
        elif 'photos' in res:
            list_files = []

            # Создание словаря лайков фотографий, у которых совпадает количество лайков
            repeat_likes = {}
            for value in res['photos']:
                if value['like_count'] in repeat_likes:
                    repeat_likes[value['like_count']] += 1
                else:
                    repeat_likes[value['like_count']] = 1

            # Определение самой большой фотографии: сортировка списка фотографий по высоте и ширине
            res['photos'] = sorted(res['photos'],
                                   key=lambda x: x['standard_height'] + x['standard_width'],
                                   reverse=True)

            # Перебор всех данных в словаре res по ключу 'photos'
            for value in res['photos']:
                # Необходимые значения скачиваемого файла для выходного json-файла
                file_params = {'type': value['type'],
                               'height': value['standard_height'],
                               'width': value['standard_width'],
                               'url': value['pic_max']}
                # Создание имени фотографии в формате: id_likes.jpg
                if repeat_likes.get(value['like_count'], 0) > 1:
                    file_params['file_name'] = str(value['like_count']) + '_' + str(value['created_ms']) + '.jpg'
                else:
                    file_params['file_name'] = str(value['like_count']) + '.jpg'
                # Добавление фото в результирующий список
                list_files.append(file_params)
            return list_files
        else:
            return [res]


class InstagramUser(ClientApi):
    """
    Класс для работы с API Instagram
    """
    def __init__(self, url, token, version=''):
        super().__init__(url, token, version)

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Инстаграмм для получения списка доступных фотографий
        @param owner_id: id пользователя страницы Instagram
        @return: список найденных фотографий или ошибку
        """

        # Выборка списка ID доступных фотографий
        params = {'access_token': self.token}
        res = requests.get(self.url + '/' + self.version + '/' + owner_id + '/media', params=params)

        # Проверка результата ответа сервера на ошибку
        res = _verify_error(res)
        if res.get('error_code', False):
            return [res]

        # Результирующий список фотографий
        list_files = []
        # Параметры запроса для детализации фотоматериалов
        params_photo = {
            'fields': 'id, media_url, media_type, timestamp',
        }
        for photo in res['data']:
            ig_media_id = photo.get('id', False)
            if not ig_media_id:
                continue
            else:
                res_photo = requests.get(self.url + '/' + self.version + '/' +
                                         ig_media_id, params={**params, **params_photo})

                # Проверка результата ответа сервера на ошибку
                res_photo = _verify_error(res_photo)
                if res_photo.get('error_code', False):
                    return [res_photo]

                # Словарь данных о фотографии
                file_params = {}
                # Проверка контента на предмет фотографии
                media_type = res_photo.get('media_type', 'No_data')
                # Проверка на тип медиа файла
                if media_type == 'IMAGE':
                    # Необходимые значения скачиваемого файла для выходного json-файла
                    file_params = {'type': res_photo.get('media_type', 'No_data'),
                                   'url': res_photo.get('media_url', 'No_data'),
                                   'file_name': str(res_photo.get('id', 'No_data')) + '.jpg',
                                   'height': '-',
                                   'width': '-'
                                   }
                # Добавление фото в результирующий список если данные есть
                if file_params:
                    list_files.append(file_params)
        return list_files


class YaDiskUser(ClientApi):
    """
    Класс для работы с сервисом Яндекс диск
    """
    def __init__(self, url, token, version=''):
        super().__init__(url, token, version)

    def get_headers(self):
        """
        Методо инициализации заголовка для запорсов
        @return: словарь заголовков
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, disk_file_path):
        """
        Функция получения ссылки на загрузку файла из локальной директории
        @param disk_file_path: локальный путь файла
        @return: ссылка на загрузку
        """
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(self.url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        """
        Функция загрузки локального файла на сетевой ресурс
        @param disk_file_path: локальная папка файл
        @param filename: имя файла
        @return: результат загрузки файла
        """
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        return {'code': response.status_code, 'text': response.text}

    def upload_url_to_disk(self, disk_path, url):
        """
        Метод загрузки файла из интернета на Яндекс диск методом post
        @param disk_path: путь к доступной папке на Яндекс диске
        @param url: ссылка файла в сети интернет
        @return: словарь с кодом ответа и текстом {'code': '', text: ''}
        """
        headers = self.get_headers()
        params = {"path": disk_path, "url": url}
        response = requests.post(url=self.url, headers=headers, params=params)
        return {'code': response.status_code, 'text': response.text}


class GoogleDriveUser(ClientApi):
    """
    Класс для работы с сервисом Google Drive
    """
    def __init__(self, url, token, version=''):
        super().__init__(url, token, version)
        self.key_id = 'e80d3bac3aced3a06184a9df460c76b3ceee2a20'
        self.application_id = '109159928286372133834'

    def get_headers(self):
        """
        Методо инициализации заголовка для запорсов
        @return: словарь заголовков
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, disk_file_path):
        """
        Функция получения ссылки на загрузку файла из локальной директории
        @param disk_file_path: локальный путь файла
        @return: ссылка на загрузку
        """
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(self.url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        """
        Функция загрузки локального файла на сетевой ресурс
        @param disk_file_path: локальная папка файл
        @param filename: имя файла
        @return: результат загрузки файла
        """
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        return {'code': response.status_code, 'text': response.text}


def download_photo(url, disk_file_path):
    """
    Функция скачивания файла по интернет ссылке url в папку disk_file_path
    @param url: url скачиваемого файла
    @param disk_file_path: локальная папка, куда будет скачан файл
    @return: полное имя файла, результат скачивания
    """
    # Скачивание файла
    res = requests.get(url, stream=True, allow_redirects=True)

    # Вычленение навзания файла
    url = res.url.split('/')[-1].split('?')[0]

    # Вычисление полного пути
    filepath = os.path.join(disk_file_path, url)

    # Сохраение файла в локальную папку disk_file_path
    try:
        with open(filepath, 'wb') as image:
            if res.ok:
                for content in res.iter_content(1024):
                    if content:
                        image.write(content)
        return filepath, f'Загружен - {filepath}'
    except Exception as Ex:
        return filepath, f'Ошибка скачивания {Ex}'
