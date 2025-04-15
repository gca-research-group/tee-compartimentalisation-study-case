import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import time
import json
import csv

API_BASE = "https://200.17.87.181:8080/api"
verify_tls = False
headers = {"Content-Type": "application/json"}

payload = {
    "IDVendedor": 1,
    "IDCliente": 1,
    "Total": 150.00,
    "Data": "2025-04-13T22:00:00"
}

get_file = "overhead_get.csv"
post_file = "overhead_post.csv"

with open(get_file, mode='w', newline='') as get_csv, open(post_file, mode='w', newline='') as post_csv:
    get_writer = csv.writer(get_csv)
    post_writer = csv.writer(post_csv)

    get_writer.writerow(["iteration", "status_code", "duration_ms"])
    post_writer.writerow(["iteration", "status_code", "duration_ms"])

    for i in range(1, 101):
        # GET
        start_get = time.perf_counter()
        response_get = requests.get(f"{API_BASE}/vendas", verify=verify_tls)
        end_get = time.perf_counter()
        duration_get = (end_get - start_get) * 1000
        get_writer.writerow([i, response_get.status_code, f"{duration_get:.3f}"])

        # POST
        start_post = time.perf_counter()
        response_post = requests.post(f"{API_BASE}/vendas", json=payload, headers=headers, verify=verify_tls)
        end_post = time.perf_counter()
        duration_post = (end_post - start_post) * 1000
        post_writer.writerow([i, response_post.status_code, f"{duration_post:.3f}"])
