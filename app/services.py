from nba_api.stats.static import teams
from nba_api.stats.endpoints import TeamDashboardByGeneralSplits, LeagueStandings
from nba_api.stats.endpoints import TeamGameLog
import pandas as pd
import os
import numpy as np
import orjson
from flask import Response

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
            "Total de Vitórias": int(overall_df["W"].iloc[0]),
            "Total de Derrotas": int(overall_df["L"].iloc[0]),
            "Vitórias em Casa": int(home_stats["W"]),
            "Vitórias Fora de Casa": int(away_stats["W"]),
            "Derrotas em Casa": int(home_stats["L"]),
            "Derrotas Fora de Casa": int(away_stats["L"])
        }

    return {
        "team_id": int(team_id),
        "results": results
    }



#rf4

def get_team_general_stats(team_id, season="2023-24"):
    """Obtém estatísticas gerais do time para a temporada."""
    team_stats = TeamDashboardByGeneralSplits(team_id=team_id, season=season)
    data_frames = team_stats.get_data_frames()
    
    # Imprimir os dados para verificar a resposta
    print("Resposta da API:", data_frames)

    # Certificar-se de que 'resultSet' ou o esperado está presente
    if len(data_frames) == 0:
        return {"error": "Nenhum dado encontrado para o time."}
    
    # Continuar com a lógica original se a resposta estiver correta
    df = data_frames[0]
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

    # Converte todos os valores NumPy para tipos serializáveis
    response_data = convert_numpy_types(response_data)

    return response_data



##rf5

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
def get_team_games(team_id, season=None):
    """Obtém a lista de jogos do time para as temporadas 2023-24 e 2024-25."""
    seasons = ["2023-24", "2024-25"]
    games = {}
    
    for season in seasons:
        team_games = TeamGameLog(team_id=team_id, season=season)
        df = team_games.get_data_frames()[0]  # Pegamos os dados de jogos

        selected_columns = {
            "GAME_DATE": "Data do Jogo",
            "MATCHUP": "Adversário",
            "WL": "Vitória ou Derrota",
            "PTS": "Pontos do Time"
        }

        # Se a coluna PLUS_MINUS existir, adicionamos ela
        if "PLUS_MINUS" in df.columns:
            selected_columns["PLUS_MINUS"] = "Saldo de Pontos"

        # Filtramos apenas as colunas existentes
        existing_columns = [col for col in selected_columns.keys() if col in df.columns]
        df = df[existing_columns].rename(columns={col: selected_columns[col] for col in existing_columns})

        # Transformar a coluna "Adversário" para indicar se o jogo foi em casa ou fora
        df["Casa ou Fora"] = df["Adversário"].apply(lambda x: "Casa" if "vs." in x else "Fora")
        df["Adversário"] = df["Adversário"].apply(lambda x: x.split()[-1])

        # Armazenar os jogos de cada temporada
        games[season] = {
            "team_id": int(team_id),
            "season": season,
            "games": df.to_dict(orient="records")
        }

    return games



## rf8
def get_bar_chart_win_loss(team_id, season="2023-24"):
    """Gera os dados para um gráfico de barras empilhado de vitórias e derrotas."""
    stats = get_team_results(team_id, season)["results"]
    
    return {
        "type": "bar",
        "labels": ["Vitórias", "Derrotas"],
        "values": [stats["Total de Vitórias"], stats["Total de Derrotas"]],
        "colors": ["green", "red"]
    }


def get_bar_chart_home_away(team_id, season="2023-24"):
    """Gera os dados para um gráfico de barras agrupado de vitórias e derrotas em casa e fora."""
    stats = get_team_results(team_id, season)["results"]
    
    return {
        "type": "bar",
        "labels": ["Vitórias Casa", "Vitórias Fora", "Derrotas Casa", "Derrotas Fora"],
        "values": [
            stats["Vitórias em Casa"], stats["Vitórias Fora de Casa"],
            stats["Derrotas em Casa"], stats["Derrotas Fora de Casa"]
        ],
        "colors": ["green", "blue", "red", "brown"]
    }


def get_histogram_win_loss(team_id, season="2023-24"):
    """Gera os dados para um histograma de vitórias e derrotas."""
    stats = get_team_results(team_id, season)["results"]
    
    return {
        "type": "histogram",
        "labels": ["Vitórias", "Derrotas"],
        "values": [stats["Total de Vitórias"], stats["Total de Derrotas"]],
        "colors": ["green", "red"]
    }


def get_pie_chart_win_loss(team_id, season="2023-24"):
    """Gera os dados para um gráfico de pizza de percentual de vitórias e derrotas."""
    stats = get_team_results(team_id, season)["results"]
    
    total_jogos = stats["Total de Vitórias"] + stats["Total de Derrotas"]
    
    return {
        "type": "pie",
        "labels": ["Vitórias", "Derrotas"],
        "values": [
            round(stats["Total de Vitórias"] / total_jogos * 100, 2),
            round(stats["Total de Derrotas"] / total_jogos * 100, 2)
        ],
        "colors": ["green", "red"]
    }


def get_radar_chart_points(team_id, season="2023-24"):
    """Gera os dados para um gráfico de radar mostrando pontos marcados e sofridos em casa e fora."""
    games = get_team_games(team_id, season)["games"]

    pontos_marcados_casa = sum([game["Pontos do Time"] for game in games if game["Casa ou Fora"] == "Casa"]) / len(games)
    pontos_marcados_fora = sum([game["Pontos do Time"] for game in games if game["Casa ou Fora"] == "Fora"]) / len(games)

    return {
        "type": "radar",
        "labels": ["Casa", "Fora"],
        "values": [round(pontos_marcados_casa, 2), round(pontos_marcados_fora, 2)],
        "colors": ["blue"]
    }


def get_line_chart_win_streak(team_id, season="2023-24"):
    """Gera os dados para um gráfico de linhas mostrando a sequência de vitórias e derrotas ao longo da temporada."""
    games = get_team_games(team_id, season)["games"]
    
    return {
        "type": "line",
        "labels": [game["Data do Jogo"] for game in games],
        "values": [1 if game["Vitória ou Derrota"] == "W" else 0 for game in games],
        "colors": ["blue"]
    }


def get_scatter_chart_points(team_id, season="2023-24"):
    """Gera os dados para um gráfico de dispersão mostrando a média de pontos marcados e sofridos por jogo."""
    games = get_team_games(team_id, season)["games"]

    return {
        "type": "scatter",
        "labels": [game["Adversário"] for game in games],
        "values": [game["Pontos do Time"] for game in games],
        "colors": ["orange"]
    }


