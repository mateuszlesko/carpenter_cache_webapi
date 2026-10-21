#!/bin/bash

input_params="$@"
APP_NAME="carpenter_cache_webapi"

if [[ "$input_params" == *"--help"* ]]; then
    echo "Usage: ./build_run.sh [--help] [--no-cache]"
    echo "Options:"
    echo "  --help : Show this help message"
    echo "  --run : Build the Docker images and run the containers"
    echo "  prod : Build the production Docker images"
    echo "  dev : Build the devlopment Docker images"
    echo "  --export Export the Docker image as archive"

fi

if [[ "$input_params" == *"--run"* ]]; then
    FOUND_IMAGE=$(docker image ls | awk '$1 ~/^carpenter_cache_webapi/ {print $3}')
    echo "$FOUND_IMAGE"
    docker compose down

    if [[ -n "$FOUND_IMAGE" ]]; then
        echo "found image of $APP_NAME \n"
        docker image rm "$FOUND_IMAGE"
        echo "image of $APP_NAME successfuly deleted \n"
    fi

    if [[ "$input_params" == *"prod"* ]]; then
        export CACHE_WEB_API_RELEASE_TYPE="prod"
    fi
    if [[ "$input_params" == *"dev"* ]]; then
        export CACHE_WEB_API_RELEASE_TYPE="dev"
    fi

    if [[ "$input_params" == *"--no-cache"* ]]; then
        docker compose --env-file .env up --build --no-cache
    else
        docker compose --env-file .env up --build
    fi
    
fi


if [[ "$input_params" == *"--export"* ]]; then
    docker save "${APP_NAME}:latest" redis | gzip > $APP_NAME.tar.gz
    echo "$APP_NAME.tar.gz successfully exported"
fi


