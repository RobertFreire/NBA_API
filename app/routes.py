from flask import Blueprint, jsonify, request
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
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


@main.route('/player/<int:player_id>/gumbel', methods=['POST'])
def calculate_gumbel_distribution_endpoint(player_id):
    """Calcula probabilidades baseadas na distribuição de Gumbel para pontos, rebotes e assistências."""
    data = request.json
    points = data.get("points", 0)
    rebounds = data.get("rebounds", 0)
    assists = data.get("assists", 0)

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


@main.route('/regression/linear/train', methods=['POST'])
def train_linear_regression():
    """
    Treina e testa um modelo de regressão linear com base nos dados fornecidos.
    """
    data = request.json  # Espera receber os dados em JSON (lista de dicionários)
    df = pd.DataFrame(data)

    # Variáveis independentes e dependentes
    X = df[["Tempo de Permanencia do Jogador em Quadra", "FGA", "TOV"]]
    y = df[["Pontos", "Assistencias", "Rebotes"]]

    # Divisão dos dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Modelo de regressão linear
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predições
    y_pred = model.predict(X_test)

    # Métricas
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Coeficientes do modelo
    coeficients = dict(zip(X.columns, model.coef_.tolist()))

    return jsonify({
        "mse": mse,
        "r2_score": r2,
        "coeficients": coeficients
    }), 200
    
def categorize(value):
    """Categorização em intervalos."""
    if value <= 10:
        return 0
    elif value <= 20:
        return 1
    elif value <= 30:
        return 2
    else:
        return 3
    
@main.route('/regression/linear/confusion_matrix', methods=['POST'])
def linear_regression_confusion_matrix():
    """
    Gera a matriz de confusão para a regressão linear com categorias.
    """
    data = request.json  # Recebe os dados como [{"real": valor, "predicted": valor}]
    if not data:
        return jsonify({"error": "Nenhum dado recebido."}), 400

    try:
        # Extrair valores reais e preditos e categorizá-los
        real = [categorize(item["real"]) for item in data]
        predicted = [categorize(item["predicted"]) for item in data]

        # Construir a matriz de confusão
        cm = confusion_matrix(real, predicted)
        return jsonify({"confusion_matrix": cm.tolist()}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao calcular matriz de confusão: {str(e)}"}), 500



@main.route('/regression/linear/roc_curve', methods=['POST'])
def linear_regression_roc_curve():
    """
    Gera os dados para a curva ROC.
    Recebe os dados reais e as probabilidades preditas para calcular a curva ROC.
    """
    data = request.json  # Recebe os dados como [{"real": valor, "prob": probabilidade}]
    if not data:
        return jsonify({"error": "Nenhum dado recebido."}), 400

    real = [item["real"] for item in data]
    probs = [item["prob"] for item in data]

    try:
        fpr, tpr, thresholds = roc_curve(real, probs)
        roc_auc = auc(fpr, tpr)
        return jsonify({
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
            "auc": roc_auc
        }), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao calcular curva ROC: {str(e)}"}), 500


@main.route('/regression/linear/coefficients', methods=['GET'])
def linear_regression_coefficients():
    """
    Retorna os coeficientes do modelo de regressão linear treinado.
    """
    try:
        # Certifique-se de que o modelo foi treinado previamente.
        if not linear_model:
            return jsonify({"error": "Modelo de regressão linear ainda não foi treinado."}), 400

        coefficients = {
            feature: coef for feature, coef in zip(["Tempo de Permanencia do Jogador em Quadra", "FGA", "TOV"], linear_model.coef_)
        }
        return jsonify({"coefficients": coefficients}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao retornar coeficientes: {str(e)}"}), 500
    
    
    