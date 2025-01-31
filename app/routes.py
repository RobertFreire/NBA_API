from flask import Blueprint, jsonify
from app.services import get_team_stats, get_player_stats

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
