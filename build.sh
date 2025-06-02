#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh


CODEBASE_LOCATION="${WORKSPACE}"/"${CODEBASE_DIR}"

graviton_scan() {

  cd ${CODEBASE_LOCATION}

  if [ -z "$CODEBASE_LOCATION" ]; then
    echo "Local directory path is required"
    return 1
  fi

  source_dir=$(basename "$CODEBASE_LOCATION")
    /usr/bin/porting-advisor "$CODEBASE_LOCATION" --output "$source_dir".html
    /usr/bin/porting-advisor  "$CODEBASE_LOCATION" --output "$source_dir"-dependencies.xlsx --output-format dependencies
    
   timestamp=$(date +%Y%m%d%H%M%S)
   base_dir=~/graviton_report

  if [ ! -d "$base_dir" ]; then
    mkdir -p "$base_dir"
    echo "Created base directory: $base_dir"
  fi

  report_dir="$base_dir/report"
  if [ ! -d "$report_dir" ]; then
    mkdir -p "$report_dir"
    echo "Created directory $report_dir"
  else
    echo "Directory $report_dir already exists"
  fi

    new_name="$report_dir/${source_dir}_$timestamp.html"
    mv ./"$source_dir".html "$new_name"


  dep_dir="$base_dir/dependencies"
  if [ ! -d "$dep_dir" ]; then
    mkdir -p "$dep_dir"
    echo "Created directory $dep_dir"
  else
    echo "Directory $dep_dir already exists"
  fi
    new_dep_name="$dep_dir/${source_dir}-dependencies_$timestamp.xlsx"
    mv ./"$source_dir"-dependencies.xlsx "$new_dep_name"
}

if [ -d "${CODEBASE_LOCATION}" ]; then
  graviton_scan
else
  echo "Error: ${CODEBASE_LOCATION} - No such file or directory exists"
  exit 1
fi




