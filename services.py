from nba_api.stats.endpoints import teamgamelog, leaguestandings
import pandas as pd
import numpy as np


def get_team_data(team_id):
    team_game_log = teamgamelog.TeamGameLog(team_id=team_id, season='2023-24')  # Temporada 2023-24
    games = team_game_log.get_data_frames()[0]
    return games

def get_nba_standings():
    """
    Obtém a classificação (RF2) e lista de times por conferência (RF1).
    """
    standings = leaguestandings.LeagueStandings(season='2024-25').get_data_frames()[0]
    standings.to_csv('standings_2024_25.csv', index=False)

    # Agrupa por conferência
    eastern = standings[standings['Conference'] == 'East']
    western = standings[standings['Conference'] == 'West']

    return eastern, western
    
