import os
import matplotlib
matplotlib.use('Agg')  # Usa backend sem interface gráfica
import matplotlib.pyplot as plt
import pandas as pd

# Diretório onde os gráficos serão salvos
GRAPH_DIR = os.path.join(os.getcwd(), "static/graphs")

# Criando o diretório se ele não existir
os.makedirs(GRAPH_DIR, exist_ok=True)

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
