import requests


class InstagramUser:
    """
    Класс для работы с API Instagram
    """

    def __init__(self, url, token, version='v12.0'):
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

    def _verify_error(self, res):
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

    def get_photos(self, owner_id=None) -> list:
        """
        Метод создания запроса к странице Инстаграмм для получения списка доступных фотографий
        :param owner_id: id пользователя страницы Instagram
        :return: список найденных фотографий или ошибку
        """

        # Выборка списка ID доступных фотографий
        params = {'access_token': self.token}
        res = requests.get(self.url + '/' + self.version + '/' + owner_id + '/media', params=params)

        res = self._verify_error(res)
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
                res_photo = requests.get(self.url + '/v12.0/' + ig_media_id, params={**params, **params_photo})

                # Проверка результата ответа сервера на ошибку
                res_photo = self._verify_error(res_photo)
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
