import os
import traceback

import src.scraper as scraper
from utils import *

# should end with a pager in '&page=<number>' format, where <number> will be a page to start with.
# per-page=<number> seems to have no effect, so we omit it in the filter.
base_url = 'https://quizplease.ru'
filter_url = 'https://quizplease.ru/schedule-past?QpGameSearch%5BcityId%5D=17&QpGameSearch%5Bmonth%5D=0&QpGameSearch%5Btype%5D=1&QpGameSearch%5Bbars%5D=all'
last_page_to_process = 3

counter = 0

games = pd.read_csv(GAMES_CSV, encoding='UTF-8', index_col='id')
scores = pd.read_csv(SCORES_CSV, encoding='UTF-8', index_col=['game_id', 'place'])


def save_game_scores_info(game_info: GameInfo):
    current_game = {
        'id': int(game_info.id),
        'scores_available': True,
        'title': game_info.title,
        'question_set': game_info.question_set,
        'date': game_info.date,
        'location': game_info.location
    }

    if game_info.is_score_parsed():
        try:
            game_scores_df = game_info.scores[column_mapping.keys()].rename(columns=column_mapping).astype(column_types)

            game_scores_df['game_id'] = game_info.id
            game_scores_df.set_index(['game_id', 'place'], inplace=True)

            global scores
            scores = pd.concat([scores, game_scores_df])
        except:
            print(f"ERROR - Can't process %s", str(game_info))
            current_game['scores_available'] = False
            traceback.print_exc()

    games.loc[game_info.id] = current_game

    global counter

    counter += 1
    if counter % 25 == 0:
        write_to_csv()


def is_game_already_saved(id):
    return int(id) in games.index


def save_date_from_pager():
    if last_page_to_process != -1:
        last_page_number = last_page_to_process
    else:
        last_page_number = int(scraper.get_last_page_number(filter_url))

    for current_pager_url in get_pager_urls(filter_url, last_page_number):
        print(current_pager_url)
        links = scraper.scrape_game_links(current_pager_url)

        for game_relative_url in links:
            full_game_url = base_url + game_relative_url

            game_id = extract_game_id(full_game_url)

            if is_game_already_saved(game_id):
                print(f"Skipping game {game_id}, already saved")
                continue

            try:
                print(f'Getting game info: {full_game_url}')
                game_info = scraper.get_game_info(full_game_url)
                print(str(game_info))
                save_game_scores_info(game_info)
            except:
                games.loc[game_id] = {'scores_available': False}
                games.fillna('', inplace=True)
                traceback.print_exc()

    write_to_csv()

    os.remove(GAMES_CSV)
    os.rename(GAMES_CSV_BACKUP, GAMES_CSV)

    os.remove(SCORES_CSV)
    os.rename(SCORES_CSV_BACKUP, SCORES_CSV)


def write_to_csv():
    print(f"Saving to csv, games: {games.size} entries, scores: {scores.size} entries")
    games.sort_index(inplace=True)
    scores.sort_index(inplace=True)
    games.to_csv(GAMES_CSV_BACKUP)
    scores.to_csv(SCORES_CSV_BACKUP)


save_date_from_pager()
