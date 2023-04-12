import pandas as pd

games = pd.read_csv('../games.csv', encoding='UTF-8', index_col=['id'])
scores = pd.read_csv('../scores.csv', encoding='UTF-8', index_col=['game_id', 'place'])

games.sort_index(ascending=True, inplace=True)
scores.sort_index(ascending=True, inplace=True)

games.to_csv('../games.new.csv', index=True)
scores.to_csv('../scores.new.csv', index=True)
