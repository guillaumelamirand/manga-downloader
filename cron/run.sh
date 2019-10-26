#!/bin/bash

echo -e "\n\n *** Start new execution : `date` ***"
calibre-debug $WORK_DIR/main.py -- $CONFIG_FILE
echo -e "\n\n *** End ***"