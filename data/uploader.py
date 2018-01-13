import requests

class Uploader():
    def upload(path):
        files = {'file':open(path, 'rb')}
        return requests.post('https://d1.dropfile.to/upload', files=files).json()

    def status(url):
        url = url.replace('https://dropfile.to/', 'https://dropfile.to/api/')
        return requests.get(url).json()

    def delete(url, key):
        url = url.replace('https://dropfile.to/', 'https://dropfile.to/api/')
        url = url + '?delete=' + key
        return requests.get(url).json()