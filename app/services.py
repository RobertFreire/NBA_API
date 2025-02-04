from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, PlayerCareerStats
import os

# Diretório base para os dados (não será usado para leitura/escrita de arquivos)
DATA_DIR = os.path.join(os.getcwd(), "data")

# 🔹 Obtendo ID do New Orleans Pelicans
def get_pelicans_id():
    """Retorna o ID do New Orleans Pelicans."""
    nba_teams = teams.get_teams()
    pelicans = next(team for team in nba_teams if team['full_name'] == 'New Orleans Pelicans')
    return pelicans['id']

# 🔹 Obtendo Estatísticas do Time para uma Temporada Específica
def get_team_stats(season="2023-24"):
    """Obtém estatísticas do New Orleans Pelicans para uma temporada específica."""
    team_id = get_pelicans_id()
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]

    return {
        "team_id": team_id,
        "team_name": "New Orleans Pelicans",
        "season": season,
        "total_victories": int(df["W"][0]),
        "home_victories": int(df["HOME_W"][0]),  
        "away_victories": int(df["ROAD_W"][0]),
        "total_losses": int(df["L"][0]),
        "home_losses": int(df["HOME_L"][0]),  
        "away_losses": int(df["ROAD_L"][0]),
        "win_percentage": float(df["W_PCT"][0]),
        "points_total": int(df["PTS"][0]),
        "points_per_game": float(df["PTS"][0] / df["GP"][0]),
        "assists_total": int(df["AST"][0]),
        "assists_per_game": float(df["AST"][0] / df["GP"][0]),
        "rebounds_total": int(df["REB"][0]),
        "rebounds_per_game": float(df["REB"][0] / df["GP"][0]),
        "steals": int(df["STL"][0]),
        "blocks": int(df["BLK"][0]),
        "three_pointers_made": int(df["FG3M"][0]),
        "two_pointers_made": int(df["FG2M"][0]),
        "free_throws_made": int(df["FTM"][0]),
        "offensive_rebounds": int(df["OREB"][0]),
        "defensive_rebounds": int(df["DREB"][0]),
        "free_throw_percentage": float(df["FT_PCT"][0])
    }

# 🔹 Obtendo Estatísticas do Time para as Duas Temporadas (RF1.1)
def get_team_stats_both_seasons():
    """Retorna estatísticas do New Orleans Pelicans para as temporadas `23-24` e `24-25`."""
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

    return {
        "player_id": player_id,
        "stats": [
            {
                "season": row["SEASON_ID"],
                "team": row["TEAM_ABBREVIATION"],
                "games_played": int(row["GP"]),
                "total_points": int(row["PTS"]),
                "points_per_game": float(row["PTS"] / row["GP"]),
                "total_assists": int(row["AST"]),
                "assists_per_game": float(row["AST"] / row["GP"]),
                "total_rebounds": int(row["REB"]),
                "rebounds_per_game": float(row["REB"] / row["GP"]),
                "field_goal_percentage": float(row["FG_PCT"]),
                "three_point_percentage": float(row["FG3_PCT"]),
                "free_throw_percentage": float(row["FT_PCT"]),
            }
            for _, row in df.iterrows()
        ]
    }
