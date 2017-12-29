import os, time, json, requests, pafy, random, wikipedia, deviantart
from flask import Flask, request, abort
from bs4 import BeautifulSoup, SoupStrainer
from PIL import Image
from imgurpython import ImgurClient
from data.MALScrapper import MAL
from data.PixivScrapper import pixivapi

#a

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import *

app = Flask(__name__)

line_bot_api = LineBotApi('E2NW4d5IBfL8zRP2FlbJ5Pg6GTDaUMAvQyfTkOGrzGReNR77kpXQDUOIfX/9XWdIEQfDGMadtkS8kcRB4VtXAeAPmkJB6GGbbb35RghRG4PA3l25h5krMSNuw0B/mEJRO/H3J0FIeDnY0W8yJQMw/QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cfc54ea01c497698b82e26d647d9610b')
adminid = 'Uc8eed8927818997fec7df0239b827d4e'
workdir = os.getcwd()
myanimelist = MAL()
pixiv = pixivapi('rahandinoor', 'rahandi')
devapi = deviantart.Api('7267','daac0fc861e570e0f9553783507266fd')
imgur = ImgurClient('19bd6586ad07952', '7cff9b3396b1b461b64d923e45d37ceff1e801fe', '663137659dbab6d44a9a1a2cb3f8af6c63b68762', '660b76c28420af23ce2e5e23b7a317c7a96a8907')
file = open('%s/data/jsondata' % (workdir), 'r')
important = file.read()
file.close()
important = json.loads(important)

def customMessage(token, cus):
    try:
        line_bot_api.reply_message(token, cus)
    except Exception as e:
        raise e

def replyTextMessage(token, text):
    try:
        line_bot_api.reply_message(token, TextSendMessage(text = text))
    except Exception as e:
        raise e

def replyImageMessage(token, urlpic, urlprev):
    try:
        line_bot_api.reply_message(token, ImageSendMessage(original_content_url=urlpic, preview_image_url=urlprev))
    except Exception as e:
        raise e

def replyAudioMessage(token, url):
    try:
        line_bot_api.reply_message(token, AudioSendMessage(original_content_url=url, duration=1))
    except Exception as e:
        raise e

def replyVideoMessage(token, urlvid, urlpic):
    try:
        line_bot_api.reply_message(token, VideoSendMessage(original_content_url=urlvid, preview_image_url=urlpic))
    except Exception as e:
        raise e

def replyLocationMessage(token, title, address, lat, lng):
    try:
        line_bot_api.reply_message(token, LocationSendMessage(title=title, address=address, latitude=lat, longitude=lng))
    except Exception as e:
        raise e

def replyTemplateMessage(token, data):
    try:
        alt = data['alt']
        thumbnail = data['tumbnail']
        title = data['title']
        text = data['text']
        action = data['action']
        line_bot_api.reply_message(token, TemplateSendMessage(alt_text=alt, template=ButtonsTemplate(thumbnail_image_url=thumbnail, title=title, text=text, actions=action)))
    except Exception as e:
        raise e

def actionBuilder(amount, type, param1, param2):
    try:
        built = []
        if amount == 1:
            if type[0] == 'msg':
                built = MessageTemplateAction(label=param1[0], text=param2[0])
            elif type[0] == 'uri':
                built = URITemplateAction(label=param1[0], uri=param2[0])
            elif type[0] == 'postback':
                built = PostbackTemplateAction(label=param1[0], data=param2[0])
        else:
            for i in range(0, amount):
                if type[i] == 'msg':
                    apped = MessageTemplateAction(label=param1[i], text=param2[i])
                elif type[i] == 'uri':
                    apped = URITemplateAction(label=param1[i], uri=param2[i])
                elif type[i] == 'postback':
                    apped = PostbackTemplateAction(label=param1[i], data=param2[i])
                built.append(apped)
        return built
    except Exception as e:
        raise e

def replyCarrouselMessage(token, data):
    try:
        alt = data['alt']
        template = data['template']
        line_bot_api.reply_message(token, TemplateSendMessage(alt_text=alt, template=template))
    except Exception as e:
        print(e)

def templateBuilder(amount, type, template):
    try:
        columse = []
        for i in range(0, amount):
            if type == 'template':
                thumbnail = template[i]['tumbnail']
                title = template[i]['title']
                text = template[i]['text']
                action = template[i]['action']
                apped = CarouselColumn(thumbnail_image_url=thumbnail, title=title, text=text, actions=action)
            elif type == 'img':
                thumbnail = template[i]['tumbnail']
                action = template[i]['action']
                apped = ImageCarouselColumn(image_url=thumbnail, action=action)
            columse.append(apped)
        if type == 'template':
            return CarouselTemplate(columns=columse)
        elif type == 'img':
            return ImageCarouselTemplate(columns=columse)
    except Exception as e:
        raise e

def donwloadContent(mId):
    try:
        path = '%s/data/temp/%s.jpg' % (workdir, str(random.randint(1, 1000000)))
        message_content = line_bot_api.get_message_content(mId)
        with open(path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        return path
    except Exception as e:
        raise e

def shorten(url):
    api_key = 'AIzaSyB2JuzKCAquSRSeO9eiY6iNE9RMoZXbrjo'
    req_url = 'https://www.googleapis.com/urlshortener/v1/url?key=' + api_key
    payload = {'longUrl': url}
    headers = {'content-type': 'application/json'}
    r = requests.post(req_url, data=json.dumps(payload), headers=headers)
    resp = json.loads(r.text)
    return resp['id']

def youtubesearch(query):
    try:
        query = query.replace(' ', '+')
        link = 'https://www.youtube.com/results?search_query=' + query
        page = requests.get(link).text
        prefered = SoupStrainer('a', {'rel':'spf-prefetch'})
        soup = BeautifulSoup(page, 'lxml', parse_only=prefered)
        hitung = 0
        url = []
        title = []
        videoid = []
        for a in soup.find_all('a', {'rel':'spf-prefetch'}):
            if '/watch?' in a['href']:
                hitung += 1
                title.append(a['title'])
                url.append('https://youtube.com' + str(a['href']) + '&t')
                videoid.append(a['href'].replace('/watch?v=', ''))
                if hitung >= 10:
                    break
        return title, url, videoid
    except Exception as e:
        raise e

def youtubemp3(query):
    try:
        pafyObj = pafy.new(query)
        audio = pafyObj.getbestaudio(preftype='m4a')
        return shorten(audio.url)
    except Exception as e:
        raise e

def youtubevideo(query):
    try:
        pafyObj = pafy.new(query)
        video = pafyObj.getbest(preftype='mp4')
        url = shorten(video.url)
        return url, 'https://img.youtube.com/vi/%s/mqdefault.jpg' % (pafyObj.videoid)
    except Exception as e:
        raise e

def youtubedownload(token, query, mode):
    try:
        pafyObj = pafy.new(query)
        kata = '『Youtube Download』\n'
        image = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % (pafyObj.videoid)
        if int(mode) == 1:
            videolist = pafyObj.streams
            for a in videolist:
                realreso = a.resolution.split('x')
                kata += '\n %s %s %s' % (a.extension, str(realreso[1])+'p', humansize(a.get_filesize()))
                kata += '\n%s\n' % (str(shorten(a.url)))
        elif int(mode) == 2:
            audiolist = pafyObj.audiostreams
            for a in audiolist:
                kata += '\n %s %s %s' % (a.extension, a.bitrate, humansize(a.get_filesize()))
                kata += '\n%s\n' % (str(shorten(a.url)))
        customMessage(token, [
                ImageSendMessage(original_content_url=image, preview_image_url=image),
                TextSendMessage(text=str(kata))
            ])
    except Exception as e:
        raise e

def humansize(nbytes):
    try:
        i = 0
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
        while nbytes >= 1024 and i < len(suffixes)-1:
            nbytes /= 1024.
            i += 1
        f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
        return '%s %s' % (f, suffixes[i])
    except Exception as e:
        raise e

def instapost(token, username, query, berapa):
    try:
        link = 'http://rahandiapi.herokuapp.com/instapost/%s/%s?key=randi123' % (username, query)
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            if data['see'] == True:
                if data['banyak'] == True:
                    data = data['media']
                    medtipe = data['mediatype']
                    kata = data['caption']
                    kata += '\n\nlike: %s' % (data['like_count'])
                    kata += '\ncomment: %s' % (data['comment_count'])
                    if medtipe == 1:
                        url = data['url']
                        kata += '\nlink: %s' % (shorten(url))
                        customMessage(token, [
                            ImageSendMessage(original_content_url=url, preview_image_url=url),
                            TextSendMessage(text = str(kata))
                            ])
                    elif medtipe == 2:
                        url = data['url']
                        pripiw = data['preview']
                        kata += '\nlink: %s' % (shorten(url))
                        customMessage(token, [
                            VideoSendMessage(original_content_url=url, preview_image_url=pripiw),
                            TextSendMessage(text = str(kata))
                            ])
                    elif medtipe == 8:
                        urllist = data['url']
                        TB = []
                        amon = len(urllist)
                        tipe = 'img'
                        for a in urllist:
                            isi_TB = {}
                            medtype = a['mediatype']
                            if medtype == 1:
                                isi_TB['tumbnail'] = a['url']
                                isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a['url']])
                            elif medtype == 2:
                                isi_TB['tumbnail'] = a['preview']
                                isi_TB['action'] = actionBuilder(1, ['uri'], ['video'], [a['url']])
                            TB.append(isi_TB)
                        dat = {}
                        dat['alt'] = 'Multi_Bots instapost'
                        dat['template'] = templateBuilder(amon, tipe, TB)
                        customMessage(token, [
                            TemplateSendMessage(alt_text=dat['alt'], template=dat['template']),
                            TextSendMessage(text = str(kata))
                            ])
                else:
                    replyTextMessage(token, 'post-ke yang diminta melebihi jumlah post yang ada di akun ini')
            else:
                replyTextMessage(token, 'akun di private, akan mencoba mem-follow, coba beberapa saat lagi')
        else:
            if int(berapa) >= 5:
                replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
            else:
                berapa = str(int(berapa)+1)
                instapost(token, username, query, berapa)
    except Exception as e:
        if int(berapa) >= 5:
            raise e
        else:
            berapa = str(int(berapa) + 1)
            instapost(token, username, query, berapa)

def instastory(token, username, berapa):
    try:
        link = 'http://rahandiapi.herokuapp.com/instastory/%s?key=randi123' % (username)
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            if len(data['url']) == 0:
                if data['reason'] == 1:
                    replyTextMessage(token, 'akun %s tidak membuat story dalam 24 jam terakhir' % (username))
                    return
                elif data['reason'] == 2:
                    replyTextMessage(token, 'akun %s di private, akan mencoba mem-follow, coba beberapa saat lagi' % (username))
                    return
            else:
                url = data['url']
                TB = []
                tipe = 'img'
                for a in url:
                    med = a['tipe']
                    isi_TB = {}
                    if med == 1:
                        isi_TB['tumbnail'] = a['link']
                        isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a['link']])
                    elif med == 2:
                        isi_TB['tumbnail'] = a['preview']
                        isi_TB['action'] = actionBuilder(1, ['uri'], ['video'], [a['link']])
                    TB.append(isi_TB)
                    if len(TB) >= 50:
                        break
                TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
                cus = []
                for a in TB:
                    kirimlist = {}
                    kirimlist['alt'] = 'Multi_Bots instastory'
                    kirimlist['template'] = templateBuilder(len(a), tipe, a)
                    kirimasli = TemplateSendMessage(alt_text=kirimlist['alt'], template=kirimlist['template'])
                    cus.append(kirimasli)
                customMessage(token, cus)
        else:
            if int(berapa) >= 5:
                replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
            else:
                berapa = str(int(berapa) + 1)
                instastory(token, username, berapa)
    except Exception as e:
        if int(berapa) >= 5:
            raise e
        else:
            berapa = str(int(berapa) + 1)
            instastory(token, username, berapa)

def instainfo(token, username, berapa):
    try:
        link = 'https://rahandiapi.herokuapp.com/instainfo/%s?key=randi123' % (str(username))
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            result = data['result']
            image = result['url']
            kata = '『Instagram Info』\n\n'
            kata += 'Username: ' + result['username']
            kata += '\nName: ' + result['name']
            kata += '\nTotal post: ' + str(result['mediacount'])
            kata += '\nFollower: ' + str(result['follower'])
            kata += '\nFollowing: ' + str(result['following'])
            kata += '\nPrivate: ' + str(result['private'])
            kata += '\nBio: ' + str(result['bio'])
            customMessage(token, [
                    ImageSendMessage(original_content_url=image, preview_image_url=image),
                    TextSendMessage(text=str(kata))
                ])
        else:
            if int(berapa) >= 5:
                replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
            else:
                berapa = str(int(berapa) + 1)
                instainfo(token, username, berapa)
    except Exception as e:
        if int(berapa) >= 5:
            raise e
        else:
            berapa = str(int(berapa) + 1)
            instainfo(token, username, berapa)

def gimage(token, query):
    try:
        query = query.replace(' ', '+')
        link = 'https://www.google.co.id/search?q=' + query +'&dcr=0&source=lnms&tbm=isch&sa=X&ved=0ahUKEwje9__4z6nXAhVMKY8KHUFCCbwQ_AUICigB&biw=1366&bih=672'
        headers = {}
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
        data = requests.get(link, headers=headers)
        data = data.text.encode('utf-8').decode('ascii', 'ignore')
        filtered = SoupStrainer('div', {'class':'rg_meta notranslate'})
        soup = BeautifulSoup(data, 'lxml', parse_only = filtered)
        piclist = []
        for a in soup.find_all('div', {'class':'rg_meta notranslate'}):
            try:
                jsonnya = json.loads(str(a.text))
                piclist.append(jsonnya['ou'])
            except Exception as e:
                pass
        TB  = []
        amon = 10
        tipe = 'img'
        random.shuffle(piclist)
        removemark = []
        for a in range(len(piclist)):
            if 'http://' in piclist[a]:
                removemark.append(piclist[a])
        for a in removemark:
            piclist.remove(a)
        for a in range(10):
            isi_TB = {}
            isi_TB['tumbnail'] = piclist[a]
            isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [piclist[a]])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots Gimage'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def wikiped(token, query):
    try:
        image = None
        wikipedia.set_lang('id')
        hasil = wikipedia.summary(query, sentences=3)
        link = wikipedia.page(query).url
        data = requests.get(link).text
        soup = BeautifulSoup(data, 'lxml')
        for a in soup.find_all('meta', {'property':'og:image'}):
            image = a['content']
        if image != None:
            customMessage(token, [
                ImageSendMessage(original_content_url=image, preview_image_url=image),
                TextSendMessage(text = str(hasil))
                ])
        else:
            replyTextMessage(token, str(hasil))
    except Exception as e:
        raise e
def lyriclagu(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'http://rahandiapi.herokuapp.com/lyricapi?key=randi123&q=' + query
        data = json.loads(requests.get(link).text)
        if data['find'] == True:
            kata = data['title'] + '\n\n'
            kata += data['lyric']
            replyTextMessage(token, str(kata))
        else:
            replyTextMessage(token, 'lyric tidak ditemukan')
    except Exception as e:
        raise e

def gifgifter(token, query):
    try:
        link = 'https://api.tenor.com/v1/search?key=LIVDSRZULELA&q=%s&limit=1' % (query)
        data = json.loads(requests.get(link).text)
        gifnya = data['results'][0]['media'][0]['gif']['url']
        TB = []
        amon = 1
        tipe = 'img'
        isi_TB = {}
        isi_TB['tumbnail'] = gifnya
        isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [gifnya])
        TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots Gif'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def chatbot(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'http://api.ntcorp.us/chatbot/v1/?text=%s&key=beta1.nt&local=id' % (query)
        data = json.loads(requests.get(link).text)
        if data['result']['result'] == 100:
            realresp = data['result']['response']
            replyTextMessage(token, str(realresp))
        else:
            replyTextMessage(token, 'error')
    except Exception as e:
        raise e

def gaul(token, query):
    try:
        quer = query.replace("'", "-")
        link = 'https://kitabgaul.com/api/entries/%s' % (quer)
        data = json.loads(requests.get(link).text)
        if len(data['entries']) == 0:
            replyTextMessage(token, 'kata %s tidak ditemukan' % (query))
        else:
            kata = '『Hasil kata gaul %s』\n' % (query)
            kata += '\nDefinisi:\n%s\n' % (data['entries'][0]['definition'])
            kata += '\nContoh:\n%s' % (data['entries'][0]['example'])
            replyTextMessage(token, str(kata))
    except Exception as e:
        raise e

def devian(token, mode, query=None):
    try:
        if mode == 0:
            find = devapi.browse(endpoint='popular', q=query)
            listdev = find['results']
            listpict = []
            for a in listdev:
                try:
                    dwn = devapi.download_deviation(a)
                    listpict.append(dwn['src'])
                except:
                    pass
            TB = []
            amon = len(listpict)
            if amon == 0:
                replyTextMessage(token, '0 found')
                return
            tipe = 'img'
            for a in range(len(listpict)):
                isi_TB = {}
                isi_TB['tumbnail'] = listpict[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [listpict[a]])
                TB.append(isi_TB)
            dat = {}
            dat['alt'] = 'Multi_Bots Deviantart Search'
            dat['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, dat)
        elif mode == 1:
            find = devapi.browse()
            listdev = find['results']
            listpict = []
            for a in listdev:
                try:
                    dwn = devapi.download_deviation(a)
                    listpict.append(dwn['src'])
                except:
                    pass
            TB = []
            amon = len(listpict)
            if amon == 0:
                replyTextMessage(token, '0 found')
                return
            tipe = 'img'
            for a in range(len(listpict)):
                isi_TB = {}
                isi_TB['tumbnail'] = listpict[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [listpict[a]])
                TB.append(isi_TB)
            dat = {}
            dat['alt'] = 'Multi_Bots Deviantart Hot'
            dat['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, dat)
    except Exception as e:
        raise e

def sholat(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'https://time.siswadi.com/pray/' + str(query)
        data = json.loads(requests.get(link).text)
        alamat = data['location']['address']
        shubuh = data['data']['Fajr']
        dzuhur = data['data']['Dhuhr']
        ashar = data['data']['Asr']
        maghrib = data['data']['Maghrib']
        isya = data['data']['Isha']
        kata = '『Jadwal Sholat』\n'
        kata += '\n%s\n' % (alamat)
        kata += '\nShubuh: %s\nDzuhur: %s\nAshar: %s\nMaghrib: %s\nIsya: %s' % (shubuh,dzuhur,ashar,maghrib,isya)
        replyTextMessage(token, str(kata))
    except Exception as e:
        raise e

def lovecalc(token, nameA, nameB):
    try:
        jumlahA = 0
        jumlahB = 0
        for a in nameA:
            jumlahA = jumlahA + ord(a)
        for b in nameB:
            jumlahB = jumlahB + ord(b)
        persen = (jumlahA*jumlahB) % 100
        persen = str(persen) + '%'
        replyTextMessage(token, '%s dan %s\ncocok %s' % (nameA, nameB, str(persen)))
    except Exception as e:
        raise e

def googlestreet(token, query):
    try:
        query = requests.utils.requote_uri(query)
        link = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?input=%s&key=AIzaSyAmZEqjaYKV1VcaKm8blPrFMu1w6fzWww0' % (query)
        data = json.loads(requests.get(link).text)
        if len(data['predictions']) == 0:
            replyTextMessage(token, 'lokasi tidak ditemukan')
            return
        data = data['predictions'][0]['description']
        data = requests.utils.requote_uri(data)
        link = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=%s&key=AIzaSyB0OAiwnVjxOZikcWh8KHymIKzkR1ufjGg' % (data)
        data = json.loads(requests.get(link).text)
        namatempat = data['results'][0]['formatted_address']
        nick = data['results'][0]['name']
        lat = data['results'][0]['geometry']['location']['lat']
        lng = data['results'][0]['geometry']['location']['lng']
        pic = [
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=0&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=90&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=180&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=270&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng)
        ]
        TB = []
        amon = len(pic)
        tipe = 'img'
        for a in pic:
            isi_TB = {}
            isi_TB['tumbnail'] = a
            isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots location'
        dat['template'] = templateBuilder(amon, tipe, TB)
        customMessage(token,[
            LocationSendMessage(title=nick[:100], address=namatempat[:100], latitude=lat, longitude=lng),
            TemplateSendMessage(alt_text=dat['alt'], template=dat['template'])
        ])
    except Exception as e:
        raise e

def kotakin(token, messageId, mode):
    try:
        path = donwloadContent(messageId)
        im = Image.open(path)
        width, height = im.size
        if mode == 1:
            if width > height:
                ukuran = height
            else:
                ukuran = width
        elif mode == 2:
            if width > height:
                ukuran = width
            else:
                ukuran = height
        left = (width-ukuran)/2
        top = (height-ukuran)/2
        right = (width+ukuran)/2
        bottom = (height+ukuran)/2
        crop = im.crop((left, top, right, bottom))
        crop.save(path)
        data = imgur.upload_from_path(path, config=None, anon=False)
        os.remove(path)
        replyImageMessage(token, data['link'], data['link'])
    except Exception as e:
        raise e

def memegen(token, msgId, query):
    try:
        path = donwloadContent(msgId)
        data = imgur.upload_from_path(path, config=None, anon=False)
        os.remove(path)
        link = 'https://memegen.link/custom/%s/%s.jpg?alt=%s' % (query[0], query[1], data['link'])
        replyImageMessage(token, link, link)
    except Exception as e:
        raise e

def myanime(token, mode, query=None):
    try:
        if mode == 0:
            judul, link, img = myanimelist.getTopAiring()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(2, ['postback', 'uri'], ['description', 'link'], ['anidesc %s' % (link[a]), link[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Top Airing Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            judul, link, img = myanimelist.getTopUpcoming()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(2, ['postback', 'uri'], ['description', 'link'], ['anidesc %s' % (link[a]), link[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Top Upcoming Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 2:
            judul, link, img = myanimelist.getMostPopular()
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Rank %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(2, ['postback', 'uri'], ['description', 'link'], ['anidesc %s' % (link[a]), link[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Most Popular Anime'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 3:
            kembali = myanimelist.detailAnime(query)
            teks = '%s\n\nScore %s\n%s\n%s\n\n%s' % (kembali['judul'], kembali['score'], kembali['rank'], kembali['popularity'], kembali['description'])
            customMessage(token, [
                ImageSendMessage(original_content_url=kembali['image'], preview_image_url=kembali['image']),
                TextSendMessage(text = teks)
            ])
        elif mode == 4:
            judul, link, img = myanimelist.searchAnime(query)
            TB = []
            tipe = 'template'
            amon = len(img)
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = img[a]
                isi_TB['title'] = judul[a][:40]
                isi_TB['text'] = 'Urutan %s' % (int(a) + 1)
                isi_TB['action'] = actionBuilder(2, ['postback', 'uri'], ['description', 'link'], ['anidesc %s' % (link[a]), link[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots Anime Search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
    except Exception as e:
        raise e

def apipixiv(token, mode, query=None):
    try:
        if mode == 0:
            imagelist = pixiv.search(query)
            TB = []
            amon = len(imagelist)
            tipe = 'img'
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = imagelist[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['direct link'], [imagelist[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots pixiv search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            imagelist = pixiv.ranking()
            TB = []
            amon = len(imagelist)
            tipe = 'img'
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = imagelist[a]
                isi_TB['action'] = actionBuilder(1, ['uri'], ['Rank %s' % (a+1)], [imagelist[a]])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots pixiv rank'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
    except Exception as e:
        raise e

def savejson():
    try:
        file = open('%s/data/jsondata' % (workdir), 'w')
        file.write(json.dumps(important, indent=2))
        file.close
    except Exception as e:
        raise e

def help(token, mode=0):
    try:
        if mode == 0:
            TB = []
            tipe = 'template'
            tumbnail = [
                'https://i.ytimg.com/vi/CVXp3ZgUIr8/maxresdefault.jpg', 
                'https://www.gulfeyes.net/content/uploads/2017/09/22/9221c046e5.jpg',
                'https://lh3.googleusercontent.com/-qXt3ofPwbOU/VVZ_PbR6CsI/AAAAAAAAABY/IeVNLmQOwpQ/s530-p/AnimeLogo.png',
                'https://static1.squarespace.com/static/56c25cd620c647590146e9c2/572bc1101bbee0b556462e85/572bc1181bbee0b556462ed4/1462485275992/styleframes4.png',
                'https://i.pinimg.com/736x/87/02/e6/8702e60c04893b6d32c7e96d9c7f7e32--social-community-antique-shops.jpg',
                'https://image.ibb.co/gjJwhG/TU_LOGO_300dpi.png',
                'https://logosave.com/images/large/23/About-logo.gif']
            text = [
                'youtube help',
                'instagram help',
                'anime help',
                'pixiv help',
                'deviantart help',
                'stuff help',
                'about']
            dataaction = [
                'help youtube',
                'help instagram',
                'help anime',
                'help pixiv',
                'help deviantart',
                'help stuff',
                'help about']
            amon = len(tumbnail)
            for a in range(0, amon):
                isi_TB = {}
                isi_TB['tumbnail'] = tumbnail[a]
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = [actionBuilder(1, ['postback'], ['help'], [dataaction[a]])]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots main Help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 1:
            TB = []
            tipe = 'template'
            amon = 7
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-search: anime'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-link: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-audio: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-video: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download-video: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/youtube-download-audio: https://www.youtube.com/watch?v=UDjuWmhIKuE'])])
            text = [
                '/youtube-search: [query]',
                '/youtube-link: [link youtube]',
                '/youtube-audio: [link youtube]',
                '/youtube-video: [link youtube]',
                '/youtube-download: [link youtube]',
                '/youtube-download-video: [link youtube]',
                '/youtube-download-audio: [link youtube]'
            ]
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 2:
            TB = []
            tipe = 'template'
            amon = 3
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instapost 1 anime.niisan'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instastory anime.niisan'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/instainfo anime.niisan'])])
            text = [
                '/instapost [post-ke] [username]',
                '/instastory [username]',
                '/instainfo [username]'
            ]
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots instagram help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 3:
            TB = []
            tipe = 'template'
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gimage: kaho hinata'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/lyric: numb linkin park'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gif: hehehehehe'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/wiki: mobil'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/chat: siapa namamu?'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/gaul: kuy'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/sholat: surabaya'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/love: koyo akizuki + kaho hinata'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/loc: surabaya'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/kotakin: 2'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/memegen: coba | saja'])])
            text = []
            text.append('/gimage: [query]')
            text.append('/lyric: [query]')
            text.append('/gif: [query]')
            text.append('/wiki: [query]')
            text.append('/chat: [query]')
            text.append('/gaul: [query]')
            text.append('/sholat: [lokasi]')
            text.append('/love: [nama pertama] + [nama kedua]')
            text.append('/loc: [lokasi]')
            text.append('/kotakin: [angka 1 atau 2]')
            text.append('/memegen: [top text] | [bottom text]')
            for a in range(len(action)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            TB = [TB[i:i+10] for i in range(0, len(TB), 10)]
            cus = []
            for a in TB:
                kirimlist = {}
                kirimlist['alt'] = 'Multi_Bots stuff help'
                kirimlist['template'] = templateBuilder(len(a), tipe, a)
                kirimasli = TemplateSendMessage(alt_text=kirimlist['alt'], template=kirimlist['template'])
                cus.append(kirimasli)
            customMessage(token, cus)
        elif mode == 4:
            TB = []
            tipe = 'template'
            amon = 2
            action = []
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/admin'])])
            action.append([actionBuilder(1, ['msg'], ['coba'], ['/leave'])])
            text = ['/admin', '/leave']
            for a in range(amon):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots about help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 5:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/anime-search: overlord'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime top airing'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime top upcoming'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/anime most popular'])]
            ]
            text = [
                '/anime-search: [query]',
                '/anime top airing',
                '/anime top upcoming',
                '/anime most popular'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots anime help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 6:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/pixiv-search: no game no life'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/pixiv rank'])]
            ]
            text = [
                '/pixiv-search: [query]',
                '/pixiv rank'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots pixiv help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
        elif mode == 7:
            TB = []
            tipe = 'template'
            action = [
                [actionBuilder(1, ['msg'], ['coba'], ['/deviant-search: dark'])],
                [actionBuilder(1, ['msg'], ['coba'], ['/deviant hot'])]
            ]
            text = [
                '/deviant-search: [query]',
                '/deviant hot'
            ]
            for a in range(len(text)):
                isi_TB = {}
                isi_TB['tumbnail'] = None
                isi_TB['title'] = None
                isi_TB['text'] = text[a]
                isi_TB['action'] = action[a]
                TB.append(isi_TB)
            amon = len(text)
            data = {}
            data['alt'] = 'Multi_Bots Deviantart help'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(token, data)
    except Exception as e:
        raise e

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    try:
        op = json.loads(str(event))
        reply_token = op['replyToken']
        data = {}
        data['alt'] = 'Multi_Bots Joined'
        data['tumbnail'] = None
        data['title'] = 'Multi_Bots'
        data['text'] = 'klik tombol dibawah ini untuk bantuan penggunaan'
        data['action'] = [actionBuilder(1, ['postback'], ['help'], ['help'])]
        replyTemplateMessage(reply_token, data)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    op = json.loads(str(event))
    msgtext = op['message']['text']
    reply_token = op['replyToken']
    try:
        if msgtext.lower() in ['help', 'key', 'cmd', 'command']:
            help(reply_token)
        elif msgtext.lower().startswith('/youtube-audio: '):
            query = msgtext[16:]
            url = youtubemp3(query)
            replyAudioMessage(reply_token, url)
        elif msgtext.lower().startswith('/youtube-video: '):
            query = msgtext[16:]
            url, preview = youtubevideo(query)
            replyVideoMessage(reply_token, url, preview)
        elif msgtext.lower().startswith('/youtube-link: '):
            query = msgtext[15:]
            dat = pafy.new(query)
            data = {}
            data['alt'] = 'Multi_Bots Youtube'
            data['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % dat.videoid
            data['title'] = None
            data['text'] = str(dat.title)
            data['action'] = actionBuilder(4, ['msg', 'msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download Video', 'download Audio'], ['/youtube-video: %s' % (query), '/youtube-audio: %s' % (query), '/youtube-download-video: %s' % (query), '/youtube-download-audio: %s' % (query)])
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-search: '):
            query = msgtext[17:]
            title, url, videoid = youtubesearch(query)
            TB = []
            amon = 10
            tipe = 'template'
            for a in range(0, amon):
                isi_TB = {}
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % videoid[a]
                isi_TB['title'] = None
                isi_TB['text'] = str(title[a])[:60]
                isi_TB['action'] = actionBuilder(3, ['msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download'], ['/youtube-video: %s' % (url[a]), '/youtube-audio: %s' % (url[a]), '/youtube-download: %s' % (url[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube-search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-download: '):
            query = msgtext[19:]
            dat = pafy.new(query)
            data = {}
            data['alt'] = 'Multi_Bots Youtube'
            data['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % dat.videoid
            data['title'] = None
            data['text'] = str(dat.title)
            data['action'] = actionBuilder(2, ['msg', 'msg'], ['download Video', 'download Audio'], ['/youtube-download-video: %s' % (query), '/youtube-download-audio: %s' % (query)])
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower().startswith('/youtube-download-video: '):
            query = msgtext[25:]
            youtubedownload(reply_token, query, 1)
        elif msgtext.lower().startswith('/youtube-download-audio: '):
            query = msgtext[25:]
            youtubedownload(reply_token, query, 2)
        elif msgtext.lower() == 'sp':
            sekarang = time.time()
            line_bot_api.reply_message(reply_token, [TextSendMessage(text = '...'), TextSendMessage(text = str(time.time()-sekarang))])
        elif msgtext.lower().startswith('/instapost '):
            query = msgtext[11:]
            query = query.split(' ')
            instapost(reply_token, query[1], query[0], 1)
        elif msgtext.lower().startswith('/instastory '):
            query = msgtext[12:]
            instastory(reply_token, query, 1)
        elif msgtext.lower().startswith('/instainfo '):
            query = msgtext[11:]
            instainfo(reply_token, query, 1)
        elif msgtext.lower().startswith('/gimage: '):
            query = msgtext[9:]
            gimage(reply_token, query)
        elif msgtext.lower().startswith('/wiki: '):
            query = msgtext[7:]
            wikiped(reply_token, query)
        elif msgtext.lower().startswith('/lyric: '):
            query = msgtext[8:]
            lyriclagu(reply_token, query)
        elif msgtext.lower().startswith('/gif: '):
            query = msgtext[6:]
            gifgifter(reply_token, query)
        elif msgtext.lower().startswith('/chat: '):
            query = msgtext[7:]
            chatbot(reply_token, query)
        elif msgtext.lower().startswith('/gaul: '):
            query = msgtext[7:]
            gaul(reply_token, query)
        elif msgtext.lower().startswith('/deviant-search: '):
            query = msgtext[17:]
            devian(reply_token, 0, query)
        elif msgtext.lower() == '/deviant hot':
            devian(reply_token, 1)
        elif msgtext.lower().startswith('/sholat: '):
            query = msgtext[9:]
            sholat(reply_token, query)
        elif msgtext.lower().startswith('/love: '):
            query = msgtext[7:]
            query = query.split(' + ')
            if len(query) !=  2:
                replyTextMessage(reply_token, 'format yang dimasukkan salah')
                return
            else:
                lovecalc(reply_token, query[0], query[1])
        elif msgtext.lower().startswith('/loc: '):
            query = msgtext[6:]
            googlestreet(reply_token, query)
        elif msgtext.lower() == '/anime top airing':
            myanime(reply_token, 0)
        elif msgtext.lower() == '/anime top upcoming':
            myanime(reply_token, 1)
        elif msgtext.lower() == '/anime most popular':
            myanime(reply_token, 2)
        elif msgtext.lower().startswith('/anime-search: '):
            query = msgtext[15:]
            if len(query) < 3:
                replyTextMessage(reply_token, 'minimum 3 character')
            else:
                myanime(reply_token, 4, query)
        elif msgtext.lower().startswith('/pixiv-search: '):
            query = msgtext[15:]
            apipixiv(reply_token, 0, query)
        elif msgtext.lower() == '/pixiv rank':
            apipixiv(reply_token, 1)
        elif msgtext.lower().startswith('/kotakin: '):
            query = msgtext[10:]
            query = int(query)
            if query != 1 and query != 2:
                replyTextMessage(reply_token, 'hanya bisa mode 1 atau 2')
            else:
                msgsource = op['source']['type']
                msgfrom = op['source']['userId']
                try:
                    name = json.loads(str(line_bot_api.get_profile(msgfrom)))
                except Exception as e:
                    replyTextMessage(reply_token, 'system tidak bisa mencatat akun anda\nadd dulu ya ~')
                    return
                if msgsource == 'user':
                    if msgsource not in important['kotakin']:
                        important['kotakin'][msgsource] = {}
                        important['kotakin'][msgsource][msgfrom] = query
                    else:
                        if msgfrom not in important['kotakin'][msgsource]:
                            important['kotakin'][msgsource][msgfrom] = query
                else:
                    try:
                        ID = op['source']['roomId']
                    except Exception as e:
                        ID = op['source']['groupId']
                    if msgsource not in important['kotakin']:
                        important['kotakin'][msgsource] = {}
                        important['kotakin'][msgsource][ID] = {}
                        important['kotakin'][msgsource][ID][msgfrom] = query
                    else:
                        if ID not in important['kotakin'][msgsource]:
                            important['kotakin'][msgsource][ID] = {}
                            important['kotakin'][msgsource][ID][msgfrom] = query
                        else:
                            if msgfrom not in important['kotakin'][msgsource][ID]:
                                important['kotakin'][msgsource][ID][msgfrom] = query
                savejson()
                replyTextMessage(reply_token, '%s silahkan kirim gambar' % (name['displayName']))
        elif msgtext.lower().startswith('/memegen: '):
            query = msgtext[10:]
            query = query.split(' | ')
            if len(query) != 2:
                replyTextMessage(reply_token, 'format yang dimasukkan salah')
            else:
                query = msgtext[10:]
                query = query.replace('-', '--')
                query = query.replace('_', '__')
                query = query.replace('?', '~q')
                query = query.replace('%', '~p')
                query = query.replace('#', '~h')
                query = query.replace('/', '~s')
                query = query.replace("''", '"')
                query = query.split(' | ')
                tipe = op['source']['type']
                userId = op['source']['userId']
                try:
                    name = json.loads(str(line_bot_api.get_profile(userId)))
                except Exception as e:
                    replyTextMessage(reply_token, 'system tidak bisa mencatat akun anda\nadd dulu ya ~')
                    return
                if tipe == 'user':
                    if tipe not in important['memegen']:
                        important['memegen'][tipe] = {}
                        important['memegen'][tipe][userId] = query
                    else:
                        if msgfrom not in important['memegen'][tipe]:
                            important['memegen'][tipe][userId] = query
                else:
                    try:
                        ID = op['source']['roomId']
                    except Exception as e:
                        ID = op['source']['groupId']
                    if tipe not in important['memegen']:
                        important['memegen'][tipe] = {}
                        important['memegen'][tipe][ID] = {}
                        important['memegen'][tipe][ID][userId] = query
                    else:
                        if ID not in important['memegen'][tipe]:
                            important['memegen'][tipe][ID] = {}
                            important['memegen'][tipe][ID][userId] = query
                        else:
                            if msgfrom not in important['memegen'][tipe][ID]:
                                important['memegen'][tipe][ID][userId] = query
                savejson()
                replyTextMessage(reply_token, '%s silahkan kirim gambar' % (name['displayName']))
        elif msgtext.lower() == '/admin':
            data = json.loads(str(line_bot_api.get_profile(adminid)))
            data['alt'] = 'Multi_Bots admin'
            data['tumbnail'] = None
            data['title'] = data['displayName']
            data['text'] = 'developer'
            data['action'] = [actionBuilder(1, ['uri'], ['add'], ['line://ti/p/~rahandi'])]
            replyTemplateMessage(reply_token, data)
        elif msgtext.lower() == '//coba help':
            help(reply_token)
        elif msgtext.lower() == '//cetak op':
            replyTextMessage(reply_token, json.dumps(op, indent=2))
        elif msgtext.lower() == '//cetak profile':
            profile = json.loads(str(line_bot_api.get_profile(op['source']['userId'])))
            replyTextMessage(reply_token, json.dumps(profile, indent=2))
        elif msgtext.lower() == '/leave':
            if op['source']['type'] == 'group':
                replyTextMessage(reply_token, ':(')
                line_bot_api.leave_group(op['source']['groupId'])
            elif op['source']['type'] == 'room':
                replyTextMessage(reply_token, ':(')
                line_bot_api.leave_room(op['source']['roomId'])
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(MessageEvent, message=ImageMessage)
def handle_imgmessage(event):
    op = json.loads(str(event))
    reply_token = op['replyToken']
    userId = op['source']['userId']
    msgId = op['message']['id']
    tipe = op['source']['type']
    if tipe == 'room':
        ID = op['source']['roomId']
    elif tipe == 'group':
        ID = op['source']['groupId']
    try:
        if tipe in important['kotakin']:
            if tipe == 'user':
                if tipe in important['kotakin']:
                    if userId in important['kotakin'][tipe]:
                        mode = important['kotakin'][tipe][userId]
                        try:
                            del important['kotakin'][tipe][userId]
                        except:
                            pass
                        kotakin(reply_token, msgId, mode)
            else:
                if tipe in important['kotakin']:
                    if ID in important['kotakin'][tipe]:
                        if userId in important['kotakin'][tipe][ID]:
                            mode = important['kotakin'][tipe][ID][userId]
                            try:
                                del important['kotakin'][tipe][ID][userId]
                            except:
                                pass
                            kotakin(reply_token, msgId, mode)
            savejson()
        if tipe in important['memegen']:
            if tipe == 'user':
                if tipe in important['memegen']:
                    if userId in important['memegen'][tipe]:
                        mode = important['memegen'][tipe][userId]
                        try:
                            del important['memegen'][tipe][userId]
                        except:
                            pass
                        memegen(reply_token, msgId, mode)
            else:
                if tipe in important['memegen']:
                    if ID in important['memegen'][tipe]:
                        if userId in important['memegen'][tipe][ID]:
                            mode = important['memegen'][tipe][ID][userId]
                            try:
                                del important['memegen'][tipe][ID][userId]
                            except:
                                pass
                            memegen(reply_token, msgId, mode)
            savejson()
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(MessageEvent, message=LocationMessage)
def handle_locmessage(event):
    op = json.loads(str(event))
    lat = op['message']['latitude']
    lng = op['message']['longitude']
    reply_token = op['replyToken']
    try:
        pic = [
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=0&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=90&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=180&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng),
            'https://maps.googleapis.com/maps/api/streetview?location=%s,%s&size=600x400&heading=270&key=AIzaSyAQmw_o6BhLfnH5LMM2B8oDGyHMx6QC--Y' % (lat, lng)
        ]
        TB = []
        amon = len(pic)
        tipe = 'img'
        for a in pic:
            isi_TB = {}
            isi_TB['tumbnail'] = a
            isi_TB['action'] = actionBuilder(1, ['uri'], ['image'], [a])
            TB.append(isi_TB)
        dat = {}
        dat['alt'] = 'Multi_Bots location'
        dat['template'] = templateBuilder(amon, tipe, TB)
        replyCarrouselMessage(reply_token, dat)
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    except Exception as e:
        replyTextMessage(reply_token, 'error')
        print(e)

@handler.add(PostbackEvent)
def handle_postback(event):
    op = json.loads(str(event))
    reply_token = op['replyToken']
    postbackdata = op['postback']['data']
    try:
        if postbackdata.lower() == 'help':
            help(reply_token)
        elif postbackdata.lower() == 'help youtube':
            help(reply_token, 1)
        elif postbackdata.lower() == 'help instagram':
            help(reply_token, 2)
        elif postbackdata.lower() == 'help stuff':
            help(reply_token, 3)
        elif postbackdata.lower() == 'help about':
            help(reply_token, 4)
        elif postbackdata.lower() == 'help anime':
            help(reply_token, 5)
        elif postbackdata.lower() == 'help pixiv':
            help(reply_token, 6)
        elif postbackdata.lower() == 'help deviantart':
            help(reply_token, 7)
        elif postbackdata.lower().startswith('anidesc '):
            data = postbackdata[8:]
            myanime(reply_token, 3, data)
        else:
            replyTextMessage(reply_token, str(postbackdata))
    except LineBotApiError as e:
        replyTextMessage(reply_token, 'error')
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
