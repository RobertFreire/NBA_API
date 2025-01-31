from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, PlayerCareerStats
import pandas as pd

# Obtendo ID do New Orleans Pelicans
def get_pelicans_id():
    nba_teams = teams.get_teams()
    pelicans = next(team for team in nba_teams if team['full_name'] == 'New Orleans Pelicans')
    return pelicans['id']

def get_team_stats():
    team_id = get_pelicans_id()
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season='2023-24')
    df = team_stats.get_data_frames()[0]

    # Selecionando apenas colunas importantes
    selected_columns = ["GP", "W", "L", "W_PCT", "PTS", "REB", "AST", "STL", "BLK"]
    df = df[selected_columns]

    # Salvando em CSV
    df.to_csv('data/team_stats.csv', index=False)

    return df.to_dict(orient='records')


# Obtendo estatísticas do jogador
def get_player_stats(name):
    nba_players = players.get_players()
    player = next((p for p in nba_players if p['full_name'] == name), None)

    if not player:
        return {"error": "Player not found"}

    player_id = player['id']
    player_stats = PlayerCareerStats(player_id=player_id)
    df = player_stats.get_data_frames()[0]

    # Selecionando colunas importantes
    selected_columns = ["SEASON_ID", "TEAM_ABBREVIATION", "GP", "PTS", "REB", "AST", "FG_PCT", "FG3_PCT", "FT_PCT"]
    df = df[selected_columns]

    # Salvando CSV
    df.to_csv(f'data/{name.replace(" ", "_")}.csv', index=False)

    return df.to_dict(orient='records')

