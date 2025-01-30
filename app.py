from flask import Flask, jsonify
from services import get_team_data, get_nba_standings

app = Flask(__name__)

TEAM_ID = 1610612740

# TODO: Procurar ids dos jogadores
PLAYER_IDS = {
    'Brandon Boston Jr': 1,
    'Brandon Ingram': 2,
    'Yves Missi': 3,
}

@app.route('/nba_teams_all', methods=['GET'])
def nba_teams_all():
    """
    RF1: Lista todos os times da NBA agrupados por Conferência
    RF2: Apresenta classificação atual dos times
    """
    eastern, western = get_nba_standings()
    return jsonify({
        'Conferência Leste': eastern[['TeamID', 'TeamName', 'WINS', 'LOSSES']].to_dict(orient='records'),
        'Conferência Oeste': western[['TeamID', 'TeamName', 'WINS', 'LOSSES']].to_dict(orient='records')
    })



if __name__ == '__main__':
    app.run(debug=True)