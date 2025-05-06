#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh

function increase_size() {
    local cluster_name=$1
    local node_group_name=$2
    local min_size=$3
    local max_size=$4
    local desired_size=$5
    local region=$6

    if [[ -z "$cluster_name" || -z "$node_group_name" || -z "$min_size" || -z "$max_size" || -z "$desired_size" || -z "$region" ]]; then
        echo "Error: Missing arguments."
        echo "Usage: $0 cluster_name, node group name, min size, max size, desired size, region."
        exit 1
    fi

    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed."
        exit 2
    fi

    output=$(aws eks update-nodegroup-config --cluster-name "$cluster_name" --nodegroup-name "$node_group_name" --scaling-config minSize="$min_size",maxSize="$max_size",desiredSize="$desired_size" --region "$region" 2>&1)
    status=$?

    if [[ $status -ne 0 ]]; then
        echo "Error: Failed to update Auto Scaling group."
        echo "Output: $output"
        exit $status
    else
        echo "Successfully updated node group '$node_group_name' in cluster '$cluster_name' with max size $max_size , min size $min_size , and desired size $desired_size in region $region."         
    fi
}

increase_size "$1" "$2" "$3" "$4" "$5" "$6"
