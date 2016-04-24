$(document).ready(function() {
    var board = ChessBoard('chessboard', {
        pieceTheme: 'static/img/chesspieces/wikipedia/{piece}.png'
    });

    $(window).resize(board.resize);

    handleSocketMessages(board);
});

function handleSocketMessages(board) {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connection_established', function(msg) {
        if (msg.game_over) {
            $('#current-game-header').text("Game #" + msg.game_id + " Complete");
        } else {
            $('#current-game-header').text("Game #" + msg.game_id + " In Progress");
        }

        update(board, msg);
    });

    socket.on('move', function(msg) {
        $('#current-game-header').text("Game #" + msg.game_id + " In Progress");
        update(board, msg);
    });
    
    socket.on('game_over', function(msg) {
        $('#current-game-header').text("Game #" + msg.game_id + " Complete");
        update(board, msg);
    });
}

function update(board, msg) {
    board.position(msg.fen);
    $('#n_games').text("Games: " + msg.n_games);
    $('#n_white_wins').text("White wins: " + msg.n_white_wins);
    $('#n_black_wins').text("Black wins: " + msg.n_black_wins);
    $('#n_draws').text("Draws: " + msg.n_draws);
    $('#n_moves').text("Moves: " + msg.n_moves);
    $('#n_game_moves').text("Moves: "+ msg.n_game_moves );
    $('#turn').text("Turn: " + msg.turn);
}