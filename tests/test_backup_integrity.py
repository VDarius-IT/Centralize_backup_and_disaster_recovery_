import os
import subprocess
import time

def test_dry_run_creates_manifest(tmp_path):
    # Run run_backup.py in dry-run mode and point LOCAL_BACKUP_ROOT to tmp_path
    env = os.environ.copy()
    env['LOCAL_BACKUP_ROOT'] = str(tmp_path)
    cmd = ["python3", "scripts/run_backup.py", "--target", "test-target", "--dry-run"]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert p.returncode == 0
    # Check manifest exists
    manifests = list((tmp_path / "manifests").glob("test-target-*.manifest.json"))
    assert len(manifests) == 1
