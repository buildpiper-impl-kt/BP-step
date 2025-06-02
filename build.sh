#!/bin/bash
source /opt/buildpiper/shell-functions/functions.sh
source /opt/buildpiper/shell-functions/log-functions.sh

clone() {
local source_code="$1"

  if [ -z "$source_code" ]; then
    echo "Git URL or local directory path is required"
    return 1
  fi

  if [[ "$source_code" == *.git ]]; then
    local source_dir
    source_dir=$(basename -s .git "$source_code")

    mkdir -p ~/source_repo
    echo "Using directory ~/source_repo"
    cd ~/source_repo || return 1

    if [ -d "$source_dir" ]; then
      echo "Directory '$source_dir' already exists."
    else
      echo "Cloning $source_code..."
      git clone "$source_code"
    fi
    cd
    /usr/bin/porting-advisor ~/source_repo/"$source_dir" --output "$source_dir".html
    /usr/bin/porting-advisor  ~/source_repo/"$source_dir" --output "$source_dir"-dependencies.xlsx --output-format dependencies
    
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

  else
    if [ -d "$source_code" ]; then
      echo "Using local directory: $source_code"
      cd "$source_code"

      /usr/bin/porting-advisor "$source_code" --output "$(basename "$source_code")".html
      /usr/bin/porting-advisor  "$source_code" --output "$(basename "$source_code")"-dependencies.xlsx --output-format dependencies
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

    new_name="$report_dir/$(basename "$source_code")_$timestamp.html"
    mv "$(basename "$source_code")".html "$new_name"


  dep_dir="$base_dir/dependencies"
  if [ ! -d "$dep_dir" ]; then
    mkdir -p "$dep_dir"
    echo "Created directory $dep_dir"
  else
    echo "Directory $dep_dir already exists"
  fi
    new_dep_name="$dep_dir/$(basename "$source_code")-dependencies_$timestamp.xlsx"
    mv "$(basename "$source_code")"-dependencies.xlsx "$new_dep_name"
    else
      echo "Directory '$source_code' does not exist."
      return 1
    fi
  fi
}

clone "$1"



# sudo docker run -it -v ~/graviton_report:/root/graviton_report check https://github.com/OT-MICROSERVICES/attendance-api.git
