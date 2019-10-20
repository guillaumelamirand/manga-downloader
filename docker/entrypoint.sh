#!/bin/bash

# Start the run once job.
echo "Setup cron job"

# Update a cron schedule
cp $WORK_DIR/crontab /etc/cron.d/manga-process-cron
sed -i -e "s|@WORK_DIR@|$WORK_DIR|" /etc/cron.d/manga-process-cron
sed -i -e "s|@CONFIG_FILE@|$CONFIG_FILE|" /etc/cron.d/manga-process-cron
sed -i -e "s|@CRON_PERIOD@|$CRON_PERIOD|" /etc/cron.d/manga-process-cron
chmod 0644 /etc/cron.d/manga-process-cron
crontab /etc/cron.d/manga-process-cron

# Run cron with foreground mode
echo "Run cron"
cron -f