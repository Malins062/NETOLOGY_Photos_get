import requests
import hashlib


class OKUser:
    """
    Класс для работы с API Одноклассники
    """

    # Параметры приложения API
    application_id = 512000933212
    application_key = 'CNFODDKGDIHBABABA'
    application_secret_key = 'tkn10fo7E9dQcFKdmWLkCDe9Q650hJtATdEeAxZnKvoK7tf7gpuAQvuONKryEoy0IMdXG'
    access_token = 'tkn1QzcYHUFZvmDYcgPvGKRklTQPudiI2WZbm6dngtvjAS7ZcpNXdytn2A8Biq9ZSBLZX'

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
        # Расчет необходимого параметра sig

        # Параметры запроса
        photos_params = {
            'application_key': self.application_key,
            'fid': owner_id,
            'format': 'json',
            'method': 'photos.getPhotos',
        }

        # Вычисление необходимого параметра sig
        sig = ''.join([key + '=' + str(value) for key, value in photos_params.items()]) + self.session_secret_key
        sig = hashlib.md5(sig.encode('utf-8')).hexdigest()

        sig_params = {
            'sig': sig,
            'access_token': self.access_token
        }

        # Запрос к ресурсу
        res = requests.get(self.url, params={**photos_params, **sig_params}).json()

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
