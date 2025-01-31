from app.services import get_team_stats, get_player_stats
from app.graphs import generate_team_graph, generate_player_graph

# Testando gráfico do time
team_stats = get_team_stats()
team_graph_path = generate_team_graph(team_stats)
print(f"✅ Gráfico do time salvo em: {team_graph_path}")

# Testando gráfico do jogador
player_name = "Brandon Ingram"
player_stats = get_player_stats(player_name)
player_graph_path = generate_player_graph(player_stats, player_name)
print(f"✅ Gráfico do jogador salvo em: {player_graph_path}")
