# Pull base image.
FROM ubuntu:latest

# Install
ENV DEBIAN_FRONTEND noninteractive
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get upgrade -y -qq && \
  apt-get install -y -qq \ 
    calibre \
    cron

# Clean apt
RUN \    
  rm -rf /var/lib/apt/lists/*

# Environment variables
ENV WORK_DIR="/manga-process"
ENV CONFIG_FILE="$WORK_DIR/config.yaml"
ENV CRON_PERIOD="0 \*\/6 \* \* \*"

# Add crontab file in the working directory
ADD \ 
  cron/crontab $WORK_DIR/crontab
ADD \
  cron/run.sh $WORK_DIR/run.sh

# Add entrypoint
ADD \
  docker/entrypoint.sh $WORK_DIR/entrypoint.sh 

# Allow execution on script
RUN \
  chmod +x $WORK_DIR/*.sh

# Run the command on container startup
ENTRYPOINT \
  $WORK_DIR/entrypoint.sh
