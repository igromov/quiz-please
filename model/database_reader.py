import pandas as pd


games = pd.read_csv('../games.csv', encoding='UTF-8')
scores = pd.read_csv('../scores.csv', encoding='UTF-8')

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
    last_n_games = df.sort_values('game_id').groupby('team_name').tail(n).sort_values('team_name').filter(['team_name', 'final_score'])
    # drop teams that played less than n games
    only_teams_played_more_than_n_games = last_n_games.groupby('team_name').filter(lambda games: len(games) >= n)
    # avg of last n games for each team suitable team
    team_name_vs_team_last_n_avg = only_teams_played_more_than_n_games.groupby('team_name').mean()
    return team_name_vs_team_last_n_avg


offline_df = filter_by_title(merged_df, 'Квиз, плиз! SPB')
avg_last_5_offline = avg_score_of_teams_played_more_than_n_games(offline_df, 5)


# https://cdnb.artstation.com/p/assets/images/images/055/842/959/large/jean-go-skinrarity-colorcode.jpg?1667878604
# TODO rework
def color_by_rarity(team_name):
    if team_name not in avg_last_5_offline.index:
        return None, '#bebebe'

    avg = avg_last_5_offline.at[team_name, 'final_score']

    if avg >= 42:
        return avg, '#ff222b'  # legendary
    elif 37 <= avg < 42:
        return avg, '#ff9e0f'  # epic
    elif 35 <= avg < 37:
        return avg, '#55c8ff'  # rare
    elif 33 <= avg < 35:
        return avg, '#72e240'  # uncommon
    elif avg < 33:
        return avg, '#bebebe'  # common





# def get_top_avg_scores_
# df_filtered.sort_values('game_id').groupby('team_name').tail(5).groupby('team_name')['final_score'].mean().round(2)
# print(scores.head())
# print(merged_df.head(n = 50).to_csv())

offline_df = filter_by_title(merged_df, 'Квиз, плиз! SPB')
avg = avg_score_of_teams_played_more_than_n_games(offline_df, 5)
# print(avg.head(100))
# final_score_t2_g2 = merged_df.loc[(53576, 'Давайте ещё немного подумаем'), 'final_score'].item()
# print(final_score_t2_g2)

# def get_

