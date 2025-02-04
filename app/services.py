from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, PlayerCareerStats
import pandas as pd
import os

# Diretório onde os CSVs serão armazenados (se precisar salvar no futuro)
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 🔹 Obtendo ID do New Orleans Pelicans
def get_pelicans_id():
    """Retorna o ID do New Orleans Pelicans."""
    nba_teams = teams.get_teams()
    pelicans = next(team for team in nba_teams if team['full_name'] == 'New Orleans Pelicans')
    return pelicans['id']

# 🔹 Obtendo Estatísticas do Time
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
        "OREB": "Rebotes Ofensivos",
        "DREB": "Rebotes Defensivos",
        "AST": "Assistências",
        "STL": "Roubos de Bola",
        "BLK": "Tocos",
        "FGM": "Cestas Convertidas",
        "FG3M": "Cestas de 3 Pontos",
        "FTM": "Lances Livres Convertidos",
        "HOME_W": "Vitórias em Casa",
        "ROAD_W": "Vitórias Fora de Casa",
        "HOME_L": "Derrotas em Casa",
        "ROAD_L": "Derrotas Fora de Casa"
    }

    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    return {
        "team_id": team_id,
        "team_name": "New Orleans Pelicans",
        "season": season,
        "stats": df.to_dict(orient="records")
    }

# 🔹 Obtendo Estatísticas para Ambas as Temporadas
def get_team_stats_both_seasons():
    """Retorna estatísticas do New Orleans Pelicans para `23-24` e `24-25`."""
    return {
        "2023-24": get_team_stats("2023-24"),
        "2024-25": get_team_stats("2024-25")
    }

# 🔹 Obtendo ID de um Jogador pelo Nome
def get_player_id(player_name):
    """Retorna o ID do jogador da NBA pelo nome."""
    nba_players = players.get_players()
    player = next((p for p in nba_players if p['full_name'] == player_name), None)

    if not player:
        return None  # Retorna None se o jogador não for encontrado

    return player['id']

# 🔹 Obtendo Estatísticas do Jogador
def get_player_stats(player_id):
    """Obtém estatísticas de um jogador da NBA pelo ID."""
    player_stats = PlayerCareerStats(player_id=player_id)
    df = player_stats.get_data_frames()[0]

    selected_columns = {
        "SEASON_ID": "Temporada",
        "TEAM_ABBREVIATION": "Time",
        "GP": "Jogos",
        "PTS": "Pontos por Temporada",
        "REB": "Rebotes",
        "AST": "Assistências",
        "FG_PCT": "Aproveitamento de Arremessos",
        "FG3_PCT": "Aproveitamento de 3 Pontos",
        "FT_PCT": "Aproveitamento de Lances Livres"
    }

    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    return {
        "player_id": player_id,
        "stats": df.to_dict(orient="records")
    }
