#!/usr/bin/env python
# coding: utf-8

# ## Создаем приложение
#
# 1) Нажимаете на кнопку создать приложение
#
# 2) Выбираете standalone приложение, указываете название приложения
#
# ![](https://sun9-60.userapi.com/c857736/v857736671/14acdc/66pnWpKHRmM.jpg)

# 3) Переходите в настройки, включаете Open API
#
# 4) В поле *адрес сайта* вводите http://localhost
#
# 5) В поле базовый домен вводите localhost
#
# ![](https://sun9-4.userapi.com/c857736/v857736671/14acee/6qdLYkpdBl4.jpg)
#
# 6) Сохраняете изменения

# 7) Копируете id приложения
#
# 8) В ссылку
#
# https://oauth.vk.com/authorize?client_id=7970911&display=page&scope=photos,stats,offline&response_type=token&v=5.131
# вместо 1 вставьте id **вашего** приложения. Не забудьте указать scope: https://vk.com/dev/permissions
#
# 9) Нажимаете разрешить
#
# 10) Сохраняете токен
#
# ![](https://sun9-29.userapi.com/c857736/v857736671/14acf8/2c-F9g7w0jA.jpg)

# ### Читаю токен из файла. В файлах с кодем реквизиты хранить не принято

# In[1]:


with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()

# ## Что нужно знать перед началом работы с VK API
#
# 1. [Синтаксис любого запроса](https://vk.com/dev/api_requests)
#
# 2. [Методы API VK](https://vk.com/dev/methods)
#
# 3. [Версии API VK](https://vk.com/dev/versions)
#
# 4. [Ограничения](https://vk.com/dev/api_requests?f=3.%20%D0%9E%D0%B3%D1%80%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D0%BD%D0%B8%D1%8F%20%D0%B8%20%D1%80%D0%B5%D0%BA%D0%BE%D0%BC%D0%B5%D0%BD%D0%B4%D0%B0%D1%86%D0%B8%D0%B8)

# ### Получим базовую информацию о пользователе при помощи [users.get](https://vk.com/dev/users.get)

# In[2]:


import requests
# импортируем pprint для более комфортного вывода информации
from pprint import pprint

URL = 'https://api.vk.com/method/users.get'
params = {
    'user_id': '1',
    'access_token': token,  # токен и версия api являются обязательными параметрами во всех запросах к vk
    'v': '5.131'
}
res = requests.get(URL, params=params)
pprint(res.json())

# ### Получим дополнительно еще какие-то поля

# In[3]:


params = {
    'user_id': '1',
    'access_token': token,
    'v': '5.131',
    'fields': 'education,sex'
}
res = requests.get(URL, params)
pprint(res.json())


# ### Напишем функцию, которая будет находить группы по поисковому запросу при помощи метода [groups.search](https://vk.com/dev/groups.search)

# In[5]:


def search_groups(q, sorting=0):
    '''
    Параметры sort
    0 — сортировать по умолчанию (аналогично результатам поиска в полной версии сайта);
    1 — сортировать по скорости роста;
    2 — сортировать по отношению дневной посещаемости к количеству пользователей;
    3 — сортировать по отношению количества лайков к количеству пользователей;
    4 — сортировать по отношению количества комментариев к количеству пользователей;
    5 — сортировать по отношению количества записей в обсуждениях к количеству пользователей.
    '''
    params = {
        'q': q,
        'access_token': token,
        'v': '5.131',
        'sort': sorting,
        'count': 300
    }
    req = requests.get('https://api.vk.com/method/groups.search', params).json()
    #     print(req)
    req = req['response']['items']
    return req


target_groups = search_groups('python')
pprint(target_groups)

# ### Получим расширенную информацию по группам при помощи метода [groups.getById](https://vk.com/dev/groups.getById)

# In[6]:


# преобразуем список всех id в строку (в таком виде принимает данные параметр fields)
target_group_ids = ','.join([str(group['id']) for group in target_groups])
pprint(target_group_ids)

# In[7]:


params = {
    'access_token': token,
    'v': '5.131',
    'group_ids': target_group_ids,
    'fields': 'members_count,activity,description'

}
req = requests.get('https://api.vk.com/method/groups.getById', params)

pprint(req.json()['response'])


# ## Если строим какую-то сложную логику взаимодействия с API, то логично будет инкапсулировать весь нужный функционал в класс. Какие нам нужны данные, чтобы инициализировать класс?

# In[8]:


# токен и версия могут быть разные в разных экзмеплярах
class VkUser:
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }


# In[9]:


# базовый URL будет всегда один, в инициализации он не нужен
class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }


# ### Перенесем в класс ранее написанный функционал
#

# In[10]:


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def search_groups(self, q, sorting=0):
        '''
        Параметры sort
        0 — сортировать по умолчанию (аналогично результатам поиска в полной версии сайта);
        1 — сортировать по скорости роста;
        2 — сортировать по отношению дневной посещаемости к количеству пользователей;
        3 — сортировать по отношению количества лайков к количеству пользователей;
        4 — сортировать по отношению количества комментариев к количеству пользователей;
        5 — сортировать по отношению количества записей в обсуждениях к количеству пользователей.
        '''
        group_search_url = self.url + 'groups.search'
        group_search_params = {
            'q': q,
            'sort': sorting,
            'count': 300
        }
        req = requests.get(group_search_url, params={**self.params, **group_search_params}).json()
        return req['response']['items']

    def search_groups_ext(self, q, sorting=0):
        group_search_ext_url = self.url + 'groups.getById'
        target_groups = self.search_groups(q, sorting)
        target_group_ids = ','.join([str(group['id']) for group in target_groups])
        groups_info_params = {
            'group_ids': target_group_ids,
            'fields': 'members_count,activity,description'
        }
        req = requests.get(group_search_ext_url, params={**self.params, **groups_info_params}).json()
        return req['response']


# ### Проверяем

# In[11]:


vk_client = VkUser(token, '5.131')

# In[12]:


pprint(vk_client.search_groups('python'))

# In[13]:


pprint(vk_client.search_groups_ext('python'))

# In[14]:


import pandas as pd

pd.DataFrame(vk_client.search_groups_ext('python'))


# ### Добавим метод для получения подписчиков при помощи [users.getFollowers](https://vk.com/dev/users.getFollowers)

# In[15]:


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def search_groups(self, q, sorting=0):
        '''
        Параметры sort
        0 — сортировать по умолчанию (аналогично результатам поиска в полной версии сайта);
        1 — сортировать по скорости роста;
        2 — сортировать по отношению дневной посещаемости к количеству пользователей;
        3 — сортировать по отношению количества лайков к количеству пользователей;
        4 — сортировать по отношению количества комментариев к количеству пользователей;
        5 — сортировать по отношению количества записей в обсуждениях к количеству пользователей.
        '''
        group_search_url = self.url + 'groups.search'
        group_search_params = {
            'q': q,
            'sort': sorting,
            'count': 300
        }
        req = requests.get(group_search_url, params={**params, **group_search_params}).json()
        return req['response']['items']

    def search_groups_ext(self, q, sorting=0):
        group_search_ext_url = self.url + 'groups.getById'
        target_groups = self.search_groups(q, sorting)
        target_group_ids = ','.join([str(group['id']) for group in target_groups])
        groups_info_params = {
            'group_ids': target_group_ids,
            'fields': 'members_count,activity,description'
        }
        req = requests.get(group_search_ext_url, params={**params, **groups_info_params}).json()
        return req['respone']

    def get_followers(self, user_id=None):
        followers_url = self.url + 'users.getFollowers'
        followers_params = {
            'count': 1000,
            'user_id': user_id
        }
        res = requests.get(followers_url, params={**self.params, **followers_params}).json()
        return res['response']


# In[16]:


# получим своих подписчиков
vk_client = VkUser(token, '5.131')
vk_client.get_followers()

# In[17]:


# получим подписчиков другого пользователя
vk_client = VkUser(token, '5.131')
vk_client.get_followers('1')


# ### Создадим метод для получения групп пользователя при помощи [groups.get](https://vk.com/dev/groups.get)

# In[18]:


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def search_groups(self, q, sorting=0):
        '''
        Параметры sort
        0 — сортировать по умолчанию (аналогично результатам поиска в полной версии сайта);
        1 — сортировать по скорости роста;
        2 — сортировать по отношению дневной посещаемости к количеству пользователей;
        3 — сортировать по отношению количества лайков к количеству пользователей;
        4 — сортировать по отношению количества комментариев к количеству пользователей;
        5 — сортировать по отношению количества записей в обсуждениях к количеству пользователей.
        '''
        group_search_url = self.url + 'groups.search'
        group_search_params = {
            'q': q,
            'sort': sorting,
            'count': 300
        }
        req = requests.get(group_search_url, params={**params, **group_search_params}).json()
        return req['response']['items']

    def search_groups_ext(self, q, sorting=0):
        group_search_ext_url = self.url + 'groups.getById'
        target_groups = self.search_groups(q, sorting)
        target_group_ids = ','.join([str(group['id']) for group in target_groups])
        groups_info_params = {
            'group_ids': target_group_ids,
            'fields': 'members_count,activity,description'
        }
        req = requests.get(group_search_ext_url, params={**params, **groups_info_params}).json()
        return req['respone']

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
        res = requests.get(groups_url, params={**params, **groups_params})
        return res.json()

    # In[19]:


# получим свои группы
vk_client = VkUser(token, '5.131')
vk_client.get_groups()

# In[20]:


# получим группы другого пользователя
vk_client = VkUser(token, '5.131')
vk_client.get_groups('1')

# ### Теперь мы можем импортировать этот класс в другие программы и использовать его интерфейс для реализации нужной логики

# In[ ]:


# In[23]:


data = [
    [13, 25, 23, 34],
    [45, 32, 44, 47],
    [12, 33, 23, 95],
    [13, 53, 34, 35]
]

# In[27]:


sum_ = 0
index = 0
for row in data:
    sum_ += row[index]
    index += 1

print(sum_)

# In[31]:


res = []

for index, row in enumerate(data):
    res.append(row[index])

print(sum(res))

# In[33]:


list(enumerate(data))

# In[30]:


sum([row[index] for index, row in enumerate(data)])

# In[ ]:


res = []

for el...:
    ...

# In[ ]:


numpy
array
