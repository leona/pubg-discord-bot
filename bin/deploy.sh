DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -o allexport
source $DIR/../.env
set +o allexport

# Deploy files
ssh $DEPLOY_USER@$DEPLOY_HOST rm -rf $DEPLOY_PATH
scp -r ./ $DEPLOY_USER@${DEPLOY_HOST}:$DEPLOY_PATH

# Delete & Add crontabs
#ssh $DEPLOY_USER@$DEPLOY_HOST crontab -r
#ssh $DEPLOY_USER@$DEPLOY_HOST touch /var/spool/cron/crontabs/root
#echo "@reboot ${DEPLOY_PATH}/bin/production.sh"
#ssh $DEPLOY_USER@$DEPLOY_HOST sudo echo "@reboot /bin/bash ${DEPLOY_PATH}/bin/production.sh" | tee -a /var/spool/cron/crontabs

# Reboot
#ssh $DEPLOY_USER@$DEPLOY_HOST reboot now
