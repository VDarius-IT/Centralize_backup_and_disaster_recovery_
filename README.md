# 🛡️ Ensuring Business Continuity: A Centralized Backup & Disaster Recovery Strategy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A resilient, scalable, and automated solution designed to safeguard on-premise VMs and critical AWS resources, ensuring minimal downtime and zero data loss.

This repository contains the complete architecture, implementation scripts, and operational procedures for a centralized backup and disaster recovery (DR) strategy. It was architected to provide high availability and data integrity across a hybrid cloud environment.

---

## 🎯 Project Objective

To architect and implement a unified disaster recovery framework that minimizes **Recovery Time Objective (RTO)** and **Recovery Point Objective (RPO)**. This is achieved through robust automation, comprehensive monitoring, and clearly documented procedures to counter infrastructure failures, human error, or cyber threats.

---

## Table of Contents

1.  [Key Features](#-key-features)
2.  [Guiding Principles](#-guiding-principles)
3.  [System Architecture](#-system-architecture)
4.  [Technology Stack](#-technology-stack)
5.  [Getting Started](#-getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation & Configuration](#installation--configuration)
6.  [Usage](#-usage)
    -   [Running a Manual Backup](#running-a-manual-backup)
    -   [Performing a Restore](#performing-a-restore)
7.  [Monitoring & Alerting](#-monitoring--alerting)
8.  [Disaster Recovery Procedures (RTO/RPO)](#-disaster-recovery-procedures-rtorpo)
9.  [Testing & Validation](#-testing--validation)
10. [Repository Structure](#-repository-structure)
11. [Contributing](#-contributing)
12. [License](#-license)

---

## ✨ Key Features

*   **Hybrid Environment Support**: Manages backups for both on-premise virtual machines (e.g., VMware, Hyper-V) and AWS cloud resources (EBS Snapshots).
*   **Automated Backup Lifecycle**: Robust scripts (Python/Bash) for scheduling, executing, and verifying backups with configurable retention policies.
*   **Centralized Management**: A single control plane for initiating and monitoring all backup and recovery operations.
*   **Continuous Health Monitoring**: Real-time observability into backup job status, system health, and storage utilization using Prometheus.
*   **Intelligent Alerting**: Proactive notifications for backup failures, RPO violations, or system anomalies via Alertmanager (to Slack, Email, etc.).
*   **Rich Visualization**: Interactive Grafana dashboards provide a clear view of backup history, duration, data size, and DR readiness.
*   **Documented DR Playbooks**: Step-by-step runbooks for various failure scenarios, ensuring a predictable and rapid recovery.
*   **Immutable & Secure**: Implements best practices like encrypted backups and can integrate with immutable storage targets (like S3 Object Lock) to protect against ransomware.

---

## 🧭 Guiding Principles

This solution was designed with the following Site Reliability Engineering (SRE) and DevOps best practices in mind:

*   🔐 **Security First**: Use of least-privilege IAM roles, encrypted data transfer and at-rest storage, and secure credentials management.
*   ⚙️ **Automation Over Manual Toil**: If a task is repeatable, it is scripted. This reduces human error and ensures consistency.
*   📈 **Designed for Scalability**: The architecture can grow from a handful of VMs to hundreds of assets without a major redesign.
*   ✅ **Testability is Key**: The system is built to be regularly tested. A DR plan that isn't tested is not a plan—it's a theory.
*   📊 **Observability is Not an Afterthought**: Deep monitoring and alerting are integrated into the core of the solution.

---

## 🏗️ System Architecture

The architecture is designed for resilience and clarity. A central backup orchestrator manages the entire process, collecting data from on-premise and cloud sources, storing it securely, and exposing metrics for monitoring.

```mermaid
graph TD
    subgraph "On-Premise"
        VM1["VMware/Hyper-V VM"]
        VM2["VMware/Hyper-V VM"]
    end

    subgraph "AWS Cloud"
        EC2["EC2 Instance"] --> EBS["EBS Volume"]
    end

    subgraph "Backup & DR Control Plane"
        Orchestrator["Backup Orchestrator<br/>(Python/Bash Scripts)"]
        Scheduler["Scheduler<br/>(Cron / systemd)"]
        BackupRepo["Central Backup Repository<br/>(Encrypted, Versioned)"]
    end

    subgraph "Monitoring & Alerting"
        Prometheus["Prometheus<br/>(Metrics Collection)"]
        Grafana["Grafana<br/>(Dashboards)"]
        Alertmanager["Alertmanager<br/>(Notifications)"]
    end

    VM1 -- API/SSH --> Orchestrator
    VM2 -- API/SSH --> Orchestrator
    EC2 -- AWS API --> Orchestrator
    
    Orchestrator --> BackupRepo
    Orchestrator -- Exposes Metrics --> Prometheus
    
    Prometheus --> Grafana
    Prometheus --> Alertmanager
    Alertmanager -- Alerts --> Slack["Slack / Email"]
```

---

## 🛠️ Technology Stack

*   **Automation & Scripting**: Python (Boto3), Bash
*   **Cloud Provider**: AWS (EC2, EBS, S3, IAM)
*   **On-Premise Virtualization**: Hyper-V
*   **Monitoring**: Prometheus
*   **Visualization & Alerting**: Grafana, Alertmanager
*   **Infrastructure as Code (Optional)**: Terraform
*   **Notifications**: Slack, PagerDuty, Email

---

## 🚀 Getting Started

Follow these instructions to set up the backup and recovery environment.

### Prerequisites

*   Python 3.8+ with `boto3`, `pyyaml`, and `requests`
*   AWS CLI v2, configured with an IAM role/user that has:
    *   `AmazonEC2FullAccess` (or least-privilege: `CreateSnapshot`, `Describe*`, `Start/StopInstances`, etc.)
    *   `AmazonS3ReadOnlyAccess` (for audit) and write access to your backup bucket
    *   `CloudWatchReadOnlyAccess` (optional for metrics)
*   SSH key-based access to on-premise hypervisor management server with `virsh` or `PowerShell` access
*   Docker & Docker Compose v2+ (to run Prometheus, Grafana, Alertmanager)
*   `rsync`, `jq`, `curl`, and `pigz` (for compression) installed on the backup orchestrator host
*   Outbound internet access for AWS API and dependency downloads

### Installation & Configuration

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/[your-username]/[your-repository-name].git
    cd [your-repository-name]
    ```

2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Configure the environment:**

*   Rename `config.env.example` to `config.env`.
*   Update `config.env` with the following:
    *   Your AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`)
    *   S3 bucket name for storing backup manifests and artifacts
    *   On-premise hypervisor IP, SSH user, and VM list/IDs
    *   Backup retention settings (daily/weekly/monthly)
*   Define your backup targets (VMs, EC2 instances) in `configs/targets.yml` using the provided schema.
*   Ensure the orchestrator server has SSH keys deployed to on-premise hosts and IAM role attached (if running on EC2).


4.  **Launch the Monitoring Stack:**
    ```sh
    docker-compose up -d
    ```
    This will start the Prometheus and Grafana containers.
    *   **Prometheus:** `http://<your-server-ip>:9090`
    *   **Grafana:** `http://<your-server-ip>:3000` (Default user/pass: admin/admin)

---

## ⚙️ Usage

### Running a Manual Backup

To trigger an on-demand backup for a specific target:
```sh
python scripts/run_backup.py --target webserver-prod
```

### Performing a Restore

1.  Identify the required backup snapshot ID from the Grafana dashboard, logs, or using:
    ```sh
    aws ec2 describe-snapshots --filters "tag:BackupName=webserver-prod" --query 'Snapshots[*].[SnapshotId,StartTime,VolumeId]' --output table
    ```
2.  Run the restoration script:
    ```sh
    python scripts/run_restore.py --snapshot-id snap-0f5d1a2b3c4d5e --destination-instance i-987zyx --region us-east-1
    ```
3.  Validate service health post-restore via monitoring or application checks.
4.  Update DNS/failover if restoring to a new instance (DR scenario).


---

## 📊 Monitoring & Alerting

*   **Grafana Dashboards**: Pre-built dashboards located in the `/dashboards` directory can be imported into Grafana to visualize:
    *   Backup Job Status (Success, Failed, In-Progress)
    *   RPO Compliance Tracker
    *   Backup Duration & Data Size Trends
    *   Storage Capacity

*   **Prometheus Alerts**: Alerting rules are defined in `prometheus/alert.rules.yml`. Key alerts include:
    *   `BackupJobFailed`: Triggers if a backup job fails.
    *   `RPOViolated`: Triggers if the time since the last successful backup exceeds the defined RPO.
    *   `BackupStorageCapacityHigh`: Fires when the backup repository disk usage is > 85%.

---

## ⏱️ Disaster Recovery Procedures (RTO/RPO)

Our recovery objectives are tiered to align with business criticality.

| Tier | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) | Example Workloads                        |
| :--- | :---------------------------- | :----------------------------- | :--------------------------------------- |
| **1**| **< 1 hour**                  | **< 15 minutes**               | **Critical Databases, Identity Services, Payment Gateways** |
| **2**| **< 4 hours**                 | **< 12 hours**                 | **Internal Applications, Web Servers, APIs** |
| **3**| **< 24 hours**                | **< 24 hours**                 | **Dev/Test Environments, Archives, Logs** |

Detailed, step-by-step DR plans for various scenarios are located in the `/runbooks` directory.
*   `[DR Plan: On-Premise Host Failure](./runbooks/on_prem_host_failure.md)`
*   `[DR Plan: AWS Region Unavailability](./runbooks/aws_region_failure.md)`
*   `[DR Plan: Ransomware Attack / Data Corruption](./runbooks/data_corruption_recovery.md)`

---

## 🧪 Testing & Validation

A disaster recovery plan is only reliable if it is regularly tested. Our validation strategy includes:

*   **Automated Restore Tests**: Weekly, automated jobs that restore a non-critical VM or a snapshot to a temporary location and run a basic health check.
*   **Quarterly DR Drills**: Simulated, full-scale outage drills to test the procedures, tools, and team response.
*   **Performance Tracking**: We measure the **Actual Recovery Time (ART)** during tests and use it to refine our RTOs and procedures.

---

## 📂 Repository Structure

```
.
├── configs/               # Environment variables, target lists (targets.yml)
├── dashboards/            # Grafana JSON dashboard models
├── docs/                  # Extended documentation (architecture details, etc.)
├── monitoring/            # Prometheus rules, Docker-compose for monitoring stack
├── runbooks/              # Step-by-step recovery guides for DR scenarios
├── scripts/               # Core backup, restore, and utility scripts
├── tests/                 # Scripts for testing backup integrity and restores
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Contributions make the open-source community an amazing place to learn and create. Any contributions you make are **greatly appreciated**. Please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
