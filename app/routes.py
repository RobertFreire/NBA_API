from flask import Blueprint, jsonify, request
from pygam import PoissonGAM, LinearGAM, s, te
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from sklearn.metrics import confusion_matrix, roc_curve, auc
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import pandas as pd
import numpy as np
from app.services import (
    get_teams_by_conference, get_team_rankings,
    get_team_results_both_seasons, get_team_general_stats, 
    get_team_divided_stats, get_line_chart_win_streak,
    get_team_defensive_stats, get_team_games, 
    get_bar_chart_win_loss, get_pie_chart_win_loss,
    get_bar_chart_home_away, get_histogram_win_loss,
    get_radar_chart_points, save_team_stats_to_csv,
    save_team_games_to_csv, save_defensive_stats_to_csv,
    save_offensive_stats_to_csv, save_graph_data_to_csv,
    get_scatter_chart_points, get_team_basic_info,
    get_team_players_info, get_player_game_logs,
    count_team_games, get_player_stats, get_player_career_stats, get_player_season_vs_career,
    save_player_stats_to_csv, save_player_games_to_csv, save_performance_graphs,
    get_player_info, calculate_gumbel_distribution, get_team_players_games_parallel, get_home_away_stats, get_player_median_stats
)


# Criando o Blueprint
main = Blueprint('main', __name__)

@main.route('/team/<int:team_id>/info', methods=['GET'])
def team_info(team_id):
    """Retorna informações gerais do time, incluindo estatísticas gerais, jogos, estatísticas defensivas, estatísticas ofensivas e gráficos."""
    info = get_team_basic_info(team_id)
    return jsonify(info), 200

## ------parte 1------ 

###  RF1 
@main.route('/teams', methods=['GET'])
def list_teams():
    """Retorna a lista de times da NBA agrupados por conferência."""
    teams = get_teams_by_conference()
    return jsonify(teams), 200

### RF2 
@main.route('/teams/ranking', methods=['GET'])
def team_ranking():
    """Retorna a classificação atual dos times agrupados por conferência."""
    rankings = get_team_rankings()
    return jsonify(rankings), 200

### RF3 
@main.route('/team/<int:team_id>/results', methods=['GET'])
def team_results(team_id):
    """Retorna os resultados de vitórias e derrotas do time para ambas as temporadas."""
    return jsonify(get_team_results_both_seasons(team_id)), 200


### rf4
@main.route("/team/<int:team_id>/general_stats", methods=["GET"])
def team_general_stats(team_id):
    stats = get_team_general_stats(team_id)
    return jsonify(stats), 200

### rf5
@main.route('/team/<int:team_id>/divided_stats', methods=['GET'])
def team_divided_stats(team_id):
    """Retorna a divisão de estatísticas do time para a temporada 2023-24 e 2024-25."""
    stats = get_team_divided_stats(team_id)
    return jsonify(stats), 200

### rf6
@main.route('/team/<int:team_id>/defensive_stats', methods=['GET'])
def team_defensive_stats(team_id):
    """Retorna as estatísticas defensivas do time para ambas as temporadas."""
    stats = get_team_defensive_stats(team_id)
    return jsonify(stats), 200

### rf7
@main.route('/team/<int:team_id>/games', methods=['GET'])
def team_games(team_id):
    """Retorna a lista de jogos do time para as temporadas 2023-24 e 2024-25."""
    games = get_team_games(team_id)
    return jsonify(games), 200

### rf8

@main.route('/team/<int:team_id>/graph/bar_win_loss', methods=['GET'])
def graph_bar_win_loss(team_id):
    """Retorna os dados para um gráfico de barras empilhado de vitórias e derrotas."""
    return jsonify(get_bar_chart_win_loss(team_id)), 200

@main.route('/team/<int:team_id>/graph/bar_home_away', methods=['GET'])
def graph_bar_home_away(team_id):
    """Retorna os dados para um gráfico de barras agrupado de vitórias e derrotas em casa e fora."""
    return jsonify(get_bar_chart_home_away(team_id)), 200

@main.route('/team/<int:team_id>/graph/pie_win_loss', methods=['GET'])
def graph_pie_win_loss(team_id):
    """Retorna os dados para um gráfico de pizza de vitórias e derrotas."""
    return jsonify(get_pie_chart_win_loss(team_id)), 200

@main.route('/team/<int:team_id>/graph/radar_points', methods=['GET'])
def graph_radar_points(team_id):
    """Retorna os dados para um gráfico de radar de pontos marcados e sofridos."""
    return jsonify(get_radar_chart_points(team_id)), 200

@main.route('/team/<int:team_id>/graph/histogram_win_loss', methods=['GET'])
def graph_histogram_win_loss(team_id):
    """Retorna os dados para um gráfico de histograma de vitórias e derrotas."""
    return jsonify(get_histogram_win_loss(team_id)), 200

@main.route('/team/<int:team_id>/graph/line_win_streak', methods=['GET'])
def graph_line_win_streak(team_id):
    """Retorna os dados para um gráfico de linhas mostrando a sequência de vitórias e derrotas ao longo da temporada."""
    return jsonify(get_line_chart_win_streak(team_id)), 200

@main.route('/team/<int:team_id>/graph/scatter_points', methods=['GET'])
def graph_scatter_points(team_id):
    """Retorna os dados para um gráfico de dispersão mostrando a média de pontos marcados e sofridos durante a temporada."""
    return jsonify(get_scatter_chart_points(team_id)), 200

### rf9
@main.route('/team/<int:team_id>/save_all', methods=['GET'])
def save_all_data(team_id):
    """Salva todas as estatísticas do time para as temporadas 2023-24 e 2024-25 em CSV."""
    seasons = ["2023-24", "2024-25"]

    for season in seasons:
        save_team_stats_to_csv(team_id, season)
        save_team_games_to_csv(team_id, season)
        save_defensive_stats_to_csv(team_id, season)
        save_offensive_stats_to_csv(team_id, season)
        save_graph_data_to_csv(team_id, season)

    return jsonify({"message": f"Todos os dados do time {team_id} para as temporadas 2023-24 e 2024-25 foram salvos com sucesso!"}), 200


### JOGADORES

#RF1
@main.route('/team/<int:team_id>/players', methods=['GET'])
def team_players(team_id):
    """Retorna informações dos jogadores de um time específico."""
    players_info = get_team_players_info(team_id)
    return jsonify(players_info), 200

@main.route('/player/<int:player_id>', methods=['GET'])
def player_info(player_id):
    """Retorna informações de um jogador específico."""
    player_data = get_player_info(player_id)
    return jsonify(player_data), 200

# RF2 & RF3
@main.route('/player/<int:player_id>/games', methods=['GET'])
def team_players_games(player_id):
    """Retorna os dados dos jogos de todos os jogadores de um time específico durante a temporada atual."""
    
    players_game_logs = get_player_game_logs(player_id, '2024-25')
    
    return jsonify(players_game_logs), 200

#RF4
@main.route('/team/<int:team_id>/player/<int:player_id>/home_away_games', methods=['GET'])
def home_away_games(team_id, player_id):
    """Retorna a quantidade de jogos realizados dentro e fora de casa, e contra um determinado time."""
    opponent = request.args.get('opponent')
    season = request.args.get('season', '2024-25')
    games_count = count_team_games(team_id, player_id, season, opponent), 
    return jsonify(games_count), 200

#RF5 RF6 RF7 RF8
@main.route('/player/<int:player_id>/stats', methods=['GET'])
def player_stats(player_id):
    """Retorna a média, mediana, moda e desvio padrão de pontos, rebotes e assistências de um jogador específico."""
    stats = get_player_stats(player_id)
    return jsonify(stats), 200

#RF9
@main.route('/player/<int:player_id>/career_stats', methods=['GET'])
def player_career_stats(player_id):
    """Retorna os totais de pontos, assistências e rebotes da carreira do jogador."""
    stats = get_player_career_stats(player_id)
    return jsonify(stats), 200

#RF10
@main.route('/player/<int:player_id>/season_vs_career', methods=['GET'])
def player_season_vs_career(player_id):
    """Retorna a comparação das estatísticas da temporada atual com a carreira do jogador."""
    stats = get_player_season_vs_career(player_id)
    return jsonify(stats), 200


@main.route('/player/<int:player_id>/save_stats', methods=['GET'])
def save_player_stats(player_id):
    """Salva as estatísticas da temporada e da carreira do jogador em CSV."""
    save_player_stats_to_csv(player_id)
    save_player_games_to_csv(player_id)
    return jsonify({"message": f"Estatísticas e jogos do jogador {player_id} salvos com sucesso!"}), 200

@main.route('/player/<int:player_id>/generate_graphs', methods=['GET'])
def generate_graphs(player_id):
    """Gera e salva gráficos de desempenho do jogador em HTML."""
    save_performance_graphs(player_id)
    return jsonify({"message": f"Gráficos do jogador {player_id} gerados com sucesso!"}), 200


@main.route('/player/<int:player_id>/gumbel', methods=['GET'])
def calculate_gumbel_distribution_endpoint(player_id):
    """Calcula probabilidades baseadas na distribuição de Gumbel para pontos, rebotes e assistências."""
    points = request.args.get("points", type=int, default=0)
    rebounds = request.args.get("rebounds", type=int, default=0)
    assists = request.args.get("assists", type=int, default=0)

    # Chama a função do services.py
    result = calculate_gumbel_distribution(player_id, points, rebounds, assists)
    return jsonify(result), 200


@main.route('/team/<int:team_id>/players/games', methods=['GET'])
def get_team_players_games(team_id):
    """
    Retorna os dados detalhados dos jogos de cada jogador de um time
    durante a temporada atual (2024-25), utilizando paralelismo.
    """
    season = "2024-25"
    try:
        # Obter informações dos jogadores do time
        players_info = get_team_players_info(team_id)

        if not players_info:
            return jsonify({"error": "Nenhum jogador encontrado para o time."}), 404

        players_games = {}

        # Processar requisições de forma paralela
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_player = {
                executor.submit(get_player_game_logs, player["id"], season): player["name"]
                for player in players_info
            }

            for future in as_completed(future_to_player):
                player_name = future_to_player[future]
                try:
                    game_logs = future.result()
                    if game_logs:
                        players_games[player_name] = game_logs
                except Exception as e:
                    print(f"Erro ao processar jogador {player_name}: {e}")

        if not players_games:
            return jsonify({"error": "Nenhum dado de jogos encontrado para os jogadores do time."}), 404

        return jsonify(players_games), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar os dados: {str(e)}"}), 500

@main.route('/player/<int:player_id>/games/filter', methods=['GET'])
def filter_player_games(player_id):
    """
    Filtra os dados de jogos de um jogador contra um adversário específico.
    """
    opponent = request.args.get("opponent", "").upper()
    season = request.args.get("season", "2024-25")

    if not opponent:
        return jsonify({"error": "É necessário fornecer o adversário (opponent)."}), 400

    try:
        # Obter os dados dos jogos do jogador
        game_logs = get_player_game_logs(player_id, season)

        if not game_logs:
            return jsonify({"error": f"Nenhum jogo encontrado para o jogador {player_id} na temporada {season}."}), 404

        # Filtrar os jogos pelo adversário
        filtered_games = [
            game for game in game_logs
            if game["Adversario"].upper() == opponent
        ]

        if not filtered_games:
            return jsonify({"error": f"Nenhum jogo encontrado contra o adversário {opponent}."}), 404

        return jsonify(filtered_games), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao filtrar jogos: {str(e)}"}), 500


@main.route('/player/<int:player_id>/home_away_stats', methods=['GET'])
def player_home_away_stats(player_id):
    """
    Retorna a quantidade de jogos dentro e fora de casa, e os jogos contra um adversário específico.
    """
    season = request.args.get("season", "2024-25")
    opponent = request.args.get("opponent")  # Adversário opcional

    stats = get_home_away_stats(player_id=player_id, season=season, opponent=opponent)
    return jsonify(stats), 200

@main.route('/player/<int:player_id>/averages', methods=['GET'])
def player_averages(player_id):
    """
    Retorna a média de pontos, rebotes e assistências de um jogador,
    bem como a porcentagem de jogos abaixo da média para cada estatística.
    """
    season = request.args.get("season", "2024-25")
    from app.services import calculate_player_averages
    stats = calculate_player_averages(player_id, season)
    return jsonify(stats), 200

@main.route('/player/<int:player_id>/medians', methods=['GET'])
def player_median_stats(player_id):
    """Retorna a mediana de pontos, rebotes e assistências de um jogador e a porcentagem abaixo da mediana."""
    season = request.args.get('season', '2024-25')
    stats = get_player_median_stats(player_id, season)
    return jsonify(stats), 200

def convert_to_native(obj):
    """Converte tipos NumPy para tipos nativos do Python antes da serialização."""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(i) for i in obj]
    return obj

@main.route('/player/<int:player_id>/modes', methods=['GET'])
def calculate_modes(player_id):
    """Calcula as modas de pontos, rebotes e assistências do jogador."""
    season = request.args.get('season', '2024-25')

    try:
        game_logs = get_player_game_logs(player_id, season)
        
        if not game_logs:
            return jsonify({"error": "Nenhum dado encontrado para o jogador."}), 404

        # Verificar as chaves nos dados retornados
        points = [log["Pontos"] for log in game_logs if "Pontos" in log]
        rebounds = [log["Rebotes"] for log in game_logs if "Rebotes" in log]
        assists = [log["Assistencias"] for log in game_logs if "Assistencias" in log]  # Alterado para chave sem acento

        if not points or not rebounds or not assists:
            return jsonify({"error": "Dados incompletos para calcular as modas."}), 400

        modes = {
            "points": stats.mode(points, keepdims=True)[0][0] if points else None,
            "rebounds": stats.mode(rebounds, keepdims=True)[0][0] if rebounds else None,
            "assists": stats.mode(assists, keepdims=True)[0][0] if assists else None
        }

        mode_counts = {
            "points": stats.mode(points, keepdims=True)[1][0] if points else None,
            "rebounds": stats.mode(rebounds, keepdims=True)[1][0] if rebounds else None,
            "assists": stats.mode(assists, keepdims=True)[1][0] if assists else None
        }

        percentage_below_mode = {
            "points": sum(1 for p in points if p < modes["points"]) / len(points) * 100 if points else None,
            "rebounds": sum(1 for r in rebounds if r < modes["rebounds"]) / len(rebounds) * 100 if rebounds else None,
            "assists": sum(1 for a in assists if a < modes["assists"]) / len(assists) * 100 if assists else None
        }

        result = {
            "player_id": player_id,
            "modes": convert_to_native(modes),
            "mode_counts": convert_to_native(mode_counts),
            "percentage_below_mode": convert_to_native(percentage_below_mode)
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar os dados: {str(e)}"}), 500


def calculate_roc_curve(y_true, y_pred):
    """Converte os valores para binário e calcula a curva ROC."""
    threshold = np.mean(y_true)  # Ajuste do threshold correto
    y_true_binary = [1 if val > threshold else 0 for val in y_true]
    
    fpr, tpr, _ = roc_curve(y_true_binary, y_pred)
    roc_auc = auc(fpr, tpr)

    return {
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "roc_auc": roc_auc
    }


# Função para calcular a matriz de confusão
def calculate_confusion_matrix(y_true, y_pred):
    """Calcula a matriz de confusão convertendo valores contínuos para binários."""
    threshold = np.mean(y_true)  # Usar média como limiar
    y_true_binary = [1 if val > threshold else 0 for val in y_true]

    cm = confusion_matrix(y_true_binary, y_pred)
    return cm.tolist()


@main.route('/player/<int:player_id>/regression', methods=['GET'])
def player_regression(player_id):
    """Realiza regressão linear para prever pontos, assistências e rebotes de um jogador."""
    season = request.args.get('season', '2024-25')
    
    try:
        game_logs = get_player_game_logs(player_id, season)
        
        if not game_logs:
            return jsonify({"error": "Nenhum dado encontrado para o jogador."}), 404

        # Preparar os dados
        X = [[log["Tempo de Permanencia do Jogador em Quadra"], log["Tentativas de Cestas de 3"], log["Turnovers"]] for log in game_logs]
        y_points = [log["Pontos"] for log in game_logs]
        y_rebounds = [log["Rebotes"] for log in game_logs]
        y_assists = [log["Assistencias"] for log in game_logs]

        # Dividir os dados em treinamento e teste
        X_train, X_test, y_points_train, y_points_test = train_test_split(X, y_points, test_size=0.2, random_state=42)
        X_train, X_test, y_rebounds_train, y_rebounds_test = train_test_split(X, y_rebounds, test_size=0.2, random_state=42)
        X_train, X_test, y_assists_train, y_assists_test = train_test_split(X, y_assists, test_size=0.2, random_state=42)

        # Treinamento do modelo de regressão linear
        model_points = LinearRegression().fit(X_train, y_points_train)
        model_rebounds = LinearRegression().fit(X_train, y_rebounds_train)
        model_assists = LinearRegression().fit(X_train, y_assists_train)

        # Fazer previsões
        y_points_pred = model_points.predict(X_test)
        y_rebounds_pred = model_rebounds.predict(X_test)
        y_assists_pred = model_assists.predict(X_test)

        # Ajuste na conversão binária (usar média do conjunto de teste)
        y_points_binary = [1 if pred > np.mean(y_points_test) else 0 for pred in y_points_pred]
        y_rebounds_binary = [1 if pred > np.mean(y_rebounds_test) else 0 for pred in y_rebounds_pred]
        y_assists_binary = [1 if pred > np.mean(y_assists_test) else 0 for pred in y_assists_pred]

        # Calcular probabilidades
        def calculate_probabilities(y_true, y_pred):
            mean = np.mean(y_true)
            median = np.median(y_true)
            mode = stats.mode(y_true, keepdims=True)[0]
            mode = mode[0] if len(mode) > 0 else np.nan  # Evita erro caso não exista moda
            max_val = np.max(y_true)
            min_val = np.min(y_true)

            probabilidades = {
                "acima_da_media": np.mean(y_pred > mean),
                "abaixo_da_media": np.mean(y_pred < mean),
                "acima_da_mediana": np.mean(y_pred > median),
                "abaixo_da_mediana": np.mean(y_pred < median),
                "acima_da_moda": np.mean(y_pred > mode) if not np.isnan(mode) else 0,
                "abaixo_da_moda": np.mean(y_pred < mode) if not np.isnan(mode) else 0,
                "acima_do_maximo": np.mean(y_pred > max_val),
                "abaixo_do_minimo": np.mean(y_pred < min_val)
            }
            return probabilidades

        points_probabilities = calculate_probabilities(y_points_test, y_points_pred)
        rebounds_probabilities = calculate_probabilities(y_rebounds_test, y_rebounds_pred)
        assists_probabilities = calculate_probabilities(y_assists_test, y_assists_pred)

        points_confusion_matrix = calculate_confusion_matrix(y_points_test, y_points_binary)
        rebounds_confusion_matrix = calculate_confusion_matrix(y_rebounds_test, y_rebounds_binary)
        assists_confusion_matrix = calculate_confusion_matrix(y_assists_test, y_assists_binary)

        points_roc_curve = calculate_roc_curve(y_points_test, y_points_pred)
        rebounds_roc_curve = calculate_roc_curve(y_rebounds_test, y_rebounds_pred)
        assists_roc_curve = calculate_roc_curve(y_assists_test, y_assists_pred)

        result = {
            "player_id": player_id,
            "points_probabilities": points_probabilities,
            "rebounds_probabilities": rebounds_probabilities,
            "assists_probabilities": assists_probabilities,
            "points_confusion_matrix": points_confusion_matrix,
            "rebounds_confusion_matrix": rebounds_confusion_matrix,
            "assists_confusion_matrix": assists_confusion_matrix,
            "points_roc_curve": points_roc_curve,
            "rebounds_roc_curve": rebounds_roc_curve,
            "assists_roc_curve": assists_roc_curve
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar os dados: {str(e)}"}), 500

    

@main.route('/player/<int:player_id>/logistic_regression', methods=['GET'])
def player_logistic_regression(player_id):
    """Realiza regressão logística para prever pontos, assistências e rebotes de um jogador."""
    season = request.args.get('season', '2024-25')
    
    try:
        game_logs = get_player_game_logs(player_id, season)
        
        if not game_logs:
            return jsonify({"error": "Nenhum dado encontrado para o jogador."}), 404

        # Preparar os dados
        X = [[log["Tempo de Permanencia do Jogador em Quadra"], log["Tentativas de Cestas de 3"], log["Turnovers"]] for log in game_logs]
        y_points = [1 if log["Pontos"] > np.mean([log["Pontos"] for log in game_logs]) else 0 for log in game_logs]
        y_rebounds = [1 if log["Rebotes"] > np.mean([log["Rebotes"] for log in game_logs]) else 0 for log in game_logs]
        y_assists = [1 if log["Assistencias"] > np.mean([log["Assistencias"] for log in game_logs]) else 0 for log in game_logs]

        # Dividir os dados em treinamento e teste
        X_train, X_test, y_points_train, y_points_test = train_test_split(X, y_points, test_size=0.2, random_state=42)
        _, _, y_rebounds_train, y_rebounds_test = train_test_split(X, y_rebounds, test_size=0.2, random_state=42)
        _, _, y_assists_train, y_assists_test = train_test_split(X, y_assists, test_size=0.2, random_state=42)

        # Treinar o modelo de regressão logística
        model_points = LogisticRegression().fit(X_train, y_points_train)
        model_rebounds = LogisticRegression().fit(X_train, y_rebounds_train)
        model_assists = LogisticRegression().fit(X_train, y_assists_train)

        # Fazer previsões
        y_points_pred = model_points.predict(X_test)
        y_rebounds_pred = model_rebounds.predict(X_test)
        y_assists_pred = model_assists.predict(X_test)

        # Calcular probabilidades
        def calculate_probabilities(y_true, y_pred):
            accuracy = accuracy_score(y_true, y_pred)
            confusion = confusion_matrix(y_true, y_pred)
            fpr, tpr, _ = roc_curve(y_true, y_pred)
            roc_auc = auc(fpr, tpr)

            probabilities = {
                "accuracy": accuracy,
                "confusion_matrix": confusion.tolist(),
                "roc_auc": roc_auc
            }
            return probabilities

        points_probabilities = calculate_probabilities(y_points_test, y_points_pred)
        rebounds_probabilities = calculate_probabilities(y_rebounds_test, y_rebounds_pred)
        assists_probabilities = calculate_probabilities(y_assists_test, y_assists_pred)

        result = {
            "player_id": player_id,
            "points_probabilities": points_probabilities,
            "rebounds_probabilities": rebounds_probabilities,
            "assists_probabilities": assists_probabilities
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar os dados: {str(e)}"}), 500
    

@main.route('/player/<int:player_id>/gam_predictions', methods=['GET'])
def player_gam_predictions(player_id):
    """Realiza previsões usando PoissonGAM e LinearGAM para pontos, assistências e rebotes de um jogador."""
    season = request.args.get('season', '2024-25')
    
    try:
        game_logs = get_player_game_logs(player_id, season)
        
        if not game_logs:
            return jsonify({"error": "Nenhum dado encontrado para o jogador."}), 404

        # Preparar os dados
        X = np.array([[log["Tempo de Permanencia do Jogador em Quadra"], log["Tentativas de Cestas de 3"], log["Turnovers"]] for log in game_logs])
        y_points = np.array([log["Pontos"] for log in game_logs])
        y_rebounds = np.array([log["Rebotes"] for log in game_logs])
        y_assists = np.array([log["Assistencias"] for log in game_logs])

        # Dividir os dados em treinamento e teste
        X_train, X_test, y_points_train, y_points_test = train_test_split(X, y_points, test_size=0.2, random_state=42)
        _, _, y_rebounds_train, y_rebounds_test = train_test_split(X, y_rebounds, test_size=0.2, random_state=42)
        _, _, y_assists_train, y_assists_test = train_test_split(X, y_assists, test_size=0.2, random_state=42)

        # Treinar os modelos PoissonGAM e LinearGAM
        gam_points = PoissonGAM(s(0) + s(1) + s(2)).fit(X_train, y_points_train)
        gam_rebounds = LinearGAM(s(0) + s(1) + s(2)).fit(X_train, y_rebounds_train)
        gam_assists = LinearGAM(s(0) + s(1) + s(2)).fit(X_train, y_assists_train)

        # Fazer previsões
        y_points_pred = gam_points.predict(X_test)
        y_rebounds_pred = gam_rebounds.predict(X_test)
        y_assists_pred = gam_assists.predict(X_test)

        # Calcular probabilidades
        def calculate_probabilities(y_true, y_pred):
            mean = np.mean(y_true)
            median = np.median(y_true)
            mode = stats.mode(y_true, keepdims=True)[0][0]
            max_val = np.max(y_true)
            min_val = np.min(y_true)

            probabilidades = {
                "acima_da_media": np.mean(y_pred > mean),
                "abaixo_da_media": np.mean(y_pred < mean),
                "acima_da_mediana": np.mean(y_pred > median),
                "abaixo_da_mediana": np.mean(y_pred < median),
                "acima_da_moda": np.mean(y_pred > mode),
                "abaixo_da_moda": np.mean(y_pred < mode),
                "acima_do_maximo": np.mean(y_pred > max_val),
                "abaixo_do_minimo": np.mean(y_pred < min_val)
            }
            return probabilidades

        points_probabilities = calculate_probabilities(y_points_test, y_points_pred)
        rebounds_probabilities = calculate_probabilities(y_rebounds_test, y_rebounds_pred)
        assists_probabilities = calculate_probabilities(y_assists_test, y_assists_pred)

        # Calcular erro quadrático médio e R² para as previsões
        points_mse = mean_squared_error(y_points_test, y_points_pred)
        rebounds_mse = mean_squared_error(y_rebounds_test, y_rebounds_pred)
        assists_mse = mean_squared_error(y_assists_test, y_assists_pred)

        points_r2 = r2_score(y_points_test, y_points_pred)
        rebounds_r2 = r2_score(y_rebounds_test, y_rebounds_pred)
        assists_r2 = r2_score(y_assists_test, y_assists_pred)

        result = {
            "player_id": player_id,
            "points_probabilities": points_probabilities,
            "rebounds_probabilities": rebounds_probabilities,
            "assists_probabilities": assists_probabilities,
            "points_mse": points_mse,
            "rebounds_mse": rebounds_mse,
            "assists_mse": assists_mse,
            "points_r2": points_r2,
            "rebounds_r2": rebounds_r2,
            "assists_r2": assists_r2
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao processar os dados: {str(e)}"}), 500


