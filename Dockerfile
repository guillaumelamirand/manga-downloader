# Pull base image.
FROM ubuntu:latest

# Environment variables
ENV WORK_DIR='/mangas-downloader'
ENV CONFIG_FILE='$WORK_DIR/config.yml'
ENV CRON_PERIOD='0 \*\/6 \* \* \*'

# Create the pseudo log file to point to stdout
RUN ln -sf /proc/1/fd/1 /var/log/mangas-downloader.log

# Add crontab file in the working directory
ADD \ 
  cron/crontab.template $WORK_DIR/crontab.template
ADD \
  cron/run.sh $WORK_DIR/run.sh

# Add entrypoint
ADD \
  docker/entrypoint.sh $WORK_DIR/entrypoint.sh 

# Allow execution on script
RUN \
  chmod +x $WORK_DIR/*.sh

# Add python files
ADD \ 
  sources $WORK_DIR/

# Install apt dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get upgrade -y && \
  apt-get install -y \ 
    calibre \
    python-pip \
    cron
    
# Clean apt
RUN \    
  rm -rf /var/lib/apt/lists/*

# Install python dependencies
RUN \
  pip install -r $WORK_DIR/requirements.txt --no-cache-dir
  
# Run the command on container startup
ENTRYPOINT \
  $WORK_DIR/entrypoint.sh
