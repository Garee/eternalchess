$(document).ready(function() {
    var board = ChessBoard('chessboard', {
        position: 'start',
        pieceTheme: 'static/img/chesspieces/wikipedia/{piece}.png'
    });

    $(window).resize(board.resize);

    handleSocketMessages(board);
});

function handleSocketMessages(board) {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('move', function(msg) {
        board.position(msg.fen);
        $('#n_moves').text("Moves: " + msg.n_moves);
        $('#current-game-header').text("Game #" + msg.game_id + " In Progress");
        $('#n_game_moves').text("Moves: "+ msg.n_game_moves );
    });
    
    socket.on('game_over', function(msg) {
        $('#n_games').text("GamesCompleted games: " + msg.n_games);
        $('#n_white_wins').text("White wins: " + msg.n_white_wins);
        $('#n_black_wins').text("Black wins: " + msg.n_black_wins);
        $('#n_draws').text("Draws: " + msg.n_draws);
        $('#n_moves').text("Moves: " + msg.n_moves);
        $('#current-game-header').text("Game #" + msg.game_id + " In Progress");
    });    
}
