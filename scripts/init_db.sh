#!/usr/bin/env bash

set -e
set -u

echo "Creating database."
python3 -c "from eternal_chess.eternal_chess import init_db; init_db()"
echo "Database created."
