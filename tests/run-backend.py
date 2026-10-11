"""Run integration tests against a temporary server and the ibt2_test database."""
import os
from pathlib import Path
import subprocess
import socket
import sys
import time

import requests
from pymongo import MongoClient

root = Path(__file__).resolve().parent.parent
mongo_url = os.environ.get('IBT2_TEST_MONGO_URL', 'mongodb://localhost:27017')
port = int(os.environ.get('IBT2_TEST_PORT', '3001'))
base_url = f'http://127.0.0.1:{port}/v1.1/'
env = dict(os.environ, IBT2_TEST_MONGO_URL=mongo_url, IBT2_TEST_BASE_URL=base_url)

# Do not mistake an existing server on this port for the test backend.
with socket.socket() as probe:
    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    probe.bind(('127.0.0.1', port))

# Fail before launching the server if the test database is unreachable.
with MongoClient(mongo_url, serverSelectionTimeoutMS=10000) as client:
    client.admin.command('ping')

with subprocess.Popen([
    sys.executable, 'ibt2.py', '--address=127.0.0.1', f'--port={port}',
    '--db_name=ibt2_test', f'--mongo_url={mongo_url}', '--admin_password=admin',
], cwd=root) as server:
    try:
        deadline = time.monotonic() + 30
        while True:
            if server.poll() is not None:
                raise RuntimeError('Test backend exited before becoming ready')
            try:
                response = requests.get(base_url + 'days', timeout=1)
                response.raise_for_status()
                break
            except requests.RequestException:
                if time.monotonic() >= deadline:
                    raise RuntimeError('Test backend did not become ready within 30 seconds')
                time.sleep(0.2)
        result = subprocess.run([sys.executable, 'tests/ibt2_tests.py'], cwd=root, env=env)
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
sys.exit(result.returncode)
