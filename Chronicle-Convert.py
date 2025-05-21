import xml.etree.ElementTree as ET
import json
import os
import sys
import argparse
import socket
from datetime import datetime

# Output directory
OUTPUT_DIR = "/var/log/scans/"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return hostname, ip_address

def safe_split_tags(tags_str):
    tag_dict = {}
    tags_list = tags_str.split('|')
    for tag in tags_list:
        split_tag = tag.split('=', 1)
        if len(split_tag) == 2:
            tag_dict[split_tag[0].strip()] = split_tag[1].strip()
        else:
            tag_dict[split_tag[0].strip()] = "N/A"
    return tag_dict

def clean_text(text):
    text = text.replace('Installation\r\npath / port:', 'Installation path / port:').replace(
        'Installation\npath / port:', 'Installation path / port:').strip()
    text = text.replace('\n', ' ')
    return ' '.join(text.split())

def is_all_na(entry):
    return all(value == "N/A" or value == "" for key, value in entry.items() if key != "id")

def parse_openvas_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    results = []
    hostname, ip_address = get_system_info()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    
    # Extract report-level attributes
    report = root if root.tag == "report" else root.find(".//report")
    #report = root.find(".//report")
    task = root.find(".//task")  # Find task outside of report
    
    report_attributes = {
        "report_id": report.get("id", "N/A"),
        "report_format_id": report.get("format_id", "N/A"),
        "report_scan_start": report.findtext("scan_start", default="N/A"),
        "report_task_id": task.get("id", "N/A") if task is not None else "N/A",
        "report_task_name": clean_text(task.findtext("name", default="N/A")) if task is not None else "N/A",
      }

    for result in root.findall(".//result"):
        result_data = {
            "id": result.get("id"),
            "name": result.findtext("name", default="N/A"),
            "host": result.findtext("host", default="N/A"),
            "port": result.findtext("port", default="N/A"),
            "threat": result.findtext("threat", default="N/A"),
            "severity": result.findtext("severity", default="N/A"),
            "original_threat": result.findtext("original_threat", default="N/A"),
            "original_severity": result.findtext("original_severity", default="N/A"),
            "description": clean_text(result.findtext("description", default="")),
            "hostname": hostname,
            "ip_address": ip_address,
            "processed_timestamp": timestamp,
            **report_attributes  # Include report-level attributes
        }

        tags = result.findtext("nvt/tags", default="")
        result_data["tags"] = safe_split_tags(tags)

        if not is_all_na(result_data):
            results.append(result_data)
    
    return results

def save_json(data, output_filename):
    with open(output_filename, "w") as json_file:
        for entry in data:
            json_file.write(json.dumps(entry) + "\n")
    print(f"Saved JSON report: {output_filename}")

def process_file(file_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(OUTPUT_DIR, f"scan_{timestamp}.json")
    results = parse_openvas_xml(file_path)
    save_json(results, output_filename)

def main():
    parser = argparse.ArgumentParser(description="OpenVAS XML to JSON Converter")
    parser.add_argument("filename", help="Path to OpenVAS XML file")
    args = parser.parse_args()
    
    if args.filename:
        process_file(args.filename)
    else:
        print("Usage: ./Convert.py filename.xml")
        sys.exit(1)

if __name__ == "__main__":
    main()
