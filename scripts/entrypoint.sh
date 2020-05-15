#!/bin/bash
set -e

# Run immediate
echo "First run"
${WORK_DIR}/run.sh > /var/log/mangas-downloader.log 2>&1

# Start the run once job.
CRON_FILE=/etc/cron.d/mangas_downloader
echo "Setup cron job with"
echo "  - CRON_FILE=${CRON_FILE}"
echo "  - CRON_PERIOD=${CRON_PERIOD}"
mkdir -p /etc/cron.d
echo -e "WORK_DIR=${WORK_DIR}\n\
CONFIG_FILE=${CONFIG_FILE}\n\
${CRON_PERIOD} root ${WORK_DIR}/run.sh > /var/log/mangas-downloader.log 2>&1\n" > ${CRON_FILE}
chmod 0644 ${CRON_FILE}

# Run cron with foreground mode
echo "Run cron in foreground mode"
exec cron -f -L 7