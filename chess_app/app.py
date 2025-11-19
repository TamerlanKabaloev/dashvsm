from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chess-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Хранилище игр
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game/<game_id>')
def game(game_id):
    return render_template('game.html', game_id=game_id)

@socketio.on('create_game')
def handle_create_game():
    game_id = str(uuid.uuid4())[:8]
    games[game_id] = {
        'white': request.sid,
        'black': None,
        'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
        'moves': [],
        'status': 'waiting'
    }
    join_room(game_id)
    emit('game_created', {'game_id': game_id, 'color': 'white'})
    emit('game_info', {
        'fen': games[game_id]['fen'],
        'status': games[game_id]['status'],
        'color': 'white'
    })

@socketio.on('join_game')
def handle_join_game(data):
    game_id = data.get('game_id')
    if game_id in games:
        game = games[game_id]
        if game['black'] is None and game['white'] != request.sid:
            game['black'] = request.sid
            game['status'] = 'active'
            join_room(game_id)
            emit('game_joined', {'color': 'black'})
            emit('game_info', {
                'fen': game['fen'],
                'status': game['status'],
                'color': 'black'
            }, room=game_id)
            socketio.emit('player_joined', {'color': 'black'}, room=game_id)
        elif game['white'] == request.sid:
            join_room(game_id)
            emit('game_joined', {'color': 'white'})
            emit('game_info', {
                'fen': game['fen'],
                'status': game['status'],
                'color': 'white'
            })
        else:
            emit('error', {'message': 'Комната заполнена'})
    else:
        emit('error', {'message': 'Игра не найдена'})

@socketio.on('make_move')
def handle_move(data):
    game_id = data.get('game_id')
    move = data.get('move')
    fen = data.get('fen')
    
    if game_id in games:
        games[game_id]['fen'] = fen
        games[game_id]['moves'].append(move)
        socketio.emit('move_made', {
            'move': move,
            'fen': fen
        }, room=game_id)

@socketio.on('disconnect')
def handle_disconnect():
    # Удаляем игрока из игр при отключении
    for game_id, game in list(games.items()):
        if game['white'] == request.sid or game['black'] == request.sid:
            socketio.emit('player_disconnected', room=game_id)
            if game['status'] == 'waiting':
                del games[game_id]
            break

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

