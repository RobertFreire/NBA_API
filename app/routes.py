from flask import Blueprint, jsonify
from app.services import (
    get_teams_by_conference, get_team_rankings,
    get_team_results, get_team_advanced_stats
)

# Criando o Blueprint
main = Blueprint('main', __name__)

### 📌 RF1 - Listar todos os times da NBA agrupados por conferência
@main.route('/teams', methods=['GET'])
def list_teams():
    """Retorna a lista de times da NBA agrupados por conferência."""
    teams = get_teams_by_conference()
    return jsonify(teams), 200

### 📌 RF2 - Apresentar a classificação atual dos times
@main.route('/teams/ranking', methods=['GET'])
def team_ranking():
    """Retorna a classificação atual dos times agrupados por conferência."""
    rankings = get_team_rankings()
    return jsonify(rankings), 200

### 📌 RF3 - Resultados do time (Vitórias e Derrotas)
@main.route('/team/<int:team_id>/results', methods=['GET'])
def team_results(team_id):
    """Retorna o total de vitórias e derrotas do time para a temporada especificada."""
    stats = get_team_results(team_id)
    return jsonify(stats), 200

### 📌 RF4, RF5, RF6 - Estatísticas avançadas do time
@main.route('/team/<int:team_id>/stats', methods=['GET'])
def team_advanced_stats(team_id):
    """Retorna estatísticas avançadas do time na temporada especificada."""
    stats = get_team_advanced_stats(team_id)
    return jsonify(stats), 200
