#!/bin/bash
set -e

# Run cron with foreground mode
echo "Run with "
echo "  - WORK_DIR=$WORK_DIR"
echo "  - CRON_PERIOD=$CRON_PERIOD"
echo "  - CONFIG_FILE=$CONFIG_FILE"

# Start the run once job.
echo "Setup cron job"
# Update a cron schedule
cp $WORK_DIR/crontab.template $WORK_DIR/crontab
sed -i -e "s|@CRON_PERIOD@|$CRON_PERIOD|" $WORK_DIR/crontab
sed -i -e "s|@WORK_DIR@|$WORK_DIR|" $WORK_DIR/crontab
sed -i -e "s|@CONFIG_FILE@|$CONFIG_FILE|" $WORK_DIR/crontab
# Update permission
chown -R mangas.mangas $WORK_DIR/crontab
chmod 0644 $WORK_DIR/crontab
# Update cron as mangas
crontab -u mangas $WORK_DIR/crontab

# Run cron with foreground mode
echo "Run cron"
exec cron -f -L 7