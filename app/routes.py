from flask import Blueprint, jsonify, send_file
from app.services import get_team_stats, get_player_stats
from app.graphs import generate_team_graph, generate_player_graph

# Criando o Blueprint
main = Blueprint('main', __name__)

@main.route('/team', methods=['GET'])
def team_stats():
    """Retorna as estatísticas formatadas do New Orleans Pelicans"""
    stats = get_team_stats()
    return jsonify({
        "team": "New Orleans Pelicans",
        "season": "2023-24",
        "stats": stats
    })

@main.route('/player/<name>', methods=['GET'])
def player_stats(name):
    """Retorna as estatísticas formatadas do jogador"""
    stats = get_player_stats(name)
    
    if "error" in stats:
        return jsonify(stats), 404  # Retorna erro 404 se o jogador não for encontrado
    
    return jsonify({
        "player": name,
        "stats": stats
    })

@main.route('/team/graph', methods=['GET'])
def team_graph():
    """Gera e retorna o gráfico de vitórias x derrotas do time"""
    team_stats = get_team_stats()
    graph_path = generate_team_graph(team_stats)
    return send_file(graph_path, mimetype='image/png')

@main.route('/player/<name>/graph', methods=['GET'])
def player_graph(name):
    """Gera e retorna o gráfico de evolução de pontos do jogador"""
    stats = get_player_stats(name)
    
    if "error" in stats:
        return jsonify(stats), 404  # Retorna erro 404 se o jogador não for encontrado

    graph_path = generate_player_graph(stats, name)
    return send_file(graph_path, mimetype='image/png')
