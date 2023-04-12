import os

import pandas as pd
import src.scraper as scraper
import traceback
import re

# should end with a pager in '&page=<number>' format, where <number> will be a page to start with.
# per-page=<number> seems to have no effect, so we omit it in the filter.
base_url = 'https://quizplease.ru'
filter_url = 'https://quizplease.ru/schedule-past?QpGameSearch%5BcityId%5D=17&QpGameSearch%5Bmonth%5D=0&QpGameSearch%5Btype%5D=1&QpGameSearch%5Bbars%5D=all&page=1'
last_page_to_process = 4

counter = 0

games = pd.read_csv('data/games.csv', encoding='UTF-8', index_col='id')
scores = pd.read_csv('data/scores.csv', encoding='UTF-8', index_col=['game_id', 'place'])


def save_info(game_info):
    new_game = {
        'id': int(game_info.id),
        'scores_available': game_info.scores is not None,
        'title': game_info.title,
        'question_set': game_info.question_set,
        'date': game_info.date,
        'location': game_info.location
    }

    games.loc[new_game['id']] = new_game

    if new_game['scores_available']:

        try:
            game_scores_df = game_info.scores[
                ['Место', 'Название команды', '1 раунд', '2 раунд', '3 раунд', '4 раунд', '5 раунд', '6 раунд',
                 '7 раунд', 'итого']].rename(columns={
                'Место': 'place',
                'Название команды': 'team_name',
                '1 раунд': 'round_1',
                '2 раунд': 'round_2',
                '3 раунд': 'round_3',
                '4 раунд': 'round_4',
                '5 раунд': 'round_5',
                '6 раунд': 'round_6',
                '7 раунд': 'round_7',
                'итого': 'final_score',
            }).astype({
                'place': 'int',
                'round_1': 'float64',
                'round_2': 'float64',
                'round_3': 'float64',
                'round_4': 'float64',
                'round_5': 'float64',
                'round_6': 'float64',
                'round_7': 'float64',
                'final_score': 'float64',
            })

            game_scores_df['game_id'] = new_game['id']
            game_scores_df.set_index(['game_id', 'place'], inplace=True)

            global scores

            scores = pd.concat([scores, game_scores_df])
        except:
            print(f"ERROR - Can't process %s", str(game_info))
            traceback.print_exc()

    global counter

    counter += 1
    if counter % 25 == 0:
        write_to_csv()


def game_already_saved(id):
    return int(id) in games.index


def scrape_pages_with_results():
    page_pattern = '&page=(\\d+)'
    starting_page_number = int(re.findall(page_pattern, filter_url)[0])
    last_page_number = last_page_to_process if last_page_to_process != -1 else int(
        scraper.get_last_page_number(filter_url))
    print(f'Starting page is {starting_page_number}')
    print(f'Last page is {last_page_number}')

    for page in range(starting_page_number, last_page_number + 1):
        current_pager_url = re.sub(page_pattern, f'&page={page}', filter_url)
        print(current_pager_url)
        links = scraper.scrape_game_links(current_pager_url)

        for game_relative_url in links:
            full_game_url = base_url + game_relative_url

            game_id = re.findall('\?id=(\\d+)', game_relative_url)[0]

            if game_already_saved(game_id):
                print(f"Skipping game {game_id}, already saved")
                continue

            try:
                print(f'Getting game info: {full_game_url}')
                game_info = scraper.get_game_info(full_game_url)
                print(str(game_info))
            except:
                game_info = scraper.GameInfo()
                traceback.print_exc()

            game_info.id = game_id

            save_info(game_info)

    write_to_csv()

    os.remove('data/games.csv')
    os.rename('./games.new.csv', 'data/games.csv')

    os.remove('data/scores.csv')
    os.rename('./scores.new.csv', 'data/scores.csv')


def write_to_csv():
    print(f"Saving to csv, games: {games.size} entries, scores: {scores.size} entries")
    games.sort_index(inplace=True)
    scores.sort_index(inplace=True)
    games.to_csv('./games.new.csv')
    scores.to_csv('./scores.new.csv')


scrape_pages_with_results()
