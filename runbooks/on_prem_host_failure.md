# DR Plan: On-Prem Host Failure

Steps:
1. Identify last successful backup manifest for affected host.
2. Provision replacement host (cloud or on-prem).
3. Use run_restore.py with the manifest to restore data.
4. Run health checks and reconfigure DNS or load balancers if needed.
