from utils import *

games = pd.read_csv(GAMES_CSV, encoding='UTF-8')
scores = pd.read_csv(SCORES_CSV, encoding='UTF-8')

merged_df = pd.merge(scores, games, how='inner', left_on='game_id', right_on='id')
del merged_df['id']

merged_df = merged_df.set_index(['game_id', 'place'])
merged_df = merged_df.sort_values(by=['game_id', 'place'])


def get_games(game_title=None):
    result = merged_df

    if game_title is not None:
        result = result.loc[result['game_title'] == game_title]

    return result


def filter_by_title(df, title):
    return df[df['title'] == title]


def avg_score_of_teams_played_more_than_n_games(df, n):
    # last n games (if any) with final scores
    last_n_games = df.sort_values('game_id').groupby('team_name').tail(n).sort_values('team_name').filter(
        ['team_name', 'final_score']
    )
    # drop teams that played less than n games
    only_teams_played_more_than_n_games = last_n_games.groupby('team_name').filter(lambda games: len(games) >= n)
    # avg of last n games for each team suitable team
    team_name_vs_team_last_n_avg = only_teams_played_more_than_n_games.groupby('team_name').mean()
    return team_name_vs_team_last_n_avg


offline_games_df = filter_by_title(merged_df, 'Квиз, плиз! SPB')
avg_last_5_offline = avg_score_of_teams_played_more_than_n_games(offline_games_df, 5)
avg = avg_score_of_teams_played_more_than_n_games(offline_games_df, 1)
