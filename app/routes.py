from flask import Blueprint, jsonify, request
import asyncio
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
    get_player_info
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
