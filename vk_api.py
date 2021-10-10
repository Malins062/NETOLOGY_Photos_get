import requests


class VKUser:
    """
    Класс для работы с API Вконтакте
    """

    def __init__(self, url, token, version):
        self.url = url
        self.params = {
            'access_token': token,
            'v': version,
        }

    def __str__(self):
        return f'Адрес API: {self.url}\n' \
               f'Параметры get-запроса:\n' \
               f'\t* версия протокола - {self.params["v"]}\n' \
               f'\t* ключ доступа - {self.params["access_token"]}\n'

    def get_photos(self, owner_id=None, album_id='profile'):
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

            # Перебор всех данных по ключу 'items'
            for value in res['response']['items']:
                # Определение самой большой фотографии: сортировка списка фотографий по высоте и ширине
                file_params = sorted(value['sizes'], key=lambda x: x['height'] + x['width'], reverse=True)[0]

                # Создание имени фотографии в формате: id_likes.jpg
                file_params['file_name'] = str(value['id']) + '_' + str(value['likes']['count']) + '.jpg'

                # Добавление фото в результирующий список
                list_files.append(file_params)
            return list_files
        else:
            return res
