from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, BoxScoreTraditionalV2, CommonTeamRoster, CommonPlayerInfo, PlayerGameLog
from nba_api.stats.endpoints import TeamGameLog, TeamGameLogs, TeamDetails, PlayerCareerStats, PlayerGameLog
from requests.exceptions import ReadTimeout
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import numpy as np
import json
from scipy import stats
from requests.exceptions import ReadTimeout
from functools import lru_cache
import time

DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)  # Criar o diretório caso não exista

def save_to_csv(data, filename):
    """Salva um dicionário ou lista de dicionários em CSV."""
    file_path = os.path.join(DATA_DIR, f"{filename}.csv")
    
    # Se os dados forem uma lista de dicionários
    if isinstance(data, list):
        df = pd.DataFrame(data)
    # Se os dados forem um único dicionário, colocamos em uma lista
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        print(f"Erro ao salvar {filename}: formato inválido")
        return
    
    df.to_csv(file_path, index=False)
    print(f"✅ Dados salvos em {file_path}")

def save_team_stats_to_csv(team_id):
    """Obtém e salva as estatísticas do time em CSV."""
    stats = get_team_general_stats(team_id)
    save_to_csv(stats, f"team_stats_{team_id}")

def save_team_games_to_csv(team_id):
    """Obtém e salva a lista de jogos do time em CSV."""
    games = get_team_games(team_id)["games"]
    save_to_csv(games, f"team_games_{team_id}")

def save_defensive_stats_to_csv(team_id):
    """Obtém e salva as estatísticas defensivas do time em CSV."""
    stats = get_team_defensive_stats(team_id)
    save_to_csv(stats, f"team_defensive_stats_{team_id}")

def save_offensive_stats_to_csv(team_id):
    """Obtém e salva as estatísticas ofensivas do time em CSV."""
    stats = get_team_divided_stats(team_id)
    save_to_csv(stats, f"team_offensive_stats_{team_id}")

def save_graph_data_to_csv(team_id):
    """Obtém e salva os dados dos gráficos do time em CSV."""
    graphs = {
        "bar_win_loss": get_bar_chart_win_loss(team_id),
        "bar_home_away": get_bar_chart_home_away(team_id),
        "histogram_win_loss": get_histogram_win_loss(team_id),
        "pie_win_loss": get_pie_chart_win_loss(team_id),
        "radar_points": get_radar_chart_points(team_id),
        "line_win_streak": get_line_chart_win_streak(team_id),
        "scatter_points": get_scatter_chart_points(team_id),
    }
    
    for key, data in graphs.items():
        save_to_csv(data, f"graph_{key}_{team_id}")


def get_team_basic_info(team_id):
    """Retorna informações básicas do time, como nome, cidade, conferência, etc."""
    team_info = teams.find_team_name_by_id(team_id)
    return {
        "team_id": team_info["id"],
        "full_name": team_info["full_name"],
        "abbreviation": team_info["abbreviation"],
        "nickname": team_info["nickname"],
        "city": team_info["city"],
        "state": team_info["state"],
        "year_founded": team_info["year_founded"],
    }

@lru_cache(maxsize=32)
def get_team_stats_both_seasons(team_id):
    """Obtém estatísticas do time para as temporadas 23-24 e a atual (24-25)."""
    seasons = ["2023-24", "2024-25"]
    return {
        season: {
            "stats": get_team_general_stats(team_id, season),
            "games": get_team_games(team_id, season),
            "defensive": get_team_defensive_stats(team_id, season),
            "offensive": get_team_divided_stats(team_id, season),
            "graphs": {
                "bar_win_loss": get_bar_chart_win_loss(team_id, season),
                "pie_win_loss": get_pie_chart_win_loss(team_id, season),
                "radar_points": get_radar_chart_points(team_id, season),
                "line_win_streak": get_line_chart_win_streak(team_id, season),
                "scatter_points": get_scatter_chart_points(team_id, season),
            }
        }
        for season in seasons
    }


### 🔹 RF1 - LISTA DE TIMES POR CONFERÊNCIA ###
@lru_cache(maxsize=32)
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
        "Conferencia Leste": east_teams,
        "Conferencia Oeste": west_teams
    }

### 🔹 RF2 - CLASSIFICAÇÃO ATUAL DOS TIMES ###
@lru_cache(maxsize=32)
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
        "Conferencia Leste": east_teams.to_dict(orient="records"),
        "Conferencia Oeste": west_teams.to_dict(orient="records")
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

@lru_cache(maxsize=32)
def get_team_results_both_seasons(team_id):
    """Obtém estatísticas detalhadas de vitórias e derrotas do time para as temporadas 23-24 e 24-25."""
    
    seasons = ["2023-24", "2024-25"]
    results = {}

    for season in seasons:
        team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
        overall_df = team_stats.get_data_frames()[0]  # Estatísticas gerais
        location_df = team_stats.get_data_frames()[1]  # Estatísticas por local

        # Obtendo estatísticas separadas para jogos em casa e fora
        home_stats = location_df[location_df['TEAM_GAME_LOCATION'] == 'Home'].iloc[0]
        away_stats = location_df[location_df['TEAM_GAME_LOCATION'] == 'Road'].iloc[0]

        results[season] = {
            "Total de Jogos": int(overall_df["GP"].iloc[0]),
            "Total de Vitorias": int(overall_df["W"].iloc[0]),
            "Total de Derrotas": int(overall_df["L"].iloc[0]),
            "Vitorias em Casa": int(home_stats["W"]),
            "Vitorias Fora de Casa": int(away_stats["W"]),
            "Derrotas em Casa": int(home_stats["L"]),
            "Derrotas Fora de Casa": int(away_stats["L"])
        }

    return {
        "team_id": int(team_id),
        "results": results
    }



#rf4
@lru_cache(maxsize=32)
def get_team_general_stats(team_id):
    """Obtém estatísticas gerais do time para as temporadas especificadas."""
    all_seasons_stats = {}
    seasons=["2023-24", "2024-25"]

    for season in seasons:
        team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
        data_frames = team_stats.get_data_frames()
        
        # Imprimir os dados para verificar a resposta
        print(f"Resposta da API para a temporada {season}:", data_frames)

        # Certificar-se de que 'resultSet' ou o esperado está presente
        if len(data_frames) == 0:
            all_seasons_stats[season] = {"error": "Nenhum dado encontrado para o time."}
            continue
        
        # Continuar com a lógica original se a resposta estiver correta
        df = data_frames[0]
        selected_columns = {
            "PTS": "Total de Pontos por Jogo",
            "AST": "Total de Assistencias por Jogo",
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
                "Total de Assistencias por Jogo": round(float(df["Total de Assistencias por Jogo"].iloc[0]) / total_jogos, 2),
                "Total de Rebotes por Jogo": round(float(df["Total de Rebotes por Jogo"].iloc[0]) / total_jogos, 2),
                "Total de Cestas de 3 Pontos Convertidas": int(df["Total de Cestas de 3 Pontos Convertidas"].iloc[0]),
                "Derrotas em Casa": int(home_stats["L"]),
                "Derrotas Fora de Casa": int(away_stats["L"])
            }
        }

        # Converte todos os valores NumPy para tipos serializáveis
        response_data = convert_numpy_types(response_data)
        all_seasons_stats[season] = response_data

    return all_seasons_stats



##rf5
@lru_cache(maxsize=32)
def get_team_divided_stats(team_id):
    """Obtém a divisão de estatísticas de rebotes, pontos e arremessos do time para as temporadas 2023-24 e 2024-25."""
    seasons = ["2023-24", "2024-25"]
    stats = {}

    for season in seasons:
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

        df = df[list(selected_columns.keys())]
        df.rename(columns=selected_columns, inplace=True)

        # Calculando as cestas de 2 pontos
        total_cestas_convertidas = df["Total de Cestas Convertidas"].iloc[0]
        total_cestas_3_pontos = df["Total de Cestas de 3 Pontos"].iloc[0]
        total_cestas_2_pontos = total_cestas_convertidas - total_cestas_3_pontos  # Cestas de 2P = Total - 3P

        stats[season] = {
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

    return stats


## rf6
@lru_cache(maxsize=32)
def get_team_defensive_stats(team_id):
    """Obtém estatísticas defensivas do time para as temporadas 2023-24 e 2024-25."""
    seasons = ["2023-24", "2024-25"]
    stats = {}
    
    for season in seasons:
        team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
        df = team_stats.get_data_frames()[0]  # Pegamos as estatísticas gerais (linha 0)

        selected_columns = {
            "STL": "Total de Roubos de Bola",
            "DREB": "Total de Rebotes Defensivos",
            "BLK": "Total de Tocos por Jogo",
            "TOV": "Total de Erros por Jogo",
            "PF": "Total de Faltas por Jogo"
        }

        # Filtrar e renomear colunas
        df = df[list(selected_columns.keys())]
        df.rename(columns=selected_columns, inplace=True)

        stats[season] = {
            "team_id": int(team_id),
            "season": season,
            "stats": {
                "Total de Roubos de Bola": int(df["Total de Roubos de Bola"].iloc[0]),
                "Total de Rebotes Defensivos": int(df["Total de Rebotes Defensivos"].iloc[0]),
                "Total de Tocos por Jogo": int(df["Total de Tocos por Jogo"].iloc[0]),
                "Total de Erros por Jogo": int(df["Total de Erros por Jogo"].iloc[0]),
                "Total de Faltas por Jogo": int(df["Total de Faltas por Jogo"].iloc[0])
            }
        }

    return stats


## rf7
@lru_cache(maxsize=32)
def get_team_games(team_id, season=None, retries=3, timeout=60):
    """Obtém a lista de jogos do time para as temporadas 2023-24 e 2024-25."""
    seasons = ["2023-24", "2024-25"]
    games = {}
    
    for season in seasons:
        for attempt in range(retries):
            try:
                team_games = TeamGameLogs(team_id_nullable=team_id, season_nullable=season, timeout=timeout)
                df = team_games.get_data_frames()[0]  # Pegamos os dados de jogos
                break
            except ReadTimeout:
                if attempt < retries - 1:
                    continue
                else:
                    raise

        selected_columns = {
            "GAME_DATE": "Data do Jogo",
            "MATCHUP": "Adversario",
            "WL": "Vitoria ou Derrota",
            "PTS": "Pontos do Time",
            "GAME_ID": "Game_ID",
            "TEAM_ID": "Team_ID",
            "PLUS_MINUS": "Saldo de Pontos"
        }

        # Se a coluna PLUS_MINUS existir, adicionamos ela
        if "PLUS_MINUS" in df.columns:
            selected_columns["PLUS_MINUS"] = "Saldo de Pontos"

        # Filtramos apenas as colunas existentes
        existing_columns = [col for col in selected_columns.keys() if col in df.columns]
        df = df[existing_columns].rename(columns={col: selected_columns[col] for col in existing_columns})

        if "Saldo de Pontos" in df.columns:
            df["Pontos do Adversario"] = df["Pontos do Time"] - df["Saldo de Pontos"]
        else:
            df["Pontos do Adversario"] = None 

        # Transformar a coluna "Adversário" para indicar se o jogo foi em casa ou fora
        df["Casa ou Fora"] = df["Adversario"].apply(lambda x: "Casa" if "vs." in x else "Fora")
        df["Adversario"] = df["Adversario"].apply(lambda x: x.split()[-1])

        # Armazenar os jogos de cada temporada
        games[season] = {
            "team_id": int(team_id),
            "season": season,
            "games": df.to_dict(orient="records")
        }

    return games



## rf8
@lru_cache(maxsize=32)
def get_bar_chart_win_loss(team_id):
    """Gera os dados para um gráfico de barras empilhado de vitórias e derrotas."""
    results = get_team_results_both_seasons(team_id)["results"]

    data = {
        "type": "bar",
        "seasons": {}
    }

    for season, stats in results.items():
        data["seasons"][season] = {
            "labels": [f"Vitorias {season}", f"Derrotas {season}"],
            "values": [stats.get("Total de Vitorias", 0), stats.get("Total de Derrotas", 0)],
            "colors": ["green", "red"]
        }

    return data

@lru_cache(maxsize=32)
def get_bar_chart_home_away(team_id):
    """Gera os dados para um gráfico de barras agrupado de vitórias e derrotas em casa e fora."""
    results = get_team_results_both_seasons(team_id)["results"]

    data = {
        "type": "bar",
        "seasons": {}
    }

    for season, stats in results.items():
        total_vitorias_casa = stats.get("Vitorias em Casa", 0)
        total_vitorias_fora = stats.get("Vitorias Fora de Casa", 0)
        total_derrotas_casa = stats.get("Derrotas em Casa", 0)
        total_derrotas_fora = stats.get("Derrotas Fora de Casa", 0)

        data["seasons"][season] = {
            "labels": ["Vitórias em Casa", "Vitórias Fora de Casa", "Derrotas em Casa", "Derrotas Fora de Casa"],
            "values": [
                total_vitorias_casa, total_vitorias_fora,
                total_derrotas_casa, total_derrotas_fora
            ],
            "colors": ["green", "blue", "red", "brown"]
        }

    return data

@lru_cache(maxsize=32)
def get_histogram_win_loss(team_id):
    """Gera os dados para um histograma de vitórias e derrotas para todas as temporadas disponíveis."""
    results = get_team_games(team_id)

    data = {
        "type": "histogram",
        "seasons": {}
    }

    for season, season_data in results.items():
        games = season_data["games"]
        game_dates = []
        game_results = []

        for game in games:
            game_dates.append(game["Data do Jogo"])
            game_results.append(1 if game["Vitoria ou Derrota"] == "W" else 0)

        data["seasons"][season] = {
            "dates": game_dates,
            "results": game_results,
            "colors": ["green", "red"]
        }

    return data

@lru_cache(maxsize=32)
def get_pie_chart_win_loss(team_id):
    """Gera os dados para um gráfico de pizza de percentual de vitórias e derrotas em casa e fora para todas as temporadas disponíveis."""
    results = get_team_results_both_seasons(team_id)["results"]

    data = {
        "type": "pie",
        "seasons": {}
    }

    for season, stats in results.items():
        total_jogos = stats.get("Total de Vitorias", 0) + stats.get("Total de Derrotas", 0)
        if total_jogos == 0:
            continue

        total_vitorias_casa = stats.get("Vitorias em Casa", 0)
        total_vitorias_fora = stats.get("Vitorias Fora de Casa", 0)
        total_derrotas_casa = stats.get("Derrotas em Casa", 0)
        total_derrotas_fora = stats.get("Derrotas Fora de Casa", 0)

        data["seasons"][season] = {
            "labels": ["Vitórias em Casa", "Vitórias Fora de Casa", "Derrotas em Casa", "Derrotas Fora de Casa"],
            "values": [
                round(total_vitorias_casa / total_jogos * 100, 2),
                round(total_vitorias_fora / total_jogos * 100, 2),
                round(total_derrotas_casa / total_jogos * 100, 2),
                round(total_derrotas_fora / total_jogos * 100, 2)
            ],
            "colors": ["green", "blue", "red", "orange"]
        }

    return data

@lru_cache(maxsize=32)
def get_radar_chart_points(team_id):
    """Gera os dados para um gráfico de radar mostrando a média de pontos marcados e sofridos em casa e fora para todas as temporadas disponíveis."""
    results = get_team_games(team_id)

    data = {
        "type": "radar",
        "seasons": {}
    }

    for season, season_data in results.items():
        games = season_data["games"]
        pontos_marcados_casa = []
        pontos_marcados_fora = []
        pontos_sofridos_casa = []
        pontos_sofridos_fora = []

        for game in games:
            if game["Casa ou Fora"] == "Casa":
                pontos_marcados_casa.append(game["Pontos do Time"])
                pontos_sofridos_casa.append(game["Pontos do Adversario"])
            else:
                pontos_marcados_fora.append(game["Pontos do Time"])
                pontos_sofridos_fora.append(game["Pontos do Adversario"])

        media_pontos_marcados_casa = sum(pontos_marcados_casa) / len(pontos_marcados_casa) if pontos_marcados_casa else 0
        media_pontos_marcados_fora = sum(pontos_marcados_fora) / len(pontos_marcados_fora) if pontos_marcados_fora else 0
        media_pontos_sofridos_casa = sum(pontos_sofridos_casa) / len(pontos_sofridos_casa) if pontos_sofridos_casa else 0
        media_pontos_sofridos_fora = sum(pontos_sofridos_fora) / len(pontos_sofridos_fora) if pontos_sofridos_fora else 0

        data["seasons"][season] = {
            "labels": ["Pontos Marcados em Casa", "Pontos Marcados Fora", "Pontos Sofridos em Casa", "Pontos Sofridos Fora"],
            "values": [
                round(media_pontos_marcados_casa, 2),
                round(media_pontos_marcados_fora, 2),
                round(media_pontos_sofridos_casa, 2),
                round(media_pontos_sofridos_fora, 2)
            ],
            "colors": ["blue", "green", "red", "orange"]
        }

    return data

@lru_cache(maxsize=32)
def get_line_chart_win_streak(team_id):
    """Gera os dados para um gráfico de linhas mostrando a sequência de vitórias e derrotas ao longo da temporada."""
    results = get_team_games(team_id)

    data = {
        "type": "line",
        "seasons": {}
    }

    for season, season_data in results.items():
        games = season_data["games"]
        
        data["seasons"][season] = {
            "labels": [game["Data do Jogo"] for game in games],
            "values": [1 if game["Vitoria ou Derrota"] == "W" else 0 for game in games],
            "colors": ["blue"]
        }

    return data


def get_scatter_chart_points(team_id):
    """Gera os dados para um gráfico de dispersão mostrando a média de pontos marcados e sofridos por jogo."""
    results = get_team_games(team_id)

    data = {
        "type": "scatter",
        "seasons": {}
    }

    for season, season_data in results.items():
        games = season_data["games"]
        
        data["seasons"][season] = {
            "labels": [game["Adversario"] for game in games],
            "values": [game["Pontos do Time"] for game in games],
            "colors": ["orange"]
        }

    return data


##JOGADORES
@lru_cache(maxsize=32)
def fetch_age_and_salary(player_name, team_abbreviation, team_name_formatted):
    url = f"https://www.espn.com/nba/team/roster/_/name/{team_abbreviation}/{team_name_formatted}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    rows = soup.find_all('tr', class_='Table__TR')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0 and player_name in cols[1].text:
            age = cols[3].text.strip()
            salary = cols[7].text.strip()
            return age, salary

    return None, None


@lru_cache(maxsize=32)
def get_player_info(player_id):
    """Retorna informações básicas do jogador, como nome, altura, peso, idade, experiência, posição, universidade e salário."""
    player_info = CommonPlayerInfo(player_id=player_id).get_data_frames()[0]
    player_data = player_info.iloc[0]

    team_id = player_data["TEAM_ID"]
    team_info = teams.find_team_name_by_id(team_id)
    team_name = team_info["full_name"]
    team_abbreviation = team_info["abbreviation"].lower()
    team_name_formatted = team_name.replace(' ', '-').lower()

    age, salary = fetch_age_and_salary(player_data["DISPLAY_FIRST_LAST"], team_abbreviation, team_name_formatted)

    player_data = {
        "id": player_data["PERSON_ID"],
        "name": player_data["DISPLAY_FIRST_LAST"],
        "height": player_data["HEIGHT"],
        "weight": player_data["WEIGHT"],
        "age": age,
        "experience": player_data["SEASON_EXP"] if player_data["SEASON_EXP"] != "R" else 0,
        "position": player_data["POSITION"],
        "college": player_data["SCHOOL"],
        "salary": salary
    }

    return player_data
    
@lru_cache(maxsize=32)
def get_team_players_info(team_id, retries=3, timeout=60):
    """Obtém informações dos jogadores de um time específico."""
    for attempt in range(retries):
        try:
            roster = CommonTeamRoster(team_id=team_id, timeout=timeout).get_data_frames()[0]
            players_info = []

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(get_player_info, player["PLAYER_ID"]): player for _, player in roster.iterrows()}
                for future in as_completed(futures):
                    player_info = future.result()
                    player_info['image_url'] = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_info['id']}.png"
                    players_info.append(convert_numpy_types(player_info))

            return players_info
        except ReadTimeout:
            if attempt < retries - 1:
                continue
            else:
                raise

lru_cache(maxsize=32)
def get_player_game_logs(teamId, season="2024-25"):
    """Obtém os dados dos jogos de todos os jogadores de um time para a temporada especificada."""
    try:
        roster_df = CommonTeamRoster(team_id=teamId, season=season).get_data_frames()[0]
        if roster_df.empty:
            return {"error": "Nenhum jogador encontrado para esse time."}

        player_ids = roster_df["PLAYER_ID"].tolist()
        players_game_logs = {}

        for player_id in player_ids:
            try:
                response = PlayerGameLog(player_id=player_id, season=season, timeout=30).get_data_frames()
                if not response or response[0].empty:
                    print(f"Nenhum jogo encontrado para o jogador {player_id}. Pulando.")
                    continue

                game_logs = response[0]
                game_logs = game_logs.rename(columns={
                    "GAME_DATE": "Data do Jogo",
                    "MATCHUP": "Adversário",
                    "WL": "V ou D",
                    "PTS": "Pontos",
                    "REB": "Rebotes",
                    "AST": "Assistências",
                })

                game_logs["Casa/Fora"] = game_logs["Adversário"].apply(lambda x: "Casa" if "vs." in x else "Fora")
                game_logs["Adversário"] = game_logs["Adversário"].apply(lambda x: x.split()[-1])

                players_game_logs[player_id] = game_logs[[
                    "Data do Jogo", "Adversário", "V ou D", "Casa/Fora", "Pontos", "Rebotes", "Assistências"
                ]].to_dict(orient="records")

            except requests.exceptions.ReadTimeout:
                print(f"Timeout ao buscar dados do jogador {player_id}. Pulando.")
            except Exception as e:
                print(f"Erro ao obter dados do jogador {player_id}: {e}")

        return players_game_logs

    except Exception as e:
        return {"error": f"Erro ao obter jogadores do time {teamId}: {e}"}


def get_game_score(game_id, retries=3, timeout=60):
    """Obtém o placar do jogo usando o ID do jogo, com tentativas extras."""
    for attempt in range(retries):
        try:
            box_score = BoxScoreTraditionalV2(game_id=game_id, timeout=timeout).get_data_frames()[0]
            team_scores = box_score.groupby('TEAM_ID')['PTS'].sum()
            return f"{team_scores.iloc[0]} - {team_scores.iloc[1]}"
        except requests.exceptions.ReadTimeout:
            print(f"Tentativa {attempt + 1}/{retries}: Timeout ao buscar placar do jogo {game_id}. Tentando novamente...")
            time.sleep(5)  # Espera 5 segundos antes de tentar novamente
        except Exception as e:
            print(f"Erro ao obter o placar do jogo {game_id}: {e}")
            return "N/A"

    return "Timeout: API da NBA não respondeu"

    
def count_team_games(team_id, season='2024-25', opponent_team_abbr=None):
    """Conta a quantidade de jogos dentro e fora de casa de um time e contra um adversário específico."""

    team_games = TeamGameLog(team_id=team_id, season=season).get_data_frames()[0]

    team_games['Casa/Fora'] = team_games['MATCHUP'].apply(lambda x: 'Casa' if 'vs.' in x else 'Fora')

    total_home_games = team_games[team_games['Casa/Fora'] == 'Casa'].shape[0]
    total_away_games = team_games[team_games['Casa/Fora'] == 'Fora'].shape[0]

    if opponent_team_abbr:
        games_against_opponent = team_games[team_games['MATCHUP'].str.contains(opponent_team_abbr, case=False)]
        home_vs_opponent = games_against_opponent[games_against_opponent['Casa/Fora'] == 'Casa'].shape[0]
        away_vs_opponent = games_against_opponent[games_against_opponent['Casa/Fora'] == 'Fora'].shape[0]
    else:
        home_vs_opponent = away_vs_opponent = 0

    return {
        "total_home_games": total_home_games,
        "total_away_games": total_away_games,
        "home_vs_opponent": home_vs_opponent,
        "away_vs_opponent": away_vs_opponent
    }

def get_player_stats(player_id):
    """Retorna a média, mediana, moda e desvio padrão de pontos, rebotes e assistências de um jogador."""

    try:
        game_logs = PlayerGameLog(player_id=player_id, season='2024-25').get_data_frames()[0]

        # Se não houver dados, retornar uma resposta vazia
        if game_logs.empty:
            return {"player_id": player_id, "error": "Nenhum dado encontrado para o jogador."}

        # Selecionando apenas as colunas necessárias
        game_logs = game_logs[['MATCHUP', 'PTS', 'REB', 'AST']]

        # Convertendo os dados para listas
        pts = game_logs['PTS'].astype(float).tolist()
        reb = game_logs['REB'].astype(float).tolist()
        ast = game_logs['AST'].astype(float).tolist()

        # Calculando estatísticas
        stats_data = {
            "player_id": int(player_id),
            "average": {
                "points": round(float(np.mean(pts)), 2),
                "rebounds": round(float(np.mean(reb)), 2),
                "assists": round(float(np.mean(ast)), 2)
            },
            "median": {
                "points": float(np.median(pts)),
                "rebounds": float(np.median(reb)),
                "assists": float(np.median(ast))
            },
            "mode": {
                "points": float(stats.mode(pts, keepdims=True)[0][0]) if pts else None,
                "rebounds": float(stats.mode(reb, keepdims=True)[0][0]) if reb else None,
                "assists": float(stats.mode(ast, keepdims=True)[0][0]) if ast else None
            },
            "standard_deviation": {
                "points": round(float(np.std(pts, ddof=1)), 2) if len(pts) > 1 else None,
                "rebounds": round(float(np.std(reb, ddof=1)), 2) if len(reb) > 1 else None,
                "assists": round(float(np.std(ast, ddof=1)), 2) if len(ast) > 1 else None
            }
        }

        return stats_data

    except Exception as e:
        return {"player_id": player_id, "error": f"Erro ao obter estatísticas: {str(e)}"}


@lru_cache(maxsize=32)
def get_player_career_stats(player_id):
    """Obtém as estatísticas totais da carreira de um jogador (pontos, assistências e rebotes)."""
    try:
        career_stats = PlayerCareerStats(player_id=player_id).get_data_frames()[0]

        # Se não houver dados, retorna erro
        if career_stats.empty:
            return {"player_id": player_id, "error": "Nenhum dado encontrado para a carreira do jogador."}

        # Somando os totais de pontos, assistências e rebotes na carreira
        total_points = int(career_stats["PTS"].sum())
        total_assists = int(career_stats["AST"].sum())
        total_rebounds = int(career_stats["REB"].sum())

        return {
            "player_id": player_id,
            "career": {
                "total_points": total_points,
                "total_assists": total_assists,
                "total_rebounds": total_rebounds
            }
        }
    
    except Exception as e:
        return {"player_id": player_id, "error": f"Erro ao obter estatísticas de carreira: {str(e)}"}

@lru_cache(maxsize=32)
def get_player_season_vs_career(player_id):
    """Obtém estatísticas comparativas entre a temporada atual e a carreira do jogador."""
    try:
        # 📌 1. Buscar estatísticas da carreira (RF9)
        career_stats = PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        
        if career_stats.empty:
            return {"player_id": player_id, "error": "Nenhum dado de carreira encontrado para o jogador."}

        total_games_career = int(career_stats["GP"].sum())  # Total de jogos na carreira
        total_points_career = int(career_stats["PTS"].sum())  # Pontos na carreira
        total_assists_career = int(career_stats["AST"].sum())  # Assistências na carreira
        total_rebounds_career = int(career_stats["REB"].sum())  # Rebotes na carreira
        total_minutes_career = int(career_stats["MIN"].sum()) if "MIN" in career_stats.columns else None  # Minutos na carreira
        
        # 📌 2. Buscar estatísticas da temporada atual (RF5)
        season_logs = PlayerGameLog(player_id=player_id, season='2024-25').get_data_frames()[0]
        
        if season_logs.empty:
            return {"player_id": player_id, "error": "Nenhum dado da temporada encontrado para o jogador."}

        total_games_season = len(season_logs)  # Total de jogos na temporada atual
        total_points_season = season_logs["PTS"].sum()  # Pontos na temporada
        total_assists_season = season_logs["AST"].sum()  # Assistências na temporada
        total_rebounds_season = season_logs["REB"].sum()  # Rebotes na temporada
        total_minutes_season = season_logs["MIN"].astype(float).sum() if "MIN" in season_logs.columns else None  # Minutos na temporada

        # 📌 3. Calcular médias
        avg_points_season = round(total_points_season / total_games_season, 2)
        avg_assists_season = round(total_assists_season / total_games_season, 2)
        avg_rebounds_season = round(total_rebounds_season / total_games_season, 2)
        avg_minutes_season = round(total_minutes_season / total_games_season, 2) if total_minutes_season else None

        avg_points_career = round(total_points_career / total_games_career, 2)
        avg_assists_career = round(total_assists_career / total_games_career, 2)
        avg_rebounds_career = round(total_rebounds_career / total_games_career, 2)
        avg_minutes_career = round(total_minutes_career / total_games_career, 2) if total_minutes_career else None

        return {
            "player_id": player_id,
            "season": {
                "total_games": total_games_season,
                "average_points": avg_points_season,
                "average_assists": avg_assists_season,
                "average_rebounds": avg_rebounds_season,
                "total_minutes": total_minutes_season
            },
            "career": {
                "total_games": total_games_career,
                "average_points": avg_points_career,
                "average_assists": avg_assists_career,
                "average_rebounds": avg_rebounds_career,
                "total_minutes": total_minutes_career
            }
        }

    except Exception as e:
        return {"player_id": player_id, "error": f"Erro ao obter comparação de estatísticas: {str(e)}"}
