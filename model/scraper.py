import dateparser
import urllib.request
from lxml import etree
import pandas as pd


class GameInfo:
    def __init__(self):
        self.scores = None
        self.location = None
        self.title = None
        self.date = None
        self.question_set = None

    def __str__(self):
        return f"{self.title} #{self.question_set}, {self.date}, scores_available={self.scores is not None}"


def _guess_precise_date(game_date_raw, game_dow_time_raw, game_question_set):
    date = dateparser.parse(game_date_raw, date_formats=['%d %B'])

    if not game_question_set.isdigit():
        return None

    # TODO
    return None


def _read_html(url):
    web = urllib.request.urlopen(url)
    s = web.read().decode('utf-8')
    return etree.HTML(s)


def get_game_info(url):
    html = _read_html(url)

    game_info = GameInfo()

    tr_nodes = html.xpath('//*[@id="resultsAnchor"]/div/*/table')
    if len(tr_nodes) != 0:
        header = list(map(lambda x: x.text.strip(), tr_nodes[0].xpath('thead/tr/td')))
        data = [[(td.text.strip() if td.text is not None else None) for td in tr.xpath('td')] for tr in tr_nodes[0].xpath('tr')]
        game_info.scores = pd.DataFrame(data=data, columns=header)

    game_meta_node = html.xpath('//*[@class="game-side-top wrapper-countDay"]')
    game_date_raw = game_meta_node[0].xpath('div[2]/div/div')[0].text
    game_dow_time_raw = game_meta_node[0].xpath('div[2]/div/div')[1].text

    game_location = game_meta_node[0].xpath('div[3]/div/div')[0].text
    game_title = html.xpath('//*[@class="game-heading-info"]/h1[1]')[0].text
    question_set_raw = html.xpath('//*[@class="game-heading-info"]/h1[2]')[0].text
    game_question_set = question_set_raw.replace('#', '') if question_set_raw.startswith('#') else ''

    # _guess_precise_date(game_date_raw, game_dow_time_raw, game_question_set)

    game_info.location = game_location
    game_info.title = game_title
    game_info.date = game_date_raw + '/' + game_dow_time_raw  # TODO
    game_info.question_set = game_question_set

    return game_info


def scrape_game_links(url):
    html = _read_html(url)
    links = html.xpath('//*[@id="w1"]/div[@class="schedule-column"]/div[@class="schedule-block past"]/div[1]/a/@href')
    return links


def get_last_page_number(filter_url):
    return _read_html(filter_url).xpath('//*[@id="w1"]/ul/li[last()-1]/a')[0].text
