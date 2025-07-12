import re
import os
import sys
import csv
import time
import shutil
from jinja2 import Template
from datetime import datetime

def read_file_content(filename):
    """Read content from a file with error handling"""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File {filename} not found")
        return ""
    except Exception as e:
        print(f"Error reading file {filename}: {str(e)}")
        return ""


def parse_cluster_summary(file_content):
    """Parse cluster upgrade summary from file content"""
    cluster_info = {
        'current_version': 'unknown',
        'target_version': 'unknown',
        'status': 'unknown'
    }

    # Extract version information
    version_match = re.search(r'Current version: (\d+\.\d+)', file_content)
    if version_match:
        cluster_info['current_version'] = version_match.group(1)

    # Extract from table if available
    table_match = re.search(r'eks-upgrade-cluster \| (\d+\.\d+).*?\| (\d+\.\d+).*?\| (.*?)\s', file_content)
    if table_match:
        cluster_info['current_version'] = table_match.group(1)
        cluster_info['target_version'] = table_match.group(2)
        cluster_info['status'] = table_match.group(3).strip()

    return cluster_info


def parse_nodegroups(file_content):
    """Parse nodegroup upgrade information from file content"""
    nodegroups = []

    # Find all nodegroup entries
    matches = re.finditer(r'(\w+-NG)\s*\|\s*(\d+\.\d+)\s*\|\s*(\d+\.\d+)\s*\|\s*(\w+)', file_content)
    for match in matches:
        nodegroups.append({
            'name': match.group(1),
            'current_version': match.group(2),
            'target_version': match.group(3),
            'status': match.group(4)
        })

    return nodegroups

def parse_addons(file_content):
    addons = []
    for line in file_content.strip().splitlines():
        line = line.strip()
    
        if re.match(r"^[^,]+,[^,]+,[^,]+,[^,]+$", line):
            name, current_version, target_version, status = line.split(",")
            addons.append({
                "name": name.strip(),
                "current_version": current_version.strip(),
                "target_version": target_version.strip(),
                "status": status.strip()
            })
    return addons


def parse_api_check(log_content):
    """Parse API version check results from log file"""
    api_check = {
        'status': 'Unknown',
        'details': 'No information found'
    }

    if 'No deprecated APIs found' in log_content:
        api_check['status'] = 'No issues found'
        api_check['details'] = 'API Check: No deprecated APIs found'
    else:
        api_check['status'] = 'Issues found'
        api_check['details'] = 'Check api_version_check_output.json for details'

    return api_check

def generate_html_report(data):
    """Generate HTML report using Jinja2 template"""
   
    has_issues = False
    warning_messages = []
    

    if data['cluster']['status'] not in ['Upgraded', 'Already Up-to-date']:
        has_issues = True
        warning_messages.append("Cluster upgrade is not complete")
    
  
    for ng in data['nodegroups']:
        if ng['status'] not in ['Upgraded', 'Already Up-to-date']:
            has_issues = True
            warning_messages.append(f"Nodegroup {ng['name']} needs attention")
            break
  
    for addon in data['addons']:
        if addon['status'] not in ['Upgraded', 'Already Up-to-date']:
            has_issues = True
            warning_messages.append(f"Addon {addon['name']} needs attention")
            break
    
    if data['api_check']['status'] != 'No issues found':
        has_issues = True
        warning_messages.append("API compatibility issues found")
    
    if has_issues:
        warning_text = "⚠️ WARNING: " + ", ".join(warning_messages[:3]) 
        if len(warning_messages) > 3:
            warning_text += f" (+{len(warning_messages)-3} more)"
    else:
        warning_text = "✅ All checks passed - No critical issues found"
    
    template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EKS Upgrade Report</title>
<style>
body { font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9; color: #333; }
.container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.header-banner { width: 100%; margin-bottom: 20px; position: relative; }
.header-image { 
    width: 100%; 
    height: 200px; 
    object-fit: cover; 
}
.banner-text { 
    position: absolute; 
    bottom: 15px; 
    left: 10px; 
    color: white; 
    background-color: rgba(0,0,0,0.6); 
    padding: 10px 5px;
    border-radius: 5px;
}
.custom-banner {
    background-color: #1a73e8;
    color: white;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
    text-align: center;
    font-size: 1.2em;
}
.warning-banner {
    background-color: #ff9800;
    color: white;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
    text-align: center;
    font-size: 1.2em;
}
.success-banner {
    background-color: #4caf50;
    color: white;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 5px;
    text-align: center;
    font-size: 1.2em;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
    border: 2px solid #333;
}
th, td {
    border: 1px solid #333;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
    color: #333;
}
h1, h2 { color: #333; }
a { color: #1a73e8; text-decoration: none; }
a:hover { text-decoration: underline; }
p { font-size: 14px; }
.success { color: green; }
.warning { color: orange; }
.error { color: red; }
.note { background-color: #fffde7; padding: 10px; border-left: 4px solid #ffd600; }
code { background-color: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
</style>
</head>
<body>
<div class="header-banner">
    <img src="https://blogs.halodoc.io/content/images/2020/10/pritam-1-2.png" alt="EKS Upgrade Header" class="header-image">
    <div class="banner-text">
        <h1>EKS Cluster Upgrade Report</h1>
        <p>Comprehensive upgrade analysis and recommendations</p>
    </div>
</div>

<div class="container">
    <!-- Dynamic Warning Banner -->
    <div class="{% if has_issues %}warning-banner{% else %}success-banner{% endif %}">
        {{ warning_text }}
    </div>

<h1>EKS Upgrade Report from {{ cluster.current_version }} to {{ cluster.target_version }}</h1>
<p><strong>Generated:</strong> {{ timestamp }}</p>
<p><strong>Cluster Name:</strong> eks-upgrade-cluster</p>
<p><strong>Region:</strong> us-east-1</p>
<p><strong>Cluster Version:</strong> {{ cluster.current_version }} → {{ cluster.target_version }}</p>
<p><strong>Status:</strong> 
  <span class="{% if cluster.status in ['Upgraded', 'Done', 'Already Upgraded', 'Already Up-to-date'] %}
                  success
               {% elif cluster.status == 'Pending' %}
                  warning
               {% else %}
                  error
               {% endif %}">
    {{ cluster.status }}
  </span>
</p>
<h2>📋 Pre-checks Summary</h2>
<table>
<tr><th>Check</th><th>Result</th></tr>
<tr>
  <td>API Version Compatibility</td>
  <td class="{% if api_check.status in ['Upgraded', 'Done', 'Already Upgraded', 'Already Up-to-date', 'No issues found'] %}
                 success
              {% elif api_check.status == 'Pending' %}
                 warning
              {% else %}
                 error
              {% endif %}">
    {{ api_check.details }}
  </td>
</tr>
</table>

<h2>🧱 Node Pools</h2>
<table>
<tr><th>Node Group</th><th>Current Version</th><th>Target Version</th><th>Status</th></tr>
{% for ng in nodegroups %}
<tr>
  <td>{{ ng.name }}</td>
  <td>{{ ng.current_version }}</td>
  <td>{{ ng.target_version }}</td>
  <td class="{% if ng.status in ['Upgraded', 'Done', 'Already Upgraded', 'Already Up-to-date'] %}
                  success
               {% elif ng.status == 'Pending' %}
                  warning
               {% else %}
                  error
               {% endif %}">
    {{ ng.status }}
  </td>
</tr>
{% endfor %}
</table>

<h2>🔌 Add-ons</h2>
<table border="1">
<tr><th>Add-on Name</th><th>Current Version</th><th>Target Version</th><th>Status</th></tr>
{% for addon in addons %}
<tr>
  <td>{{ addon.name }}</td>
  <td>{{ addon.current_version }}</td>
  <td>{{ addon.target_version }}</td>
  <td class="{% if addon.status in ['Upgraded', 'Done', 'Already Upgraded', 'Already Up-to-date'] %}
                  success
               {% elif addon.status == 'Pending' %}
                  warning
               {% else %}
                  error
               {% endif %}">
    {{ addon.status }}
  </td>
</tr>
{% endfor %}
</table>

<h2>📝 Notes</h2>
<div class="note">
<ul>
{% set addon_names = addons|map(attribute='name')|list %}
{% if 'vpc-cni' in addon_names %}
<li><strong>vpc-cni:</strong> Requires IAM OIDC provider to be associated with the cluster. Run: <code>eksctl utils associate-iam-oidc-provider --region=us-east-1 --cluster=eks-upgrade-cluster</code></li>
{% endif %}
{% if 'coredns' in addon_names %}
<li><strong>coredns:</strong> Marked as incompatible - please check EKS add-on compatibility matrix for version {{ cluster.target_version }}.</li>
{% endif %}
{% if cluster.status == 'Upgraded', 'Done', 'Already Upgraded', 'Already Up-to-date' %}
<li>Cluster is already at the target version. No upgrade needed.</li>
{% endif %}
</ul>
</div>
</body>
</html>
"""
    template = Template(template_str)
    return template.render(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        cluster=data['cluster'],
        nodegroups=data['nodegroups'],
        addons=data['addons'],
        api_check=data['api_check'],
        has_issues=has_issues,
        warning_text=warning_text
    )


def main(input_dir=".", sleep_duration=5):
    print(f"Sleeping for {sleep_duration} seconds before starting...")
    time.sleep(sleep_duration)

    cluster_path = os.path.join(input_dir, "eks-cluster-summary.txt")
    nodegroup_path = os.path.join(input_dir, "nodegroup-summary.txt")
    addon_path = os.path.join(input_dir, "addon-output.txt")
    api_check_path = os.path.join(input_dir, "api_version_check_output.log")

    cluster_content = read_file_content(cluster_path)
    nodegroup_content = read_file_content(nodegroup_path)
    addon_content = read_file_content(addon_path)
    api_check_content = read_file_content(api_check_path)

    data = {
        'cluster': parse_cluster_summary(cluster_content),
        'nodegroups': parse_nodegroups(nodegroup_content),
        'addons': parse_addons(addon_content),
        'api_check': parse_api_check(api_check_content)
    }

    html_report = generate_html_report(data)

    output_file = "eks_upgrade_report.html"
    with open(output_file, 'w') as f:
        f.write(html_report)

    print(f"Report generated: {output_file}")

    target_dir = "/bp/workspace/report"
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(output_file, target_dir)
    print(f"Location: {os.path.abspath(output_file)}")
    print(f"Copied to: {os.path.abspath(os.path.join(target_dir, output_file))}")

if __name__ == "__main__":

    input_directory = os.getenv("INPUT_DIR", ".")
    sleep_duration = int(os.getenv("SLEEP_DURATION", "5"))

    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            sleep_duration = int(sys.argv[1])
            if len(sys.argv) > 2:
                input_directory = sys.argv[2]
        else:
            input_directory = sys.argv[1]
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                sleep_duration = int(sys.argv[2])

main(input_directory, sleep_duration)
