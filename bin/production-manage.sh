DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -o allexport
source $DIR/../.env
set +o allexport
SUPER_USER_ID=$SUPER_USER_ID DISCORD_TOKEN=$DISCORD_TOKEN_REPORTER DISCORD_TOKEN_MANAGER=$DISCORD_TOKEN_MANAGER PUBG_KEY=$PUBG_KEY DEBUG_SERVER_ID=$DEBUG_SERVER python3.7 $DIR/../manage.py
