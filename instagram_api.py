import requests


class InstagramUser:
    """
    Класс для работы с API Instagram
    """

    # Параметры приложения API
    application_id = '174862478155512'
    # application_id = 168400752147982
    secret_key = 'fbecd9b2130448aa4ae5bd3d08ea0714'
    url_auth = 'https://api.instagram.com/oauth/authorize'

    def __init__(self, url, token, version='v12.0'):
        self.url = url + '/' + version
        self.token = token
        self.params = {
            'fields': 'id, user_name, media_count',
            'access_token': token
        }

    def __str__(self):
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* ключ доступа - {self.token[:5]}...' \
               f'{self.token[len(self.token)-5:]}\n'

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Инстаграмм для получения списка доступных фотографий
        :param owner_id: id пользователя страницы Instagram
        :return: список найденных фотографий или ошибку
        """
        # Параметры запроса
        # photos_params = {
        #     'application_key': self.application_key,
        #     'fid': owner_id,
        #     'fields': 'photo.like_count, photo.pic_max, photo.text, photo.standard_height, '
        #               'photo.standard_width, photo.preview_data, photo.type, user_photo.created_ms',
        #     'format': 'json',
        #     'method': 'photos.getPhotos',
        # }

        params_auth = {
            'client_id': self.application_id,
            'client_secret': self.secret_key,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://localhost/',
            'code': self.token
        }
        headers_auth = {'Content-Type': 'application/x-www-form-urlencoded'}

        # res = requests.post(self.url_auth, data=params_auth, headers=headers_auth)
        res = requests.get('https://api.instagram.com/v12.0/users/search?q=' + owner_id + '&access_token=' +
                           self.token, verify=True)
        res = res.json()
        # Запрос к ресурсу
        # res = requests.get(self.url + '/' + owner_id, params=self.params)
        # res = res.json()
        # res = requests.get(self.url, params={**photos_params, **sig_params}).json()

        # Проверка результата ответа сервера на ошибку
        if 'error_message' in res:
            res['error_code'] = f'{res["code"]} - {res["error_type"]}'
            res['error_msg'] = res['error_message']
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
