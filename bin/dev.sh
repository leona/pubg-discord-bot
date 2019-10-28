DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -o allexport
source $DIR/../.env
set +o allexport
DISCORD_TOKEN=$DISCORD_TOKEN_REPORTER DISCORD_TOKEN_MANAGER=$DISCORD_TOKEN_MANAGER PUBG_KEY=$PUBG_KEY DEBUG_SERVER_ID=$DEBUG_SERVER DEBUG=true python3 $DIR/../report.py
