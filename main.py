from wiki_parser import WikipediaParse
from time_func import add_spec_text, get_days_from_tomorrow_plus, get_delay_lst
from vk_pic_post import VKPicUploader
from get_images_from_google import get_original_images
from bs4 import BeautifulSoup
from urllib.error import URLError
from http.client import RemoteDisconnected
import urllib.request
import requests
import json
from sys import exit


#TODO:
# пофиксить поиск картинок

def send_photos_and_get_id(vk_pic_upl, files, pic_id):
    upload_url = vk_pic_upl.get_server()  # получить сервер для загрузки
    vk_resp = vk_pic_upl.save_pic(upload_url, files)  # загрузить фотографии и получить response
    try:
        for elem in vk_resp['response']:  # получить id загруженных фото
            pic_id.append(elem['id'])
    except KeyError:
        pass

    return pic_id


def main(next_days_lst_len: int = 1, add_days: int = 4):
    """
    :param next_days_lst_len: количество охватываемых дней
    :param add_days: начинать с (завтра + add_days)
    """

    with open('text.json', 'r', encoding="utf-8") as text_js:
        txt_data = json.load(text_js)

    with open('config.json', 'r', encoding="utf-8") as text_js:  # конфиг
        conf_data = json.load(text_js)

    days, days_unix = get_days_from_tomorrow_plus(next_days_lst_len, txt_data["month"],
                                                  add_days)  # получить дни для парсинга

    content = WikipediaParse(txt_data['headers']).get_data_by_days(days)  # получение контента
    vk_pic_upl = VKPicUploader(conf_data['vk_token'], conf_data['album_id'],
                               conf_data['group_id'])  # класс для загрузки в вк

    # json.dump(content, open('content.json', 'w', encoding="utf-8"), ensure_ascii=False)

    delay = get_delay_lst(4)  # задержка для отложенного постинга (каждые 4 часа)
    counter = 0

    for key in content:
        counter_delay = 0
        for text in content[key]:

            # # https://serpapi.com/blog/scrape-google-images-with-python/#full-code
            params = {
                "q": text,  # search query
                "tbm": "isch",  # image results
                "hl": "ru",  # language of the search
                "gl": "ru",  # country where search comes from
                "ijn": "0"  # page number
            }

            # # Поиск картинок
            html = requests.get("https://www.google.com/search", params=params, headers=txt_data['headers'], timeout=30)
            soup = BeautifulSoup(html.text, "lxml")
            images = get_original_images(soup)  # получить список с картинками

            max_pic_count = 10
            current_pic_count = 0
            pack_1 = []
            pack_2 = []

            for image in images:  # сохраняем пикчи
                if current_pic_count == max_pic_count:  # всего 10 штук (макс 10 вложений)
                    break
                else:
                    try:  # если сайт не доступен
                        urllib.request.urlretrieve(image['original'], f'tmp/{current_pic_count}.jpg')
                    except URLError:
                        continue
                    except RemoteDisconnected:
                        continue

                    if current_pic_count < 5:
                        pack_1.append(f'tmp/{current_pic_count}.jpg')
                    else:
                        pack_2.append(f'tmp/{current_pic_count}.jpg')

                    current_pic_count += 1
                    # print(f'{image["original"]}\t{image["title"]}')

            files1, files2 = {}, {}

            for i in range(len(pack_1)):
                files1[f'file{i}'] = open(pack_1[i], 'rb')  # разбиваем на 2 группы
            for i in range(len(pack_2)):
                files2[f'file{i}'] = open(pack_2[i], 'rb')  # по 5 штук

            pic_id = []
            pic_id = send_photos_and_get_id(vk_pic_upl, files1, pic_id)  # загрузить фото на сервер вк и получить id
            pic_id = send_photos_and_get_id(vk_pic_upl, files2, pic_id)

            attachment = ''

            if len(pic_id) == 0:
                attachment = f'photo-{conf_data["group_id"]}_{457239452}'
            else:
                for pid in pic_id:
                    attachment += f'photo-{conf_data["group_id"]}_{pid},'  # вложение к посту
                attachment = attachment[:-1]  # убрать последнюю запятую

            response = requests.get('https://api.vk.com/method/wall.post',  # постинг на стене
                                    params={
                                        'access_token': conf_data['vk_token'],
                                        'owner_id': -conf_data['group_id'],
                                        'message': add_spec_text(key, text),
                                        'attachments': attachment,
                                        'close_comments': 0,
                                        'publish_date': days_unix[counter] + delay[counter_delay],
                                        'v': 5.92,
                                    })

            print(f'Загружается пост {counter}_{counter_delay}')
            counter_delay += 1
        counter += 1

    print('Данные успешно загружены')
    return


if __name__ == '__main__':
    main()
