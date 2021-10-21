import requests
import hashlib


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
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* версия протокола - {self.version};\n' \
               f'\t* ключ доступа - {self.token[:5]}...' \
               f'{self.token[len(self.token) - 5:]}\n'


def _verify_error(res):
    try:
        res.raise_for_status()
        res = res.json()
        if 'error_message' in res:
            error_list = {
                'error_code': f'{res["code"]} - {res["error_type"]}',
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


class OKUser:
    """
    Класс для работы с API Одноклассники
    """

    # Параметры приложения API
    application_id = 512000933212
    application_key = 'CNFODDKGDIHBABABA'
    access_token = 'tkn1sj0BQ94qGFESvnA8kwIa7QQTy2whiRrCVzoNi9EMx62anC9vAXjPXCNIYgi21W1Zd'

    def __init__(self, url, token):
        self.url = url
        self.session_secret_key = token

    def __str__(self):
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* ключ доступа - {self.session_secret_key[:5]}...' \
               f'{self.session_secret_key[len(self.session_secret_key)-5:]}\n'

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Одноклассники для получения списка доступных фотографий
        :param owner_id: id пользователя страницы Одноклассники
        :return: список найденных фотографий или ошибку
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
        res = requests.get(self.url, params={**photos_params, **sig_params}).json()

        # Проверка результата ответа сервера на ошибку
        if 'error_code' in res:
            return res

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
            return res


class VKUser:
    """
    Класс для работы с API Вконтакте
    """
    def __init__(self, url, token, version='5.131'):
        self.url = url
        self.params = {
            'access_token': token,
            'v': version,
        }

    def __str__(self):
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* версия протокола - {self.params["v"]}\n' \
               f'\t* ключ доступа - {self.params["access_token"][:5]}...' \
               f'{self.params["access_token"][len(self.params["access_token"]) - 5:]}\n'

    def get_photos(self, owner_id=None, album_id='profile') -> list:
        """
        Метод создания запроса к странице ВКонтакте для получения списка доступных фотографий
        :param owner_id: id пользователя страницы ВКонтакте
        :param album_id: profile, saved или
        :return: список найденных фотографий или ошибку
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
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()

        # Проверка результата ответа сервера на ошибку
        if 'error' in res:
            return res['error']

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
            return res


class InstagramUser(ClientApi):
    """
    Класс для работы с API Instagram
    """

    def __init__(self, url, token, version='v12.0'):
        super().__init__(url, token)
        self.version = version

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Инстаграмм для получения списка доступных фотографий
        :param owner_id: id пользователя страницы Instagram
        :return: список найденных фотографий или ошибку
        """

        # Выборка списка ID доступных фотографий
        params = {'access_token': self.token}
        res = requests.get(self.url + '/' + self.version + '/' + owner_id + '/media', params=params)

        res = _verify_error(res)
        # Проверка результата ответа сервера на ошибку
        if res.get('error_code', False):
            return res

        # res = res.json()

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
                # Проверка результата ответа сервера на ошибку
                if res_photo.get('error_code', False):
                    return res_photo
                # if self._verify_error(res_photo):
                #     return res_photo
                # if 'error_message' in res_photo:
                #     res['error_code'] = f'{res["code"]} - {res["error_type"]}'
                #     res['error_msg'] = res['error_message']
                #     return res

                # Словарь данных о фотографии
                file_params = {}
                # Проверка контента на предмет фотографии
                media_type = res_photo.get('media_type', 'No_data')
                # Проверка на тип медиа файла
                if media_type == 'IMAGE':
                    # Необходимые значения скачиваемого файла для выходного json-файла
                    file_params = {'type': res_photo.get('media_type', 'No_data'),
                                   'url': res_photo.get('media_url', 'No_data'),
                                   'file_name': str(res_photo.get('id', 'No_data')) + '.jpg'
                                   }
                # Добавление фото в результирующий список если данные есть
                if file_params:
                    list_files.append(file_params)
        return list_files


# def download_photo(self, url, disk_file_path):
#     photo_params = {"path": disk_file_path, "overwrite": "true"}
#     # Запрос к ресурсу
#     # res = requests.get(url, params={**self.params, **photo_params})
#
#     res = requests.get(url, stream=True, allow_redirects=True)
#     realurl = res.url.split('/')[-1].split('?')[0]
#
#     filepath = os.path.join(disk_file_path, realurl)
#
#     with open(filepath, 'wb') as image:
#         if res.ok:
#             for content in res.iter_content(1024):
#                 if content:
#                     image.write(content)
#     # Проверка результата ответа сервера на ошибку
#     if 'error' in res:
#         return res['error']
#     else:
#         return res
