#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh

function increase_size() {
    local asg_name=$1
    local asg_max_size=$2
    local region=$3

    if [[ -z "$asg_name" || -z "$asg_max_size" || -z "$region" ]]; then
        echo "Error: Missing arguments."
        echo "Usage: $0 asg name, asg size, region."
        exit 1
    fi

    if ! command -v aws &> /dev/null; then
        echo "Error: AWS CLI is not installed."
        exit 2
    fi

    output=$(aws autoscaling update-auto-scaling-group --auto-scaling-group-name "$asg_name" --max-size "$asg_max_size" --region "$region" 2>&1)
    status=$?

    if [[ $status -ne 0 ]]; then
        echo "Error: Failed to update Auto Scaling group."
        echo "Output: $output"
        exit $status
    else
        echo "Successfully updated auto scaling group $asg_name with max size $asg_max_size in region $region."
    fi
}

increase_size "$1" "$2" "$3"


