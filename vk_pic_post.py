import requests


class VKPicUploader:
    def __init__(self, token, album_id, group_id):
        self.__token = token
        self.__album_id = album_id
        self.__group_id = group_id

    def get_server(self):
        response = requests.get('https://api.vk.com/method/photos.getUploadServer',
                                params={
                                    'access_token': self.__token,
                                    'album_id': self.__album_id,
                                    'group_id': self.__group_id,
                                    'v': 5.131,
                                })
        return response.json()['response']['upload_url']

    def save_pic(self, upload_url, files_pic):
        response = requests.post(upload_url, files=files_pic).json()
        response = requests.get('https://api.vk.com/method/photos.save',
                                params={
                                    'access_token': self.__token,
                                    'album_id': self.__album_id,
                                    'group_id': self.__group_id,
                                    'server': response['server'],
                                    'photos_list': response['photos_list'],
                                    'hash': response['hash'],
                                    'v': 5.131,
                                })

        return response.json()          # вернуть responce с id-шниками

