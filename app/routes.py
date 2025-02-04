from flask import Blueprint, jsonify
from app.services import (
    get_teams_by_conference, get_team_rankings,
    get_team_results, get_team_general_stats, 
    get_team_divided_stats, 
    get_team_defensive_stats, get_team_games, 
    get_bar_chart_win_loss, get_pie_chart_win_loss, 
    get_radar_chart_points
)


# Criando o Blueprint
main = Blueprint('main', __name__)

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
    """Retorna os resultados de vitórias e derrotas do time."""
    return get_team_results(team_id) 

### rf4
@main.route('/team/<int:team_id>/general_stats', methods=['GET'])
def team_general_stats(team_id):
    """Retorna estatísticas gerais do time para a temporada."""
    stats = get_team_general_stats(team_id)

    return jsonify(stats), 200

### rf5
@main.route('/team/<int:team_id>/divided_stats', methods=['GET'])
def team_divided_stats(team_id):
    """Retorna a divisão de estatísticas do time para a temporada."""
    stats = get_team_divided_stats(team_id)
    return jsonify(stats), 200

### rf6
@main.route('/team/<int:team_id>/defensive_stats', methods=['GET'])
def team_defensive_stats(team_id):
    """Retorna as estatísticas defensivas do time para a temporada."""
    stats = get_team_defensive_stats(team_id)
    return jsonify(stats), 200

### rf7
@main.route('/team/<int:team_id>/games', methods=['GET'])
def team_games(team_id):
    """Retorna a lista de jogos do time para a temporada."""
    games = get_team_games(team_id)
    return jsonify(games), 200

### rf8

@main.route('/team/<int:team_id>/graph/bar_win_loss', methods=['GET'])
def graph_bar_win_loss(team_id):
    """Retorna os dados para um gráfico de barras empilhado de vitórias e derrotas."""
    return jsonify(get_bar_chart_win_loss(team_id)), 200

@main.route('/team/<int:team_id>/graph/pie_win_loss', methods=['GET'])
def graph_pie_win_loss(team_id):
    """Retorna os dados para um gráfico de pizza de vitórias e derrotas."""
    return jsonify(get_pie_chart_win_loss(team_id)), 200

@main.route('/team/<int:team_id>/graph/radar_points', methods=['GET'])
def graph_radar_points(team_id):
    """Retorna os dados para um gráfico de radar de pontos marcados e sofridos."""
    return jsonify(get_radar_chart_points(team_id)), 200



