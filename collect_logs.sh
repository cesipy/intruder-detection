#!/bin/sh 

LOGS_DEST_DIR="res/collected_logs"
CONTAINER_LOGS_DIR="/app/logs"

mkdir -p $LOGS_DEST_DIR
# if there are any logs, delete them. 
rm -rf $LOGS_DEST_DIR/*

# Get all containers (including stopped ones)
containers=$(docker ps -aq)      # -a includes stopped containers, -q for quiet mode (IDs only)

for cont in $containers; do
    echo "Processing container: $cont"
    mkdir -p "$LOGS_DEST_DIR/$cont"

    # Add error handling for the copy operation
    if docker cp "$cont:$CONTAINER_LOGS_DIR/." "$LOGS_DEST_DIR/$cont/"; then
        echo "Successfully copied logs from container $cont"
    else
        echo "Failed to copy logs from container $cont"
    fi
done