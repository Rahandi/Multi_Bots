import requests
from bs4 import BeautifulSoup as bs

class Bioskop():
	def getallbioskop():
		for a in range(1, 23):
			namabioskop = []
			linkbisokop = []
			link = 'https://jadwalnonton.com/bioskop/?page=' + str(a)
			data = requests.get(link).text
			soup = bs(data, 'lxml')
			for b in soup.find_all('div', {'class':'bg relative'}):
				data = b.find('a', {'href':True})
				namabioskop.append(data.text.replace('\n', ''))
				linkbisokop.append(data['href'])
			return namabioskop, linkbisokop