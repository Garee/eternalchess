$(document).ready(function() {
    var board = ChessBoard('chessboard', {
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    });

    $(window).resize(board.resize);

    var pgn = $('#pgn').text();
    var game = new Chess();
    game.load_pgn(pgn);
    
    var moves = game.history();
    handleMoves(moves, board);
});

function handleMoves(moves, board) {
    var game = new Chess();
    var move_idx = 0;
    
    $('#start-btn').click(function() {
        game.reset();
        board.position(game.fen());
        move_idx = 0;
        
        $(this).attr('disabled', true);
        $('#prev-btn').attr('disabled', true);
        $('#next-btn').attr('disabled', false);
        $('#end-btn').attr('disabled', false);
    });

    $('#prev-btn').click(function() {
        move_idx--;
        game.undo();
        board.position(game.fen());

        if (move_idx === 0) {
            $('#start-btn').attr('disabled', true);
            $(this).attr('disabled', true);
        }
        
        $('#next-btn').attr('disabled', false);
        $('#end-btn').attr('disabled', false);
    });

    $('#next-btn').click(function() {
        var move = moves[move_idx++];
        game.move(move);
        board.position(game.fen());

        if (move_idx === moves.length) {
            $(this).attr('disabled', true);
            $('#end-btn').attr('disabled', true);
        }

        $('#start-btn').attr('disabled', false);
        $('#prev-btn').attr('disabled', false);
    });

    $('#end-btn').click(function() {
        var pgn = $('#pgn').text();
        game.load_pgn(pgn);
        board.position(game.fen());
        move_idx = moves.length - 1;

        $('#start-btn').attr('disabled', false);
        $('#prev-btn').attr('disabled', false);
        $('#next-btn').attr('disabled', true);
        $(this).attr('disabled', true);
    });
}