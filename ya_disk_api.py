import requests


class YaDiskUser:
    """
    Класс для работы с сервисом Яндекс диск
    """

    files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_files_list(self):
        """
        Метод получения списка файлов
        :return: список файлов в формате json
        """
        headers = self.get_headers()
        response = requests.get(self.files_url, headers=headers)
        return response.json()

    def _get_upload_link(self, disk_file_path):
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(self.upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        response.raise_for_status()
        if response.status_code == 201:
            print(f"Файл - {disk_file_path} загружен.")

    def upload_url_to_disk(self, disk_path, url):
        headers = self.get_headers()
        params = {"path": disk_path, "url": url, "overwrite": "true"}
        response = requests.post(url=self.upload_url, headers=headers, params=params)
        response.raise_for_status()
        return response.status_code

