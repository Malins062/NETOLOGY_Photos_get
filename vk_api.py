import requests


class VKUser:
    def __init__(self, url, file_token, version):
        with open(file_token, 'r') as file_object:
            token = file_object.read().strip()

        self.url = url
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_followers(self, user_id=None):
        followers_url = self.url + 'users.getFollowers'
        followers_params = {
            'count': 1000,
            'user_id': user_id
        }
        res = requests.get(followers_url, params={**self.params, **followers_params}).json()
        return res['response']['items']

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

