import requests

class Uploader():
    def __init__():
        self.uploadlink = requests.get(link).text.replace('\n', '')

    def upload(path):
        files = {'file':open(path, 'rb')}
        return requests.post(self.link+'/upload', files=files).json()

    def status(url):
        url = url.replace('https://dropfile.to/', 'https://dropfile.to/api/')
        return requests.get(url).json()

    def delete(url, key):
        url = url.replace('https://dropfile.to/', 'https://dropfile.to/api/')
        url = url + '?delete=' + key
        return requests.get(url).json()