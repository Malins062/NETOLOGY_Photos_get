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
               f'\t* версия протокола - {self.params["v"]}\n' \
               f'\t* ключ доступа - {self.params["access_token"]}\n'

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
            list_files = {}
            for f in res['response']['items']:
                name_file = str(f['id']) + '_' + str(f['likes']['count']) + '.jpg'
                list_files['file_name'] = name_file
                list_files['size'] = max(f['sizes'], key=f['sizes']['height'])
                # list_files['url'] = f['sizes']
            # list_files = {f['id'] + str(f['likes']['count']) + '.jpg': '' for f in res['response']['items']}
            return list_files
        else:
            return res
