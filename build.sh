#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh


CODEBASE_LOCATION="${WORKSPACE}"/"${CODEBASE_DIR}"

graviton_scan() {

  if [ -z "$CODEBASE_LOCATION" ]; then
    echo "Local directory path is required"
    return 1
  fi
    /usr/bin/porting-advisor "$CODEBASE_LOCATION" --output "$CODEBASE_DIR".html
    /usr/bin/porting-advisor  "$CODEBASE_LOCATION" --output "$CODEBASE_DIR"-dependencies.xlsx --output-format dependencies
    
   base_dir="$CODEBASE_LOCATION/graviton_report" #chnage

  if [ ! -d "$base_dir" ]; then
    mkdir -p "$base_dir"
    echo "Created base directory: $base_dir"
  fi

  report_dir="$base_dir/html_report"
  if [ ! -d "$report_dir" ]; then
    mkdir -p "$report_dir"
    echo "Created directory $report_dir"
  else
    echo "Directory $report_dir already exists"
  fi

    mv ./"$CODEBASE_DIR".html "$report_dir"


  dep_dir="$base_dir/dependencies"
  if [ ! -d "$dep_dir" ]; then
    mkdir -p "$dep_dir"
    echo "Created directory $dep_dir"
  else
    echo "Directory $dep_dir already exists"
  fi
    mv ./"$CODEBASE_DIR"-dependencies.xlsx "$dep_dir"
}

if [ -d "${CODEBASE_LOCATION}" ]; then
  graviton_scan
else
  echo "Error: ${CODEBASE_LOCATION} - No such file or directory exists"
  exit 1
fi

#cp -rf reports/* /bp/execution_dir/${GLOBAL_TASK_ID}/
#dest_dir="/bp/execution_dir/${GLOBAL_TASK_ID}/"
dest_dir="/bp/execution_dir/test/"
mkdir -p "$dest_dir"
cp -rf "$base_dir"/* "$dest_dir"
