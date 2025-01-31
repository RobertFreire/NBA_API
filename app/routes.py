from flask import Blueprint, jsonify, send_file, render_template
from app.services import (
    get_team_stats, get_player_stats,
    save_team_stats_to_csv, save_player_stats_to_csv
)
from app.graphs import (
    generate_team_graph, generate_player_graph, generate_histogram,
    generate_radar_chart, generate_boxplot, generate_pie_chart, generate_scatter_plot
)

# Criando o Blueprint
main = Blueprint('main', __name__)

### 📊 ENDPOINTS DE ESTATÍSTICAS ###
@main.route('/team', methods=['GET'])
def team_stats():
    """Retorna as estatísticas formatadas do New Orleans Pelicans e salva em CSV"""
    stats = get_team_stats()
    save_team_stats_to_csv(stats)  # Salva os dados do time automaticamente em CSV
    return jsonify({
        "team": "New Orleans Pelicans",
        "season": "2023-24",
        "stats": stats
    })

@main.route('/player/<name>', methods=['GET'])
def player_stats(name):
    """Retorna as estatísticas formatadas do jogador e salva em CSV"""
    stats = get_player_stats(name)

    if "error" in stats:
        return jsonify(stats), 404  # Retorna erro 404 se o jogador não for encontrado

    save_player_stats_to_csv(stats, name)  # Salva os dados do jogador automaticamente em CSV

    return jsonify({
        "player": name,
        "stats": stats
    })

### 📈 ENDPOINTS DE GRÁFICOS ###
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
        return jsonify(stats), 404

    graph_path = generate_player_graph(stats, name)
    return send_file(graph_path, mimetype='image/png')

@main.route('/team/graph/histogram', methods=['GET'])
def team_histogram():
    """Gera e retorna o histograma de vitórias e derrotas do time"""
    team_stats = get_team_stats()
    graph_path = generate_histogram(team_stats)
    return send_file(graph_path, mimetype='image/png')

@main.route('/team/graph/radar', methods=['GET'])
def team_radar():
    """Gera e retorna o gráfico de radar do time"""
    team_stats = get_team_stats()
    graph_path = generate_radar_chart(team_stats)
    return send_file(graph_path, mimetype='image/png')

@main.route('/player/<name>/graph/boxplot', methods=['GET'])
def player_boxplot(name):
    """Gera e retorna o boxplot do jogador"""
    stats = get_player_stats(name)
    
    if "error" in stats:
        return jsonify(stats), 404

    graph_path = generate_boxplot(stats, name)
    return send_file(graph_path, mimetype='image/png')

@main.route('/team/graph/pie', methods=['GET'])
def team_pie_chart():
    """Gera e retorna o gráfico de pizza do time"""
    team_stats = get_team_stats()
    graph_path = generate_pie_chart(team_stats)
    return send_file(graph_path, mimetype='image/png')

@main.route('/player/<name>/graph/scatter', methods=['GET'])
def player_scatter(name):
    """Gera e retorna o gráfico de dispersão do jogador"""
    stats = get_player_stats(name)
    
    if "error" in stats:
        return jsonify(stats), 404

    graph_path = generate_scatter_plot(stats, name)
    return send_file(graph_path, mimetype='image/png')

### 🖥️ ENDPOINT DO DASHBOARD ###
@main.route('/dashboard', methods=['GET'])
def dashboard():
    """Renderiza um dashboard simples com os gráficos"""
    return render_template("dashboard.html")
