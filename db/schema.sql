CREATE TABLE IF NOT EXISTS chess_game(
   completion_date    TEXT               NOT NULL,
   is_draw            INT                NOT NULL,
   n_moves            INT                NOT NULL,
   winner             TEXT,
   pgn                TEXT               NOT NULL
);
