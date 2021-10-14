import requests


class YaDiskUser:
    """
    Класс для работы с сервисом Яндекс диск
    """

    # ссылка для загрузки файлов на Яндекс диск
    upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    def __init__(self, token):
        """
        Метод инициализация ключа доступа к Яндекс диску
        :param token: ключ доступа
        """
        self.token = token

    def get_headers(self):
        """
        Методо инициализации заголовка для запорсов
        :return: словарь заголовков
        """
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def _get_upload_link(self, disk_file_path):
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(self.upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, disk_file_path, filename):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        response = requests.put(href, data=open(filename, 'rb'))
        return {'code': response.status_code, 'text': response.text}

    def upload_url_to_disk(self, disk_path, url):
        """
        Метод загрузки файла из интернета на Яндекс диск методом post
        :param disk_path: путь к доступной папке на Яндекс диске
        :param url: ссылка файла в сети интернет
        :return: словарь с кодом ответа и текстом {'code': '', text: ''}
        """
        headers = self.get_headers()
        params = {"path": disk_path, "url": url}
        response = requests.post(url=self.upload_url, headers=headers, params=params)
        return {'code': response.status_code, 'text': response.text}

