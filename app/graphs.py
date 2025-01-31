import os
import matplotlib
matplotlib.use('Agg')  # Usa backend sem interface gráfica
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Diretório onde os gráficos serão salvos
GRAPH_DIR = os.path.join(os.getcwd(), "static/graphs")

# Criando o diretório se ele não existir
os.makedirs(GRAPH_DIR, exist_ok=True)

### 📊 GRÁFICO DE BARRAS (Vitórias x Derrotas) ###
def generate_team_graph(team_stats):
    """Gera um gráfico de barras do desempenho do time na temporada."""
    df = pd.DataFrame(team_stats)

    plt.figure(figsize=(8, 5))
    plt.bar(["Vitórias", "Derrotas"], [df["W"][0], df["L"][0]], color=['green', 'red'])
    plt.xlabel("Resultados")
    plt.ylabel("Quantidade")
    plt.title("Vitórias x Derrotas - New Orleans Pelicans")

    file_path = os.path.join(GRAPH_DIR, "team_performance.png")
    plt.savefig(file_path)
    plt.close()
    
    return file_path

### 📈 GRÁFICO DE LINHA (Evolução dos pontos do jogador) ###
def generate_player_graph(player_stats, player_name):
    """Gera um gráfico de linha para evolução dos pontos do jogador."""
    df = pd.DataFrame(player_stats)

    plt.figure(figsize=(8, 5))
    plt.plot(df["SEASON_ID"], df["PTS"], marker='o', linestyle='-', color='blue', label="Pontos")
    plt.xlabel("Temporada")
    plt.ylabel("Pontos")
    plt.title(f"Evolução dos Pontos - {player_name}")
    plt.xticks(rotation=45)
    plt.legend()

    file_path = os.path.join(GRAPH_DIR, f"{player_name.replace(' ', '_')}_points.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

def generate_histogram(team_stats):
    """Gera um histograma da frequência de vitórias e derrotas."""
    df = pd.DataFrame(team_stats)

    plt.figure(figsize=(8, 5))
    
    # Criando o histograma corretamente
    plt.bar(["Vitórias", "Derrotas"], [df["W"][0], df["L"][0]], color=['green', 'red'], alpha=0.7)
    
    plt.xlabel("Resultado")
    plt.ylabel("Frequência")
    plt.title("Histograma de Vitórias e Derrotas - New Orleans Pelicans")

    file_path = os.path.join(GRAPH_DIR, "histogram_wins_losses.png")
    plt.savefig(file_path)
    plt.close()
    
    return file_path


### 📈 GRÁFICO DE RADAR (Comparação de Estatísticas do Time) ###
def generate_radar_chart(team_stats):
    """Gera um gráfico de radar para comparar estatísticas do time."""
    df = pd.DataFrame(team_stats)
    
    labels = ["Pontos", "Assistências", "Rebotes", "Roubos", "Tocos"]
    stats = [df["PTS"][0], df["AST"][0], df["REB"][0], df["STL"][0], df["BLK"][0]]
    
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats += stats[:1]  # Fechar o círculo
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='blue', alpha=0.3)
    ax.plot(angles, stats, color='blue', linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_title("Radar Chart - Estatísticas do Time")

    file_path = os.path.join(GRAPH_DIR, "radar_chart_team.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

### 📉 BOXPLOT (Distribuição de Estatísticas do Jogador) ###
def generate_boxplot(player_stats, player_name):
    """Gera um boxplot para distribuição de pontos, assistências e rebotes do jogador."""
    df = pd.DataFrame(player_stats)

    plt.figure(figsize=(8, 5))
    plt.boxplot([df["PTS"], df["AST"], df["REB"]], labels=["Pontos", "Assistências", "Rebotes"])
    plt.ylabel("Valores")
    plt.title(f"Boxplot - {player_name}")

    file_path = os.path.join(GRAPH_DIR, f"{player_name.replace(' ', '_')}_boxplot.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

### 📊 GRÁFICO DE PIZZA (Percentual de Vitórias e Derrotas) ###
def generate_pie_chart(team_stats):
    """Gera um gráfico de pizza para mostrar a proporção de vitórias e derrotas."""
    df = pd.DataFrame(team_stats)
    
    labels = ["Vitórias", "Derrotas"]
    sizes = [df["W"][0], df["L"][0]]
    colors = ['green', 'red']

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title("Proporção de Vitórias e Derrotas")

    file_path = os.path.join(GRAPH_DIR, "pie_chart_wins_losses.png")
    plt.savefig(file_path)
    plt.close()

    return file_path

### 🔵 GRÁFICO DE DISPERSÃO (FG% vs. Pontos do Jogador) ###
def generate_scatter_plot(player_stats, player_name):
    """Gera um gráfico de dispersão relacionando FG% com Pontos."""
    df = pd.DataFrame(player_stats)

    plt.figure(figsize=(8, 5))
    plt.scatter(df["FG_PCT"], df["PTS"], color='blue', alpha=0.6)
    plt.xlabel("Aproveitamento de Arremessos (FG%)")
    plt.ylabel("Pontos")
    plt.title(f"Dispersão FG% vs Pontos - {player_name}")

    file_path = os.path.join(GRAPH_DIR, f"{player_name.replace(' ', '_')}_scatter.png")
    plt.savefig(file_path)
    plt.close()

    return file_path
