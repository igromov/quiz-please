from lxml import etree
import urllib.request

web = urllib.request.urlopen("https://quizplease.ru/game-page?id=53576")
s = web.read().decode('utf-8')

html = etree.HTML(s)

tr_nodes = html.xpath('//*[@id="resultsAnchor"]/div/div[3]/table')

header = list(map(lambda x: x.text, tr_nodes[0].xpath('thead/tr/td')))
data = [[td.text for td in tr.xpath('td')] for tr in tr_nodes[0].xpath('tr')]

print(header)
print(data)

