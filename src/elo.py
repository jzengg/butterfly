K_VALUE = 20


def get_new_rating(opponent_rating=None, player_rating=None, player_won=None):
    scoring_point = 1 if player_won else 0
    player_win_prob = 1 / (10 ** ((opponent_rating - player_rating) / 400) + 1)
    new_rating = player_rating + (K_VALUE * (scoring_point - player_win_prob))
    return round(new_rating)
