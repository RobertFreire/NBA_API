import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Diretório dos dados CSV
DATA_DIR = os.path.join(os.getcwd(), "data")

def train_player_model(player_name):
    """Treina um modelo de Machine Learning para prever a pontuação futura de um jogador."""
    file_path = os.path.join(DATA_DIR, f"{player_name.replace(' ', '_')}.csv")

    if not os.path.exists(file_path):
        return {"error": "Arquivo de estatísticas do jogador não encontrado."}

    df = pd.read_csv(file_path)

    # 🔹 Verificar colunas disponíveis
    available_features = [col for col in ["FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST"] if col in df.columns]
    target = "PTS"

    if target not in df.columns:
        return {"error": "A coluna PTS não está disponível no CSV."}

    if len(available_features) < 3:
        return {"error": "Dados insuficientes para treinar o modelo."}

    # 🔹 Criar novas features (médias móveis)
    df["PTS_rolling"] = df["PTS"].rolling(window=3, min_periods=1).mean()
    df["REB_rolling"] = df["REB"].rolling(window=3, min_periods=1).mean()
    df["AST_rolling"] = df["AST"].rolling(window=3, min_periods=1).mean()

    feature_columns = available_features + ["PTS_rolling", "REB_rolling", "AST_rolling"]

    # 🔹 Remover temporadas com dados ausentes
    df = df.dropna(subset=feature_columns + [target])

    if len(df) < 5:
        return {"error": "Dados insuficientes para treinar o modelo."}

    # 🔹 Separando variáveis independentes (X) e dependente (y)
    X = df[feature_columns]
    y = df[target]

    # 🔹 Normalizar os dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 🔹 Dividir dados em treino (80%) e teste (20%)
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # 🔹 Criando o modelo de XGBoost
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    # 🔹 Avaliando o modelo
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # 🔹 Pegando os últimos valores conhecidos para prever a próxima temporada
    last_season = df.iloc[-1][feature_columns].values.reshape(1, -1)
    last_season_scaled = scaler.transform(last_season)
    next_season_prediction = model.predict(last_season_scaled)[0]

    return {
        "Jogador": player_name,
        "Previsão de Pontos na Próxima Temporada": round(next_season_prediction, 2),
        "Erro Médio Absoluto (MAE)": round(mae, 2),
        "Erro Quadrático Médio (MSE)": round(mse, 2),
        "R² (Coeficiente de Determinação)": round(r2, 2)
    }
