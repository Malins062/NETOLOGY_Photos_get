import requests


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
               f'{self.params["access_token"][len(self.params["access_token"])-5:]}\n'

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
