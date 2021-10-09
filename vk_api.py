import requests


class VKUser:
    def __init__(self, url, token, version):
        self.url = url
        self.params = {
            'access_token': token,
            'v': version,
        }

    def __str__(self):
        return f'Адрес: {self.url}.\n' \
               f'Параметры:\n' \
               f'\t* версия - {self.params["v"]}\n' \
               f'\t* сервисный ключ - {self.params["access_token"]}\n'

    def get_photos(self, owner_id=None, album_id='profile'):
        photos_url = self.url + 'photos.get'
        photos_params = {
            'extended': 1,
            'owner_id': owner_id,
            'album_id': album_id
        }
        res = requests.get(photos_url, params={**self.params, **photos_params}).json()
        if 'error' in res:
            return res['error']
        elif 'response' in res and 'items' in res['response']:
            return res['response']['items']
        else:
            return res

    def get_groups(self, user_id=None):
        groups_url = self.url + 'groups.get'
        groups_params = {
            'count': 1000,
            'user_id': user_id,
            'extended': 1,
            'fields': 'members_count'
        }
        res = requests.get(groups_url, params={**self.params, **groups_params})
        return res.json()

