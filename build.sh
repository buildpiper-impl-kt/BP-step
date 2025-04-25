#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh

function archive_name() {
     local path_of_file=$1

     if [ -z "$path_of_file" ]; then
        echo "Path is empty. Please provide a valid path." 

     else 
        if [ -e "$path_of_file" ]; then
            archive_name=$(basename "$path_of_file")_$(date +%Y%m%d%H%M%S).tar.gz
            tar -czvf "/data/$archive_name" "$path_of_file"
            echo "File successfully zipped as: $archive_name"
        else
            echo "Error: Path does not exist."
        fi
    fi
}

archive_name "$1"
