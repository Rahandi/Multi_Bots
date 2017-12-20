import os, time, json, requests, pafy, random, wikipedia
from flask import Flask, request, abort
from bs4 import BeautifulSoup, SoupStrainer

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
        else:
            for i in range(0, amount):
                if type[i] == 'msg':
                    apped = MessageTemplateAction(label=param1[i], text=param2[i])
                elif type[i] == 'uri':
                    apped = URITemplateAction(label=param1[i], uri=param2[i])
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
        if int(berapa) >= 5:
            replyTextMessage(token, 'error')
            return
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
            replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
    except Exception as e:
        berapa = str(int(berapa) + 1)
        instapost(token, username, query, berapa)
        raise e

def instastory(token, usename):
    try:
        link = 'http://rahandiapi.herokuapp.com/instastory/%s?key=randi123' % (usename)
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
            replyTextMessage(token, 'akun %s tidak ditemukan' % (username))
    except Exception as e:
        raise e

def instainfo(token, username):
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
    except Exception as e:
        raise e

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
        replyTextMessage(reply_token, 'Terimakasih telah mengundang\n\nketik help untuk bantuan penggunaan')

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
            file = open('help', 'r')
            texet = file.read()
            file.close()
            replyTextMessage(reply_token, texet)
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
                isi_TB['action'] = actionBuilder(2, ['msg', 'msg'], ['send Video', 'send Audio'], ['/youtube-video: %s' % (url[a]), '/youtube-audio: %s' % (url[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube-search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
        elif msgtext.lower().startswith('debug: '):
            query = msgtext[7:]
            title, url, videoid = youtubesearch(query)
            TB = []
            amon = 10
            tipe = 'template'
            for a in range(0, amon):
                isi_TB = {}
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/%s/hqdefault.jpg' % videoid[a]
                isi_TB['title'] = None
                isi_TB['text'] = str(title[a])[:60]
                isi_TB['action'] = actionBuilder(4, ['msg', 'msg', 'msg', 'msg'], ['send Video', 'send Audio', 'download Video', 'download Audio'], ['/youtube-video: %s' % (url[a]), '/youtube-audio: %s' % (url[a]), '/youtube-download-video: %s' % (url[a]), '/youtube-download-audio: %s' % (url[a])])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'Multi_Bots youtube-search'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
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
            instastory(reply_token, query)
        elif msgtext.lower().startswith('/instainfo '):
            query = msgtext[11:]
            instainfo(reply_token, query)
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
        elif msgtext.lower() == 'self profile':
            data = line_bot_api.get_profile(op['source']['userId'])
            data = json.loads(str(data))
            replyTextMessage(reply_token, json.dumps(data, indent=2))
        elif msgtext.lower() == '///coba':
            TB = []
            isi_TB = {}
            amon = 2
            tipe = 'img'
            for i in range(0, amon):
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/yq6VhQGz-no/hqdefault.jpg'
                isi_TB['action'] = actionBuilder(1, ['msg'], ['satu'], ['a'])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'uji coba carrousel'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
        elif msgtext.lower() == '///coba image':
            TB = []
            isi_TB = {}
            amon = 2
            tipe = 'template'
            for i in range(0, amon):
                isi_TB['tumbnail'] = 'https://img.youtube.com/vi/yq6VhQGz-no/hqdefault.jpg'
                isi_TB['title'] = 'coba'
                isi_TB['text'] = 'txt'
                isi_TB['action'] = actionBuilder(2, ['msg', 'msg'], ['satu', 'dua'], ['a', 'b'])
                TB.append(isi_TB)
            data = {}
            data['alt'] = 'uji coba carrousel'
            data['template'] = templateBuilder(amon, tipe, TB)
            replyCarrouselMessage(reply_token, data)
        elif msgtext.lower() == '/cetak op':
            replyTextMessage(reply_token, json.dumps(op, indent=2))
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
