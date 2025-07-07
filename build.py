import os
import sys
import time
import pandas as pd
import shutil
from datetime import datetime
from sqlalchemy import create_engine

RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

required_vars = ["MYSQL_HOST", "MYSQL_DB", "ENV_FILTER", "START_DATE", "END_DATE"]
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"{RED}ERROR: Missing required environment variables: {', '.join(missing_vars)}{RESET}")
    sys.exit(1)
else:
    print(f"{GREEN}PASS: All required environment variables are set.{RESET}")

db_host = os.getenv("MYSQL_HOST", "db")
db_user = os.getenv("MYSQL_USER", "root")
db_pass = os.getenv("MYSQL_PASS", "password")
db_name = os.getenv("MYSQL_DB")
env_filter_raw = os.getenv("ENV_FILTER")
start_date_input = os.getenv("START_DATE")
end_date_input = os.getenv("END_DATE")
sleep_seconds = int(os.getenv("SLEEP_SECONDS", "5"))


time.sleep(sleep_seconds)

env_filter = tuple(env.strip() for env in env_filter_raw.split(",") if env.strip())

def parse_date_input(date_str, is_start):
    valid_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]
    for fmt in valid_formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    else:
        print(f"{RED}ERROR: Invalid date format '{date_str}'. Allowed formats: YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY{RESET}")
        sys.exit(1)

    if is_start:
        return parsed_date.replace(hour=0, minute=0, second=0)
    else:
        now = datetime.now()
        return parsed_date.replace(hour=now.hour, minute=now.minute, second=now.second)

parsed_start = parse_date_input(start_date_input, is_start=True)
parsed_end = parse_date_input(end_date_input, is_start=False)
start_date = parsed_start.strftime("%Y-%m-%d %H:%M:%S")
end_date = parsed_end.strftime("%Y-%m-%d %H:%M:%S")

file_date_part = f"{parsed_start.strftime('%d%m')}-{parsed_end.strftime('%d%m')}"
env_name_part = "-".join(env_filter)
filename_base = f"{env_name_part}-deployment-user-report{file_date_part}"
csv_filename = f"{filename_base}.csv"
xlsx_filename = f"{filename_base}.xlsx"

env_placeholders = ', '.join(['%s'] * len(env_filter))
query = f"""
SELECT
  a.name AS Environment,
  pj.name AS `Application/Team`,
  d.deployment_name AS `Deployed Microservice`,
  e.created_at AS `Deployment Time`,
  e.status AS `Deployment Status`,
  e.deploy_tag AS `Deployed Artifact`,
  f.name AS `Triggered by user`
FROM environment_master a, project_env b, component_env c, env_cd_detail d,
     env_cd_deploy_history e, user f, project pj
WHERE
  b.environment_master_id = a.id
  AND b.project_id = pj.id
  AND a.name IN ({env_placeholders})
  AND c.project_env_id = b.id
  AND d.component_env_id = c.id
  AND e.env_cd_detail_id = d.id
  AND e.created_at >= '{start_date}'
  AND e.updated_at <= '{end_date}'
  AND e.deploy_by_user_id = f.id;
"""

try:
    engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}")
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=env_filter)

    df.to_csv(csv_filename, index=False)
    df.to_excel(xlsx_filename, index=False)
    print(f"{GREEN}PASS: Exported {csv_filename} and {xlsx_filename}{RESET}")

    destination_dir = "/bp/workspace"
    shutil.move(csv_filename, os.path.join(destination_dir, csv_filename))
    shutil.move(xlsx_filename, os.path.join(destination_dir, xlsx_filename))
    print(f"{GREEN}PASS: Files moved to {destination_dir}{RESET}")

except Exception as e:
    print(f"{RED}ERROR: {e}{RESET}")
    sys.exit(1)
