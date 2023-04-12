import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import database_reader
import pandas as pd
from database_reader import offline_df


data = offline_df.loc[(53576,), :]
all_scores = data.loc[:, 'round_1':'round_7']

round_max_scores = [6, 6, 6, 12, 6, 6, 18]
highlighted_team_name = 'Давайте ещё немного подумаем'

num_teams = 8
bar_width = 0.8 / num_teams

# Создаем столбчатый график для вашей команды
# for i, score in enumerate(all_scores):
#     plt.bar(i + 0.1, score, width=bar_width, color='blue', alpha=0.7, label='Ваша команда' if i == 0 else None)

# Создаем столбчатый график для топ-7 команд
colors = plt.cm.get_cmap('tab10', num_teams)
for index, row in data.iterrows():
    for i, score in enumerate(row.loc['round_1':'round_7'].array, start=1):
        plt.bar(i + 0.1 + (index + 1) * bar_width, score, width=bar_width, color=colors(index + 1), alpha=0.7,
                label=f'Команда {index + 1}' if i == 0 else None)

# Добавляем подписи осей и легенду
plt.xlabel('Раунды')
plt.ylabel('Среднее количество очков')
plt.legend(loc='best')

# Задаем подписи для оси X
plt.xticks(np.arange(0.5, 7.5, step=1), np.arange(1, 8, step=1))

# Отображаем график
plt.show()