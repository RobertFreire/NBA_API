from nba_api.stats.endpoints import PlayerGameLog

# Defina o ID do jogador e a temporada
player_id = 203507  # Substitua pelo ID do jogador que deseja testar
season = "2024-25"  # Temporada atual

# Tente obter os jogos do jogador
try:
    game_logs = PlayerGameLog(player_id=player_id, season=season, timeout=120).get_data_frames()
    
    if game_logs and not game_logs[0].empty:
        print("✅ Dados encontrados! Exibindo as primeiras linhas:")
        print(game_logs[0].head())  # Exibir apenas as primeiras linhas
    else:
        print(f"⚠️ Nenhum jogo encontrado para o jogador {player_id} na temporada {season}.")
except Exception as e:
    print(f"❌ Erro ao buscar dados: {str(e)}")
