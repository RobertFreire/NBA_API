from flask import send_file
from app.graphs import generate_team_graph, generate_player_graph

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
