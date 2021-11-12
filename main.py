import json
import os

import requests
import vk_api
from SETTING import *
import datetime

global photo_index
global news_index
global today


def getToday():
    return datetime.date.today()


def link_handler(media_link_row):
    photo_media_row = media_link_row['photo']['sizes']
    url = media_link_row['url']

    desired_photo = max(photo_media_row, key=lambda x: x['height'])

    link_news.append(url)
    photo_news.append(desired_photo['url'])


def image_handler(media_image_row):

    photo_media_row = media_image_row['sizes']
    desired_photo = max(photo_media_row, key=lambda x: x['height'])
    photo_news.append(desired_photo['url'])


def row_handler(news_row):

    # photo / album / video / link / doc / ...
    media_type = news_row['attachments'][0]['type']
    media_row = news_row['attachments'][0][media_type]

    source_id = str(news_row['source_id'])[1:]
    group_name = vk.groups.getById(group_id=source_id)[0]['name']

    if media_type == 'link':
        owner_news.append(group_name)
        text_news.append(news_row['text'])
        link_handler(media_row)

    elif media_type == 'photo' or media_type == 'album':
        owner_news.append(group_name)
        text_news.append(news_row['text'])
        link_news.append('')
        image_handler(media_row)


owner_news = []
text_news = []
photo_news = []
link_news = []


def load_data():

    global photo_index, news_index

    for owner, text, photo_url, link in zip(owner_news, text_news, photo_news, link_news):

        os.makedirs(f'NEWS/{today}/{news_index}/', exist_ok=True)

        image = requests.get(photo_url).content

        with open(f'NEWS/{today}/{news_index}/news.txt', 'w', encoding='utf-8') as file:
            j = json.dumps({'owner : ': owner, 'text : ': text, 'link : ': link}, indent=4, ensure_ascii=False,)
            file.write(j)

        with open(f'NEWS/{today}/{news_index}/{photo_index}_download_photo.png', 'wb') as file:
            file.write(image)
            photo_index += 1

        news_index += 1


if __name__ == '__main__':

    photo_index = 1
    news_index = 1
    today = getToday()

    os.makedirs(f'NEWS/{today}/', exist_ok=True)

    vk_session = vk_api.VkApi(login, password)
    vk_session.auth()
    vk = vk_session.get_api()

    data = vk.newsfeed.get(filters='post', fields='firstname')

    for row in data['items']:
        # Если прусутствует медиа файлы
        if 'attachments' in row:
            row_handler(row)

    print('###')
    load_data()
