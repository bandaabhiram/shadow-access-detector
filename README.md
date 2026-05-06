# Shadow Access Detector for Entra ID

> **PIM catches privileged access. This catches the privileged access PIM forgot.**

An automated "access hygiene" engine that finds dangerous identity gaps Microsoft doesn't surface: disabled accounts with active refresh tokens, guest users still holding RBAC 6 months after project ended, service principals with `Contributor` that haven't authenticated in 180 days, and orphaned managed identities attached to deleted resources but still holding Key Vault access.

## 🎓 Author Credentials
- **AZ-500** Microsoft Certified: Azure Security Engineer Associate
- **MSc Cybersecurity** — Heriot-Watt University (NCSC-certified)
- **1 Year Azure DevOps** — CI/CD, IaC, pipeline security gates

## 🚨 Problem Statement

Azure AD Access Reviews catch *active* assignments, but miss:
- **Disabled users** whose sessions are still valid (token hasn't expired)
- **Guests** "removed" from team but still in Entra ID with RBAC
- **Service principals** created by apps that were uninstalled
- **Managed identities** on deleted VMs still in Key Vault access policies

## 🏗️ Architecture

```
┌──────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Microsoft Graph │────▶│  Logic Apps  │────▶│  Azure Data     │
│  API (Beta)      │     │  Workflow    │     │  Lake Gen2      │
└──────────────────┘     └──────────────┘     └────────┬────────┘
                                                       │
              ┌────────────────────────────────────────┘
              ▼
    ┌─────────────────┐     ┌─────────────────┐
    │  Scoring Engine │────▶│  Sentinel +     │
    │  (Python)       │     │  KQL Analytics  │
    └─────────────────┘     └─────────────────┘
```

## 🛠️ Technologies & Rationale

| Technology | Why |
|------------|-----|
| **Terraform** | Deploys dedicated "security audit" RG with least-privilege MI |
| **Azure Logic Apps** | Orchestrates multi-step audit: Graph query → transform → Sentinel incident |
| **Microsoft Graph API (Beta)** | Only way to access `signInActivity`, `refreshTokensValidFromDateTime` |
| **Azure Data Lake Gen2** | Raw Graph JSON exports for 2 years. Parquet for cheap analytics |
| **Azure Synapse Serverless SQL** | Query Data Lake without moving data |
| **Sentinel + KQL** | "Shadow Access Score > 80 = auto-create incident" |

## ⚖️ Tradeoffs Made

- **Graph API throttling:** Hit 429 errors on large tenants. Implemented exponential backoff + delta pagination.
- **Privacy vs Security:** `signInActivity` requires `AuditLog.Read.All`. Isolated Logic App in dedicated subscription.
- **False positive rate:** 15% of detections are legitimate. Added frequency pattern detection to reduce noise.

## 🚀 Quick Start

```bash
git clone https://github.com/bandaabhiram/shadow-access-detector.git
cd shadow-access-detector/terraform
terraform init
terraform apply -var="tenant_id=$AZURE_TENANT_ID"
```

## 📊 Shadow Risk Score

| Score | Severity | Action |
|-------|----------|--------|
| 0-30  | Low      | Log only |
| 31-60 | Medium   | Weekly digest to security team |
| 61-80 | High     | Daily email + Teams alert |
| 81-100| Critical | **Auto-create Sentinel incident** |

## 📁 Repo Structure

```
shadow-access-detector/
├── terraform/
│   ├── graph_api_permissions.tf
│   ├── logic_app_workflow.tf
│   └── data_lake.tf
├── src/
│   ├── graph_queries/
│   ├── scoring_engine/
│   └── remediation_playbooks/
├── sentinel/
│   ├── analytics_rules/
│   └── workbooks/
├── docs/
└── tests/
```
