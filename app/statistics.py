import os
import pandas as pd
import numpy as np

# Diretório dos dados CSV
DATA_DIR = os.path.join(os.getcwd(), "data")

def convert_numpy_to_python(obj):
    """Converte objetos numpy (int64, float64, NaN) para tipos Python nativos."""
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if pd.isna(obj):  # Se for NaN, retorna None
        return None
    return obj

def safe_correlation(series1, series2):
    """Calcula a correlação de forma segura, evitando NaN."""
    if series1.nunique() <= 1 or series2.nunique() <= 1:
        return 0  # Se a coluna tem apenas um valor, não é possível calcular correlação
    correlation = series1.corr(series2)
    return float(correlation) if not pd.isna(correlation) else 0  # Se for NaN, retorna 0

def calculate_team_stats():
    """Calcula estatísticas descritivas do time a partir do arquivo CSV."""
    file_path = os.path.join(DATA_DIR, "team_stats.csv")
    
    if not os.path.exists(file_path):
        return {"error": "Arquivo de estatísticas do time não encontrado."}

    df = pd.read_csv(file_path)

    stats = {
        "Média de Pontos": df["PTS"].mean(),
        "Mediana de Pontos": df["PTS"].median(),
        "Desvio Padrão de Pontos": df["PTS"].std() if df["PTS"].nunique() > 1 else 0,
        "Máximo de Pontos": df["PTS"].max(),
        "Mínimo de Pontos": df["PTS"].min(),
        "Correlação PTS x Assistências": safe_correlation(df["PTS"], df["AST"]),
        "Correlação PTS x FG%": safe_correlation(df["PTS"], df["W_PCT"]),
    }

    # Substituir NaN por None para evitar erro no JSON
    return {key: convert_numpy_to_python(value) for key, value in stats.items()}

def calculate_player_stats(player_name):
    """Calcula estatísticas descritivas do jogador a partir do arquivo CSV."""
    file_path = os.path.join(DATA_DIR, f"{player_name.replace(' ', '_')}.csv")
    
    if not os.path.exists(file_path):
        return {"error": "Arquivo de estatísticas do jogador não encontrado."}

    df = pd.read_csv(file_path)

    stats = {
        "Média de Pontos": df["PTS"].mean(),
        "Mediana de Pontos": df["PTS"].median(),
        "Desvio Padrão de Pontos": df["PTS"].std() if df["PTS"].nunique() > 1 else 0,
        "Máximo de Pontos": df["PTS"].max(),
        "Mínimo de Pontos": df["PTS"].min(),
        "Correlação PTS x FG%": safe_correlation(df["PTS"], df["FG_PCT"]),
        "Correlação PTS x Rebotes": safe_correlation(df["PTS"], df["REB"]),
    }

    # Substituir NaN por None para evitar erro no JSON
    return {key: convert_numpy_to_python(value) for key, value in stats.items()}
