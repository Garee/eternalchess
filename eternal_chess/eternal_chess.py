#!/usr/bin/env python

import time
import chess
import sqlite3
import eventlet
import threading
from random import randint
from chess.pgn import Game
from datetime import datetime
from contextlib import closing
from flask import Flask, g, render_template
from flask.ext.socketio import SocketIO, emit


# Necessary because we use background threads.
eventlet.monkey_patch()

DATE_FORMAT = '%H:%M:%S %d-%m-%Y'

app = Flask(__name__)
app.config.from_envvar('ETERNAL_CHESS_CFG')

socketio = SocketIO(app)

board = chess.Board()


def init_db():
    """Create the sqlite3 database using the configured schema file."""
    with closing(connect_db()) as db:
        with app.open_resource(app.config['SCHEMA_FILE'], mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    """Return an established sqlite3 database connection."""
    return sqlite3.connect(app.config['DATABASE'])


def get_db():
    """Return or create an established sqlite3 database connection."""
    db = getattr(g, 'db', None)
    if not db:
        db = g.db = connect_db()
    return db


@app.before_request
def before_request():
    """Establish a database connection."""
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """Close the established database connection."""
    db = getattr(g, 'db', None)
    if db:
        db.close()


def query_db(query, args=(), one=False):
    """Return the result of a database query."""
    with app.app_context():
        cur = get_db().execute(query, args)
        rs = cur.fetchall()
        cur.close()
        return (rs[0] if rs else None) if one else rs


def exec_db(query, args):
    """Execute an SQL statement on the configured database."""
    with app.app_context():
        get_db().execute(query, args)
        get_db().commit()


def get_all_chess_games():
    games = []
    query = 'SELECT * FROM chess_game'
    for row in query_db(query):
        completion_date, is_draw, n_moves, winner, pgn = row
        games.append({
            'completion_date': datetime.strptime(completion_date, DATE_FORMAT),
            'is_draw': bool(is_draw),
            'n_moves': int(n_moves),
            'winner': winner,
            'pgn': pgn
        })
    return games


def insert_chess_game(completion_date, is_draw, n_moves, winner, pgn):
    """Add a row to chess_game."""
    query = ('INSERT INTO chess_game'
             '(completion_date, is_draw, n_moves, winner, pgn)'
             'VALUES (?, ?, ?, ?, ?)')
    args = [completion_date, is_draw, n_moves, winner, pgn]
    exec_db(query, args)


def get_n_of_games():
    """Return the number of completed games in the database."""
    with app.app_context():
        query = 'SELECT COUNT(*) FROM chess_game'
        result = query_db(query, one=True)[0]
        return int(result)


def get_n_white_wins():
    """Return the number of white chess game wins in the database."""
    with app.app_context():
        query = 'SELECT COUNT(*) FROM chess_game WHERE winner = "white"'
        result = query_db(query, one=True)[0]
        return int(result)


def get_n_black_wins():
    """Return the number of black chess game wins in the database."""
    with app.app_context():
        query = 'SELECT COUNT(*) FROM chess_game WHERE winner = "black"'
        result = query_db(query, one=True)[0]
        return int(result)


def get_n_draws():
    """Return the number of chess game draws in the database."""
    with app.app_context():
        query = 'SELECT COUNT(*) FROM chess_game WHERE is_draw = 1'
        result = query_db(query, one=True)[0]
        return int(result)


def get_total_moves():
    """Return the total number of chess moves made in the database."""
    with app.app_context():
        query = 'SELECT TOTAL(n_moves) FROM chess_game'
        result = query_db(query, one=True)[0]
        return int(result)


def play_chess():
    """Repeatedly play games of chess and record their results."""
    global board
    if board.is_game_over():
        record_result(board)
        socketio.emit('game_over', get_state())
        time.sleep(app.config['SLEEP_INTERVAL_SEC'])
        board.reset()
    moves = list(board.legal_moves)
    move = moves[randint(0, len(moves) - 1)]
    board.push(move)
    socketio.emit('move', get_state())
    interval = app.config['MOVE_INTERVAL_SEC']
    threading.Timer(interval, play_chess).start()


def record_result(board):
    """Add a chess game result to the database."""
    completion_date = datetime.now().strftime(DATE_FORMAT)
    is_draw = 1 if board.result() == '1/2-1/2' else 0
    n_moves = board.fullmove_number
    winner = 'white' if board.result() == '1-0' else 'black'
    if is_draw:
        winner = None
    pgn = configure_pgn(board)
    insert_chess_game(completion_date, is_draw, n_moves, winner, pgn)


def configure_pgn(board):
    """Return a PGN representation of a completed chess game."""
    pgn = Game.from_board(board)
    pgn.headers['Event'] = 'Eternal Chess'
    pgn.headers['Site'] = 'www.eternalchess.com'
    pgn.headers['Date'] = datetime.now().strftime(DATE_FORMAT)
    pgn.headers['Round'] = str(int(get_n_of_games()) + 1)
    pgn.headers['White'] = 'Random'
    pgn.headers['Black'] = 'Random'
    return str(pgn)


def get_state():
    """Return statistics for all chess games."""
    return {
        'fen': board.fen(),
        'n_games': get_n_of_games(),
        'n_white_wins': get_n_white_wins(),
        'n_black_wins': get_n_black_wins(),
        'n_draws': get_n_draws(),
        'n_moves': get_total_moves() + board.fullmove_number,
        'game_id': str(int(get_n_of_games()) + 1),
        'n_game_moves': board.fullmove_number,
        'turn': "White" if board.turn else "Black",
        'game_over': board.is_game_over()
    }


@socketio.on('connect')
def test_connect():
    app.logger.info("Client connected.")
    emit('connection_established', get_state())


@socketio.on('disconnect')
def test_disconnect():
    app.logger.info("Client disconnected.")


@app.route('/')
def index():
    """Serve the root page."""
    return render_template('index.html', **get_state())


@app.route('/games')
def games():
    """Serve the historical games page."""
    return render_template('games.html', games=get_all_chess_games())


@app.route('/about')
def about():
    """Serve the about page."""
    return render_template('about.html')


if __name__ == '__main__':
    play_chess()
    socketio.run(app, use_reloader=False)
