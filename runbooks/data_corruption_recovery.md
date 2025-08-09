# DR Plan: Ransomware / Data Corruption

Steps:
1. Isolate affected systems.
2. Identify immutable backups within retention window.
3. Restore from known-good snapshot to isolated environment and validate integrity.
4. Reintroduce services after verification.
