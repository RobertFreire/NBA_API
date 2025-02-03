from flask import Blueprint, jsonify, render_template
from app.services import get_team_stats_both_seasons, get_team_stats, get_player_stats
from app.statistics import calculate_team_stats, calculate_player_stats
from app.ml_model import train_player_model
from app.graphs import (
    generate_team_graph_data, generate_player_graph_data, generate_histogram_data,
    generate_radar_chart_data, generate_boxplot_data, generate_pie_chart_data, generate_scatter_plot_data
)

# Criando o Blueprint
main = Blueprint('main', __name__)

### 📌 RF1.1 - Listar estatísticas do time para `23-24` e `24-25`
@main.route('/team/stats', methods=['GET'])
def team_advanced_stats():
    """Retorna estatísticas do New Orleans Pelicans para `23-24` e `24-25`."""
    stats = get_team_stats_both_seasons()
    return jsonify(stats), 200

### 📌 RF1.2 - Estatísticas do time para uma temporada específica
@main.route('/team/stats/<season>', methods=['GET'])
def team_stats_season(season):
    """Retorna estatísticas do New Orleans Pelicans para uma temporada específica."""
    stats = get_team_stats(season)
    return jsonify(stats), 200

### 📌 RF2.1 - Estatísticas detalhadas de um jogador por temporada
@main.route('/player/<int:player_id>/stats', methods=['GET'])
def player_advanced_stats(player_id):
    """Retorna estatísticas descritivas do jogador pelo ID."""
    stats = get_player_stats(player_id)
    
    if "error" in stats:
        return jsonify(stats), 404

    return jsonify(stats), 200

### 📌 RF3.1 - Prever a pontuação de um jogador na próxima temporada
@main.route('/player/<int:player_id>/predict', methods=['GET'])
def predict_player_performance(player_id):
    """Prevê a pontuação de um jogador na próxima temporada usando Machine Learning."""
    prediction = train_player_model(player_id)
    
    if "error" in prediction:
        return jsonify(prediction), 400

    return jsonify(prediction), 200

### 📌 RF4.1 - Retornar gráficos como JSON (não imagens)
@main.route('/team/graph', methods=['GET'])
def team_graph():
    """Retorna os dados do gráfico de vitórias x derrotas do time em JSON."""
    team_stats = get_team_stats()
    graph_data = generate_team_graph_data(team_stats)
    return jsonify(graph_data), 200

@main.route('/player/<int:player_id>/graph', methods=['GET'])
def player_graph(player_id):
    """Retorna os dados do gráfico de evolução de pontos do jogador em JSON."""
    stats = get_player_stats(player_id)
    
    if "error" in stats:
        return jsonify(stats), 404

    graph_data = generate_player_graph_data(stats)
    return jsonify(graph_data), 200

@main.route('/team/graph/histogram', methods=['GET'])
def team_histogram():
    """Retorna os dados do histograma de vitórias e derrotas do time."""
    team_stats = get_team_stats()
    graph_data = generate_histogram_data(team_stats)
    return jsonify(graph_data), 200

@main.route('/team/graph/radar', methods=['GET'])
def team_radar():
    """Retorna os dados do gráfico de radar do time."""
    team_stats = get_team_stats()
    graph_data = generate_radar_chart_data(team_stats)
    return jsonify(graph_data), 200

@main.route('/player/<int:player_id>/graph/boxplot', methods=['GET'])
def player_boxplot(player_id):
    """Retorna os dados do boxplot do jogador."""
    stats = get_player_stats(player_id)
    
    if "error" in stats:
        return jsonify(stats), 404

    graph_data = generate_boxplot_data(stats)
    return jsonify(graph_data), 200

@main.route('/team/graph/pie', methods=['GET'])
def team_pie_chart():
    """Retorna os dados do gráfico de pizza do time."""
    team_stats = get_team_stats()
    graph_data = generate_pie_chart_data(team_stats)
    return jsonify(graph_data), 200

@main.route('/player/<int:player_id>/graph/scatter', methods=['GET'])
def player_scatter(player_id):
    """Retorna os dados do gráfico de dispersão do jogador."""
    stats = get_player_stats(player_id)
    
    if "error" in stats:
        return jsonify(stats), 404

    graph_data = generate_scatter_plot_data(stats)
    return jsonify(graph_data), 200

### 📌 RF10.1 - Criar Dashboard interativo com gráficos e estatísticas
@main.route('/dashboard', methods=['GET'])
def dashboard():
    """Renderiza um dashboard interativo com gráficos e estatísticas do time e dos jogadores."""
    return render_template("dashboard.html")
