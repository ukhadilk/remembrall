#!/usr/bin/env bash
echo "Calling AWS from script"


aws s3 sync s3://remembrall-bot-jars /app/jars


if [[ $? -ne 0 ]];then
    echo "Error getting jars"
    return 2
fi