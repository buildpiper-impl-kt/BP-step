#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh

SESSION_NAME="eks-update-session"

function assume_role() {
    creds=$(aws sts assume-role --role-arn arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME --role-session-name "$SESSION_NAME" --output json)
    export AWS_ACCESS_KEY_ID=$(echo "$creds" | jq -r '.Credentials.AccessKeyId')
    export AWS_SECRET_ACCESS_KEY=$(echo "$creds" | jq -r '.Credentials.SecretAccessKey')
    export AWS_SESSION_TOKEN=$(echo "$creds" | jq -r '.Credentials.SessionToken')
    if [ $? -ne 0 ]; then
          echo "Failed to assume role."
          exit 1
    fi
}

function increase_size() {

    if [[ -z "$CLUSTER_NAME" || -z "$NODE_GROUP_NAME" || -z "$MIN_SIZE" || -z "$MAX_SIZE" || -z "$DESIRED_SIZE" || -z "$REGION" ]]; then
        echo "Error: Missing arguments."
        echo "Usage: $0 CLUSTER_NAME NODE_GROUP_NAME MIN_SIZE MAX_SIZE DESIRED_SIZE REGION"
        exit 1
    fi

    assume_role

    output=$(aws eks update-nodegroup-config \
        --cluster-name "$CLUSTER_NAME" \
        --nodegroup-name "$NODE_GROUP_NAME" \
        --scaling-config minSize="$MIN_SIZE",maxSize="$MAX_SIZE",desiredSize="$DESIRED_SIZE" \
        --region "$REGION" 2>&1)


    status=$?

    if [[ $status -ne 0 ]]; then
        echo "Error: Failed to update Auto Scaling group."
        echo "Output: $output"
        exit $status
    else
        echo "Successfully updated node group '$NODE_GROUP_NAME' in cluster '$CLUSTER_NAME' with max size $MAX_SIZE , min size $MIN_SIZE , and desired size $DESIRED_SIZE in REGION $REGION."         
    fi
}

increase_size 

