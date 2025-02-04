from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, LeagueStandings
import pandas as pd
import os

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Criar o diretório caso não exista

### 🔹 RF1 - LISTA DE TIMES POR CONFERÊNCIA ###
def get_teams_by_conference():
    """Lista os times da NBA agrupados por Conferência Leste e Oeste."""
    nba_teams = teams.get_teams()

    # Dicionário com a divisão correta das conferências
    eastern_conference = [
        "Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers", "Toronto Raptors",
        "Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons", "Indiana Pacers", "Milwaukee Bucks",
        "Atlanta Hawks", "Charlotte Hornets", "Miami Heat", "Orlando Magic", "Washington Wizards"
    ]
    
    western_conference = [
        "Denver Nuggets", "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers", "Utah Jazz",
        "Golden State Warriors", "Los Angeles Clippers", "Los Angeles Lakers", "Phoenix Suns", "Sacramento Kings",
        "Dallas Mavericks", "Houston Rockets", "Memphis Grizzlies", "New Orleans Pelicans", "San Antonio Spurs"
    ]

    east_teams = []
    west_teams = []

    for team in nba_teams:
        team_info = {"id": team["id"], "name": team["full_name"]}

        if team["full_name"] in eastern_conference:
            east_teams.append(team_info)
        elif team["full_name"] in western_conference:
            west_teams.append(team_info)

    return {
        "Conferência Leste": east_teams,
        "Conferência Oeste": west_teams
    }

### 🔹 RF2 - CLASSIFICAÇÃO ATUAL DOS TIMES ###
def get_team_rankings():
    """Obtém a classificação atual dos times da NBA agrupados por conferência."""
    standings = LeagueStandings().get_data_frames()[0]

    east_teams = standings[standings["Conference"] == "East"][["TeamID", "TeamCity", "TeamName", "ConferenceRank"]]
    west_teams = standings[standings["Conference"] == "West"][["TeamID", "TeamCity", "TeamName", "ConferenceRank"]]

    rankings = {
        "Conferência Leste": east_teams.to_dict(orient="records"),
        "Conferência Oeste": west_teams.to_dict(orient="records"),
    }

    return rankings

### 🔹 RF3 - ESTATÍSTICAS DO TIME (VITÓRIAS E DERROTAS) ###
def get_team_results(team_id, season="2023-24"):
    """Obtém estatísticas detalhadas do time na temporada, separando vitórias e derrotas por casa e fora."""
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[1]  # Índice 1 contém estatísticas de casa e fora
    
    selected_columns = {
        "W": "Total de Vitórias",
        "W_HOME": "Total de Vitórias em Casa",
        "W_ROAD": "Total de Vitórias Fora de Casa",
        "L": "Total de Derrotas",
        "L_HOME": "Total de Derrotas em Casa",
        "L_ROAD": "Total de Derrotas Fora de Casa"
    }

    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    return {
        "team_id": team_id,
        "season": season,
        "stats": df.to_dict(orient="records")
    }

### 🔹 RF4, RF5, RF6 - ESTATÍSTICAS GERAIS E DEFENSIVAS ###
def get_team_advanced_stats(team_id, season="2023-24"):
    """Obtém estatísticas avançadas do time para a temporada."""
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]  # Índice 0 contém estatísticas gerais

    selected_columns = {
        "PTS": "Total de Pontos por Jogo",
        "AST": "Total de Assistências por Jogo",
        "REB": "Total de Rebotes por Jogo",
        "FG3M": "Total de Cestas de 3 Pontos Convertidas",
        "REB_O": "Total de Rebotes Ofensivos",
        "REB_D": "Total de Rebotes Defensivos",
        "BLK": "Total de Tocos por Jogo",
        "TOV": "Total de Erros por Jogo",
        "PF": "Total de Faltas por Jogo"
    }

    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    return {
        "team_id": team_id,
        "season": season,
        "stats": df.to_dict(orient="records")
    }
