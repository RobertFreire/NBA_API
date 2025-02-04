from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, LeagueStandings
import pandas as pd
import os
import numpy as np
import orjson
from flask import Response

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
    """Obtém a classificação dos times por conferência."""
    from nba_api.stats.endpoints import LeagueStandings

    standings = LeagueStandings(season="2023-24").get_data_frames()[0]

    print("Colunas disponíveis:", standings.columns.tolist())  # Debugging

    # Verificando quais colunas têm relação com a classificação
    possible_rank_columns = ["PlayoffRank", "ConfRank", "WINS"]  # Alternativas possíveis

    # Encontrar a primeira coluna de ranking válida
    rank_column = next((col for col in possible_rank_columns if col in standings.columns), None)

    if not rank_column:
        return {"error": "Nenhuma coluna de ranking encontrada nos dados."}

    east_teams = standings[standings["Conference"] == "East"][
        ["TeamID", "TeamCity", "TeamName", rank_column]
    ].rename(columns={rank_column: "ConferenceRank"}).sort_values(by="ConferenceRank")

    west_teams = standings[standings["Conference"] == "West"][
        ["TeamID", "TeamCity", "TeamName", rank_column]
    ].rename(columns={rank_column: "ConferenceRank"}).sort_values(by="ConferenceRank")

    return {
        "Conferência Leste": east_teams.to_dict(orient="records"),
        "Conferência Oeste": west_teams.to_dict(orient="records")
    }


### 🔹 RF3 - ESTATÍSTICAS DO TIME (VITÓRIAS E DERROTAS) ###

def convert_numpy_types(obj):
    """Converte tipos NumPy para tipos nativos do Python antes da serialização"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    return obj

def get_team_results(team_id, season="2023-24"):
    """Obtém estatísticas detalhadas de vitórias e derrotas do time na temporada, separando casa e fora."""
    
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    
    overall_df = team_stats.get_data_frames()[0]  # Estatísticas gerais
    location_df = team_stats.get_data_frames()[1]  # Estatísticas por local

    # Get home/away stats from location_df based on TEAM_GAME_LOCATION
    home_stats = location_df[location_df['TEAM_GAME_LOCATION'] == 'Home'].iloc[0]
    away_stats = location_df[location_df['TEAM_GAME_LOCATION'] == 'Road'].iloc[0]

    response_data = {
        "team_id": int(team_id),  # Garante que team_id seja um int nativo
        "season": season,
        "results": {
            "Total de Jogos": int(overall_df["GP"].iloc[0]),
            "Total de Vitórias": int(overall_df["W"].iloc[0]),
            "Total de Derrotas": int(overall_df["L"].iloc[0]),
            "Vitórias em Casa": int(home_stats["W"]),
            "Vitórias Fora de Casa": int(away_stats["W"]),
            "Derrotas em Casa": int(home_stats["L"]),
            "Derrotas Fora de Casa": int(away_stats["L"])
        }
    }

    # 🔹 Converte qualquer dado NumPy para um tipo serializável
    response_data = convert_numpy_types(response_data)

    # 🔹 Serializa usando orjson e retorna um Response Flask com `application/json`
    return Response(orjson.dumps(response_data), mimetype="application/json")


#rf4

def get_team_general_stats(team_id, season="2023-24"):
    """Obtém estatísticas gerais do time para a temporada."""
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]  # Pegamos as estatísticas gerais (linha 0)

    selected_columns = {
        "PTS": "Total de Pontos por Jogo",
        "AST": "Total de Assistências por Jogo",
        "REB": "Total de Rebotes por Jogo",
        "FG3M": "Total de Cestas de 3 Pontos Convertidas"
    }

    # Filtrar e renomear colunas
    df = df[list(selected_columns.keys()) + ["GP"]]
    df.rename(columns=selected_columns, inplace=True)

    # Número de jogos
    total_jogos = int(df["GP"].iloc[0])

    # Obtendo estatísticas de casa e fora
    location_df = team_stats.get_data_frames()[1]
    home_stats = location_df[location_df["TEAM_GAME_LOCATION"] == "Home"].iloc[0]
    away_stats = location_df[location_df["TEAM_GAME_LOCATION"] == "Road"].iloc[0]

    response_data = {
        "team_id": int(team_id),
        "season": season,
        "stats": {
            "Total de Pontos por Jogo": round(float(df["Total de Pontos por Jogo"].iloc[0]) / total_jogos, 2),
            "Total de Assistências por Jogo": round(float(df["Total de Assistências por Jogo"].iloc[0]) / total_jogos, 2),
            "Total de Rebotes por Jogo": round(float(df["Total de Rebotes por Jogo"].iloc[0]) / total_jogos, 2),
            "Total de Cestas de 3 Pontos Convertidas": int(df["Total de Cestas de 3 Pontos Convertidas"].iloc[0]),
            "Derrotas em Casa": int(home_stats["L"]),
            "Derrotas Fora de Casa": int(away_stats["L"])
        }
    }

    # 🔹 Converte todos os valores NumPy para tipos serializáveis
    response_data = convert_numpy_types(response_data)

    return response_data

##rf5

def get_team_divided_stats(team_id, season="2023-24"):
    """Obtém a divisão de estatísticas de rebotes, pontos e arremessos do time na temporada."""
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    df = team_stats.get_data_frames()[0]  # Pegamos as estatísticas gerais (linha 0)

    selected_columns = {
        "REB": "Total de Rebotes",
        "OREB": "Total de Rebotes Ofensivos",
        "DREB": "Total de Rebotes Defensivos",
        "PTS": "Total de Pontos",
        "FGM": "Total de Cestas Convertidas",
        "FG3M": "Total de Cestas de 3 Pontos",
        "FTM": "Total de Lances Livres Convertidos"
    }

    # Filtrar e renomear colunas
    df = df[list(selected_columns.keys())]
    df.rename(columns=selected_columns, inplace=True)

    # 🔹 Calculando as cestas de 2 pontos
    total_cestas_convertidas = df["Total de Cestas Convertidas"].iloc[0]
    total_cestas_3_pontos = df["Total de Cestas de 3 Pontos"].iloc[0]
    total_cestas_2_pontos = total_cestas_convertidas - total_cestas_3_pontos  # Cestas de 2P = Total - 3P

    response_data = {
        "team_id": int(team_id),
        "season": season,
        "stats": {
            "Total de Rebotes": int(df["Total de Rebotes"].iloc[0]),
            "Total de Rebotes Ofensivos": int(df["Total de Rebotes Ofensivos"].iloc[0]),
            "Total de Rebotes Defensivos": int(df["Total de Rebotes Defensivos"].iloc[0]),
            "Total de Pontos": int(df["Total de Pontos"].iloc[0]),
            "Total de Cestas de 2 Pontos": int(total_cestas_2_pontos),
            "Total de Cestas de 3 Pontos": int(df["Total de Cestas de 3 Pontos"].iloc[0]),
            "Total de Lances Livres Convertidos": int(df["Total de Lances Livres Convertidos"].iloc[0])
        }
    }

    return response_data

