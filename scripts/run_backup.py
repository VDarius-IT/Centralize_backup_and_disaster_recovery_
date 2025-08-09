#!/usr/bin/env python3
"""
Simple backup orchestrator demo.

Features:
- Supports dry-run (simulates backup)
- If boto3 is available and AWS credentials/backet configured, can run basic S3 upload of a manifest
- Exposes minimal Prometheus metrics on /metrics
"""
import os
import sys
import argparse
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

try:
    from prometheus_client import Counter, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
except Exception:
    Counter = None

REGISTRY = None
backup_counter = None
failure_counter = None

def start_metrics_server(host="0.0.0.0", port=8000):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/metrics" and REGISTRY is not None:
                data = generate_latest(REGISTRY)
                self.send_response(200)
                self.send_header("Content-Type", CONTENT_TYPE_LATEST)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()

    server = HTTPServer((host, port), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

def init_metrics():
    global REGISTRY, backup_counter, failure_counter
    if Counter is None:
        return
    from prometheus_client import CollectorRegistry, Counter
    REGISTRY = CollectorRegistry()
    backup_counter = Counter('backup_jobs_total', 'Total backup jobs run', registry=REGISTRY)
    failure_counter = Counter('backup_job_failed_total', 'Total failed backup jobs', registry=REGISTRY)

def write_manifest(target, outdir):
    os.makedirs(outdir, exist_ok=True)
    manifest = {
        "target": target,
        "timestamp": int(time.time()),
        "status": "SUCCESS"
    }
    filename = os.path.join(outdir, f"{target}-{manifest['timestamp']}.manifest.json")
    with open(filename, "w") as f:
        json.dump(manifest, f)
    return filename

def do_backup(target, dry_run=False, local_root="./backups"):
    try:
        if dry_run:
            print(f"[dry-run] Simulating backup for {target}")
            fname = write_manifest(target, os.path.join(local_root, "manifests"))
            print("[dry-run] Manifest written to", fname)
            if backup_counter:
                backup_counter.inc()
            return 0
        # If boto3 and BACKUP_BUCKET present, perform a simple manifest upload
        try:
            import boto3
            s3 = boto3.client('s3')
            bucket = os.environ.get("BACKUP_BUCKET")
            if bucket:
                fname = write_manifest(target, "/tmp")
                s3.upload_file(fname, bucket, os.path.basename(fname))
                print("Uploaded manifest to s3://{}/{}".format(bucket, os.path.basename(fname)))
                if backup_counter:
                    backup_counter.inc()
                return 0
        except Exception as e:
            print("boto3 upload failed or not configured:", e)

        # Fallback: write local manifest
        fname = write_manifest(target, os.path.join(local_root, "manifests"))
        print("Manifest written to", fname)
        if backup_counter:
            backup_counter.inc()
        return 0
    except Exception as e:
        print("Backup failed:", str(e))
        if failure_counter:
            failure_counter.inc()
        return 2

def main():
    parser = argparse.ArgumentParser(description="Run backup for a target")
    parser.add_argument("--target", required=True, help="Target name from configs/targets.yml")
    parser.add_argument("--dry-run", action="store_true", help="Simulate backup without modifying remote systems")
    parser.add_argument("--metrics-host", default=os.environ.get("METRICS_LISTEN_ADDR", "0.0.0.0"))
    parser.add_argument("--metrics-port", type=int, default=int(os.environ.get("METRICS_LISTEN_PORT", 8000)))
    args = parser.parse_args()

    init_metrics()
    if REGISTRY is not None:
        start_metrics_server(args.metrics_host, args.metrics_port)
        print(f"Metrics available at http://{args.metrics_host}:{args.metrics_port}/metrics")

    rc = do_backup(args.target, dry_run=args.dry_run)
    sys.exit(rc)

if __name__ == "__main__":
    main()
