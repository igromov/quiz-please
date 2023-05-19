import re

import pandas as pd

column_mapping = {
    'Место': 'place',
    'Название команды': 'team_name',
    '1 раунд': 'round_1',
    '2 раунд': 'round_2',
    '3 раунд': 'round_3',
    '4 раунд': 'round_4',
    '5 раунд': 'round_5',
    '6 раунд': 'round_6',
    '7 раунд': 'round_7',
    'итого': 'final_score'
}

column_types = {
    'place': 'int',
    'round_1': 'float64',
    'round_2': 'float64',
    'round_3': 'float64',
    'round_4': 'float64',
    'round_5': 'float64',
    'round_6': 'float64',
    'round_7': 'float64',
    'final_score': 'float64'
}

SCORES_CSV_BACKUP = '../data/scores.backup.csv'
SCORES_CSV = '../data/scores.csv'
GAMES_CSV_BACKUP = '../data/games.backup.csv'
GAMES_CSV = '../data/games.csv'


class GameInfo:
    def __init__(self,
                 id: int,
                 scores: pd.DataFrame,
                 location: str,
                 title: str,
                 date: str,
                 question_set: str):
        if not isinstance(id, int):
            raise TypeError("id must be an integer")
        self.id = id
        self.scores = scores
        self.location = location
        self.title = title
        self.date = date
        self.question_set = question_set

    def __str__(self):
        return f"{self.title} #{self.question_set}, {self.date}, scores_available={self.is_score_parsed()}"

    def is_score_parsed(self):
        return self.scores is not None


def extract_game_id(url: str):
    return int(re.findall('\\?id=(\\d+)', url)[0])


def get_pager_urls(starting_filter_url, pages_to_parse, total_page_count, parse_all_pages):
    page_pattern = '&page=(\\d+)'

    if len((s := re.findall(page_pattern, starting_filter_url))) > 0:
        starting_page = int(s[0])
    else:
        starting_page = 1

    if parse_all_pages:
        last_page = total_page_count
    else:
        last_page = starting_page + pages_to_parse

    print(f'Pager: start: {starting_page}, end: {last_page}')

    return [re.sub(page_pattern, f'&page={page}', starting_filter_url) for page in range(starting_page, last_page + 1)]


rarity_heat_map = {
    'legendary': ('#ff222b', "Legendary team"),
    'epic': ('#ff9e0f', "Epic team"),
    'rare': ('#55c8ff', "Rare team"),
    'uncommon': ('#72e240', "Uncommon team"),
    'common': ('#bebebe', "Common team")
}


# https://cdnb.artstation.com/p/assets/images/images/055/842/959/large/jean-go-skinrarity-colorcode.jpg?1667878604
def color_by_rarity(avg_df, team_name):
    if team_name not in avg_df.index:
        return None, '#bebebe'

    avg = avg_df.at[team_name, 'final_score']

    rarity = 'common'

    if avg >= 42:
        rarity = 'legendary'
    elif 37 <= avg < 42:
        rarity = 'epic'
    elif 35 <= avg < 37:
        rarity = 'rare'
    elif 33 <= avg < 35:
        rarity = 'uncommon'

    color_hex, display_name = rarity_heat_map[rarity]

    return avg, color_hex
