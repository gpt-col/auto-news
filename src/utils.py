import os
import json

import redis


def gen_filename(data_folder, filename):
    return f"{data_folder}/{filename}"


def save_data_json(full_path, data):
    with open(full_path, "w") as out_file:
        json.dump(data, out_file)


def read_data_json(full_path):
    if not os.path.exists(full_path):
        return {}

    f = open(full_path, "r")
    data = json.load(f)
    f.close()

    return data


def redis_conn(url):
    conn = None

    try:
        conn = redis.from_url(url)
    except Exception as e:
        print(f"[ERROR]: Connect to redis @{url} failed: {e}")

    return conn
