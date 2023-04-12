import urllib.request

from lxml import etree

from utils import *


def _read_html(url):
    web = urllib.request.urlopen(url)
    s = web.read().decode('utf-8')
    return etree.HTML(s)


def get_game_info(url):
    html = _read_html(url)

    scores = None

    tr_nodes = html.xpath('//*[@id="resultsAnchor"]/div/*/table')
    if len(tr_nodes) != 0:
        header = list(map(lambda x: x.text.strip(), tr_nodes[0].xpath('thead/tr/td')))
        trs = tr_nodes[0].xpath('tr')
        data = [[(td.text.strip() if td.text is not None else None) for td in tr.xpath('td')] for tr in trs]
        scores = pd.DataFrame(data=data, columns=header)

    game_meta_node = html.xpath('//*[@class="game-side-top wrapper-countDay"]')
    game_date_raw = game_meta_node[0].xpath('div[2]/div/div')[0].text
    game_dow_time_raw = game_meta_node[0].xpath('div[2]/div/div')[1].text

    location = game_meta_node[0].xpath('div[3]/div/div')[0].text
    title = html.xpath('//*[@class="game-heading-info"]/h1[1]')[0].text
    question_set_raw = html.xpath('//*[@class="game-heading-info"]/h1[2]')[0].text
    question_set = question_set_raw.replace('#', '') if question_set_raw.startswith('#') else ''
    date = game_date_raw + '/' + game_dow_time_raw  # TODO

    return GameInfo(extract_game_id(url), scores, location, title, date, question_set)


def scrape_game_links(url):
    html = _read_html(url)
    links = html.xpath('//*[@id="w1"]/div[@class="schedule-column"]/div[@class="schedule-block past"]/div[1]/a/@href')
    return links


def get_last_page_number(filter_url):
    return _read_html(filter_url).xpath('//*[@id="w1"]/ul/li[last()-1]/a')[0].text
