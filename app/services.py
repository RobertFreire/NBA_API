from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits
import pandas as pd
import os

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Criar o diretório caso não exista

def get_pelicans_id():
    """Retorna o ID do New Orleans Pelicans."""
    nba_teams = teams.get_teams()
    pelicans = next(team for team in nba_teams if team['full_name'] == 'New Orleans Pelicans')
    return pelicans['id']

def get_team_stats(season="2023-24"):
    """Obtém estatísticas do New Orleans Pelicans para uma temporada específica."""
    team_id = get_pelicans_id()
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]

    selected_columns = {
        "GP": "Jogos",
        "W": "Vitórias",
        "L": "Derrotas",
        "W_PCT": "Porcentagem de Vitórias",
        "PTS": "Pontos Totais",
        "REB": "Rebotes",
        "AST": "Assistências",
        "STL": "Roubos de Bola",
        "BLK": "Tocos"
    }
    
    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    return {
        "team_id": team_id,
        "team_name": "New Orleans Pelicans",
        "season": season,
        "stats": df.to_dict(orient="records")
    }

def get_team_stats_both_seasons():
    """Retorna estatísticas do New Orleans Pelicans para as temporadas `23-24` e `24-25`."""
    return {
        "2023-24": get_team_stats("2023-24"),
        "2024-25": get_team_stats("2024-25")
    }
