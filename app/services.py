from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, PlayerCareerStats
import pandas as pd
import os

# Diretório onde os CSVs serão armazenados
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Criando o diretório caso não exista

# 🔹 Obtendo ID do New Orleans Pelicans
def get_pelicans_id():
    """Retorna o ID do New Orleans Pelicans."""
    nba_teams = teams.get_teams()
    pelicans = next(team for team in nba_teams if team['full_name'] == 'New Orleans Pelicans')
    return pelicans['id']

# 🔹 Obtendo Estatísticas do Time e Salvando em CSV
def get_team_stats():
    """Obtém as estatísticas do New Orleans Pelicans e salva em CSV."""
    team_id = get_pelicans_id()
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season='2023-24')
    df = team_stats.get_data_frames()[0]

    # Selecionando colunas importantes
    selected_columns = ["GP", "W", "L", "W_PCT", "PTS", "REB", "AST", "STL", "BLK"]
    df = df[selected_columns]

    # Salvando os dados em CSV
    save_team_stats_to_csv(df.to_dict(orient='records'))

    return df.to_dict(orient='records')

# 🔹 Obtendo Estatísticas do Jogador e Salvando em CSV
def get_player_stats(name):
    """Obtém estatísticas do jogador pelo nome e salva em CSV."""
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

    # Salvando os dados em CSV
    save_player_stats_to_csv(df.to_dict(orient='records'), name)

    return df.to_dict(orient='records')

# 🔹 Funções para salvar dados em CSV
def save_team_stats_to_csv(team_stats):
    """Salva as estatísticas do time em um arquivo CSV."""
    df = pd.DataFrame(team_stats)
    file_path = os.path.join(DATA_DIR, "team_stats.csv")
    df.to_csv(file_path, index=False)
    print(f"✅ Dados do time salvos em {file_path}")

def save_player_stats_to_csv(player_stats, player_name):
    """Salva as estatísticas de um jogador em um arquivo CSV."""
    df = pd.DataFrame(player_stats)
    file_path = os.path.join(DATA_DIR, f"{player_name.replace(' ', '_')}.csv")
    df.to_csv(file_path, index=False)
    print(f"✅ Dados do jogador {player_name} salvos em {file_path}")
