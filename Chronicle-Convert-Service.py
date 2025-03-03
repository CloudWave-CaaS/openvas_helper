import xml.etree.ElementTree as ET
import json
import os
import socket
import sys
from datetime import datetime

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

def parse_openvas_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    results = []

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
        }

        tags = result.findtext("nvt/tags", default="")
        result_data["tags"] = safe_split_tags(tags)
        results.append(result_data)
    
    return results

def save_json(data, output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(output_dir, f"scan_{timestamp}.json")
    with open(output_filename, "w") as json_file:
        for entry in data:
            json_file.write(json.dumps(entry) + "\n")
    print(f"Saved JSON report: {output_filename}")

def process_file(file_path, output_dir):
    results = parse_openvas_xml(file_path)
    save_json(results, output_dir)

def tcp_listener(port, output_dir):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Listening for OpenVAS reports on port {port}...")
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection received from {addr}")
        data = b""
        while True:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            data += chunk
        client_socket.close()
        
        if data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(output_dir, f"scan_{timestamp}.xml")
            with open(file_path, "wb") as f:
                f.write(data)
            print(f"Received XML saved to {file_path}")
            process_file(file_path, output_dir)

def main():
    OUTPUT_DIR = "/var/log/scans/"
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    PORT = 7680
    tcp_listener(PORT, OUTPUT_DIR)

if __name__ == "__main__":
    main()
