import json
import os
import threading
import time
import requests
import vk_api
import datetime

from SETTING import *


global photo_index
global news_index
global today


def link_handler(media_link_row):

    photo_url = ''

    if 'photo' in media_link_row:
        photo_media_row = media_link_row['photo']['sizes']

        desired_photo = max(photo_media_row, key=lambda x: x['height'])
        photo_url = desired_photo['url']

    link = media_link_row['url']

    return photo_url, link


def image_handler(media_image_row):

    photo_media_row = media_image_row['sizes']

    # Find the best photo
    desired_photo = max(photo_media_row, key=lambda x: x['height'])

    return desired_photo['url']


def row_handler(news_row):

    # photo / album / video / link / doc / ...
    media_type = news_row['attachments'][0]['type']
    media_row = news_row['attachments'][0][media_type]

    source_id = str(news_row['source_id'])[1:]
    group_name = vk.groups.getById(group_id=source_id)[0]['name']

    if media_type == 'link':
        owner = group_name
        text = news_row['text']
        photo_url, link = link_handler(media_row)

        load_news(owner, text, photo_url, link)

    elif media_type == 'photo' or media_type == 'album':
        owner = group_name
        text = news_row['text']
        photo_url = image_handler(media_row)
        link = ''
        load_news(owner, text, photo_url, link)


def load_news(owner, text, photo_url, link):

    global photo_index, news_index

    # Creating the folder for current news
    os.makedirs(f'NEWS/{today}/{news_index}/', exist_ok=True)

    # Photo loading
    if photo_url != '':
        image = requests.get(photo_url).content
        with open(f'NEWS/{today}/{news_index}/{photo_index}_download_photo.png', 'wb') as file:
            file.write(image)
            photo_index += 1

    # JSON loading
    with open(f'NEWS/{today}/{news_index}/news.json', 'w', encoding='utf-8') as file:
        j = json.dumps({'owner : ': owner, 'text : ': text, 'link : ': link}, indent=4, ensure_ascii=False,)
        file.write(j)

    # Incrementing of news index
    news_index += 1


if __name__ == '__main__':

    # Initialization
    photo_index = 1
    news_index = 1
    counter = 1
    media_types = ['photo', 'album', 'link']
    threads_list = []

    start_time = time.time()
    today = datetime.date.today()

    # Creating "TODAY" path directory
    os.makedirs(f'NEWS/{today}/', exist_ok=True)

    # VK-authorization
    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()

    # Getting newsfeed
    data = vk.newsfeed.get(filters='post')

    for row in data['items']:
        # Если прусутствует медиа файлы
        if 'attachments' in row:
            print(counter)
            row_type = row['attachments'][0]['type']
            if row_type in media_types:
                counter += 1
                thread = threading.Thread(target=row_handler, args=(row,))
                thread.start()
                threads_list.append(thread)
