import argparse
import shutil
import traceback

import src.scraper as scraper
from src.utils import *

base_url = 'https://quizplease.ru'
single_game_url = 'https://quizplease.ru/game-page?id='

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

    write_to_csv()


def is_game_already_saved(id):
    return int(id) in games.index


def save_data_from_pager(args):
    total_page_count = int(scraper.get_last_page_number(args.filter)) if args.all else None

    for current_pager_url in get_pager_urls(args.filter, args.pages, total_page_count, args.all):
        print(current_pager_url)
        links = scraper.scrape_game_links(current_pager_url)

        for game_relative_url in links:
            full_game_url = base_url + game_relative_url

            game_id = extract_game_id(full_game_url)

            if is_game_already_saved(game_id):
                print(f"Skipping game {game_id}, already saved")
                continue

            save_game(game_id)

    write_to_csv()


def save_game(game_id):
    full_game_url = single_game_url + str(game_id)
    try:
        print(f'Getting game info: {full_game_url}')
        game_info = scraper.get_game_info(full_game_url)
        print(str(game_info))
        save_game_scores_info(game_info)
    except:
        print(f'Error getting game info: {full_game_url}')
        games.loc[game_id] = {'scores_available': False}
        games.fillna('', inplace=True)
        traceback.print_exc()


def write_to_csv():
    print(f"Saving to csv, games: {games.size} entries, scores: {scores.size} entries")
    games.sort_index(inplace=True)
    scores.sort_index(inplace=True)
    games.to_csv(GAMES_CSV)
    scores.to_csv(SCORES_CSV)


def back_up_db():
    print("Backup started...")
    shutil.copy(GAMES_CSV, GAMES_CSV_BACKUP)
    shutil.copy(SCORES_CSV, SCORES_CSV_BACKUP)
    print(f"Backup complete: {GAMES_CSV_BACKUP}, {SCORES_CSV_BACKUP}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_argument_group()

    group.add_argument('-s', '--single', type=int, default=None, help='ID of a single game to be parsed and saved')
    group.add_argument('-f', '--filter',
                       default='https://quizplease.ru/schedule-past?QpGameSearch%5BcityId%5D=17&QpGameSearch%5Bmonth%5D=0&QpGameSearch%5Btype%5D=1&QpGameSearch%5Bbars%5D=all&page=1',
                       help='Filter URL, like https://quizplease.ru/schedule-past?QpGameSearch%5BcityId%5D=17&QpGameSearch%5Bmonth%5D=0&QpGameSearch%5Btype%5D=1&QpGameSearch%5Bbars%5D=all&page=1')
    group.add_argument('-n', '--number-of-pages', dest='pages', type=int, default=3, help='Number of pages to parse')
    group.add_argument('-a', '--all', help='Parse all pages of the specified filter', action="store_true")

    args = parser.parse_args()

    print(vars(args))
    
    back_up_db()

    single_game_id = args.single
    if single_game_id is not None:
        save_game(single_game_id)
    else:
        save_data_from_pager(args)
