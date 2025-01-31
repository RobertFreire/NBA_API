import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Diretório dos dados CSV
DATA_DIR = os.path.join(os.getcwd(), "data")

def convert_numpy_to_python(obj):
    """Converte numpy.float32 e numpy.int64 para tipos nativos do Python."""
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    return obj

def train_player_model(player_name):
    """Treina um modelo de Machine Learning para prever a pontuação futura de um jogador."""
    file_path = os.path.join(DATA_DIR, f"{player_name.replace(' ', '_')}.csv")
    
    if not os.path.exists(file_path):
        return {"error": "Arquivo de estatísticas do jogador não encontrado."}

    df = pd.read_csv(file_path)

    # 🔹 Criar feature de Pontos por Jogo (PTS por GP)
    df["PTS_per_game"] = df["PTS"] / df["GP"]

    # 🔹 Debug: Verificando quantas temporadas temos
    print(f"\n📊 Número de temporadas disponíveis para {player_name}: {len(df)}")
    
    if len(df) < 5:
        print("⚠️ Poucos dados! O modelo pode não aprender corretamente.")
        return {"error": "Dados insuficientes para treinar o modelo."}

    # 🔹 Selecionar as melhores features
    features = ["FG_PCT", "FG3_PCT", "FT_PCT", "REB", "AST", "GP"]
    target = "PTS_per_game"

    # 🔹 Criar novas features
    df["SCORING_EFF"] = df["FG_PCT"] * df["PTS_per_game"]
    df["USAGE"] = (df["PTS"] + df["AST"]) / df["GP"]

    # 🔹 Criar médias móveis para suavizar oscilações
    for window in [2, 3, 5]:
        df[f"PTS_MA_{window}"] = df["PTS_per_game"].rolling(window=window, min_periods=1).mean()
        df[f"FG_PCT_MA_{window}"] = df["FG_PCT"].rolling(window=window, min_periods=1).mean()

    # 🔹 Lista final de features
    feature_columns = features + ["SCORING_EFF", "USAGE"] + [col for col in df.columns if "MA_" in col]

    # 🔹 Tratamento de valores faltantes (Correção do Warning)
    df = df.ffill().bfill()

    # 🔹 Debug: Estatísticas dos pontos
    print("\n📊 Estatísticas dos pontos por jogo:")
    print(df["PTS_per_game"].describe())

    if df["PTS_per_game"].std() < 1e-2:  # Se o desvio padrão for muito baixo
        print("⚠️ Pouca variação nos pontos! O modelo pode ter dificuldade para prever.")
        return {"error": "Os dados do jogador têm pouca variação, o que pode afetar a previsão."}

    # 🔹 Separação entre variáveis independentes (X) e dependente (y)
    X = df[feature_columns]
    y = df[target]

    # 🔹 Normalização dos dados
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 🔹 Debug: Mostrar amostra dos dados normalizados
    print("\n📊 Amostra dos dados normalizados (primeiras 5 linhas):")
    print(pd.DataFrame(X_scaled, columns=feature_columns).head())

    # 🔹 Modelos com hiperparâmetros ajustados
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_split=5, min_samples_leaf=2, random_state=42)
    xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=4, min_child_weight=2, random_state=42)

    # 🔹 Cross-validation para avaliar o modelo
    kf = KFold(n_splits=min(5, len(df) - 1), shuffle=True, random_state=42)
    mae_scores, mse_scores, r2_scores = [], [], []

    for train_idx, test_idx in kf.split(X_scaled):
        X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        
        rf_model.fit(X_train, y_train)
        xgb_model.fit(X_train, y_train)

        y_pred_rf = rf_model.predict(X_test)
        y_pred_xgb = xgb_model.predict(X_test)
        y_pred = (y_pred_rf + y_pred_xgb) / 2

        mae_scores.append(mean_absolute_error(y_test, y_pred))
        mse_scores.append(mean_squared_error(y_test, y_pred))

        # 🔹 Evita erro de R² NaN verificando a variabilidade de y_test
        if np.var(y_test) > 0:
            r2_scores.append(r2_score(y_test, y_pred))
        else:
            r2_scores.append(None)  # Evita erro dividindo por zero
    
    # 🔹 Remover valores None antes de calcular a média do R²
    r2_scores = [r for r in r2_scores if r is not None]
    r2_mean = np.mean(r2_scores) if len(r2_scores) > 0 else "Variância muito baixa"

    # 🔹 Fazer a previsão da próxima temporada
    last_season_df = pd.DataFrame([df.iloc[-1][feature_columns]], columns=feature_columns)  # Mantém os nomes das colunas
    last_season_scaled = scaler.transform(last_season_df)
    
    next_season_pred = (
        rf_model.predict(last_season_scaled)[0] + 
        xgb_model.predict(last_season_scaled)[0]
    ) / 2

    # 🔹 Converter previsão de pontos por jogo para pontos totais
    predicted_total_points = next_season_pred * df["GP"].mean()

    # 🔹 Debug: Exibir previsão final
    print(f"\n📊 Previsão Final para {player_name}: {predicted_total_points:.2f} pontos na próxima temporada")

    return {
        "Jogador": player_name,
        "Previsão de Pontos na Próxima Temporada": convert_numpy_to_python(predicted_total_points),
        "Erro Médio Absoluto (MAE)": convert_numpy_to_python(np.mean(mae_scores)),
        "Erro Quadrático Médio (MSE)": convert_numpy_to_python(np.mean(mse_scores)),
        "R² (Coeficiente de Determinação)": convert_numpy_to_python(r2_mean)
    }
