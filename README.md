# AWS Lambda + IAM Bulk Export Toolkit

Two standalone Python / `boto3` scripts used at Production to **mass-export Lambda source code and IAM role definitions** from an AWS account into flat files — handy for disaster recovery snapshots, pre-migration audits, or just getting a plain-text copy of everything you're running. Paired with `lambda_exports/` and `lambda_exports_virginia/` folders that hold the captured ZIPs from two different regions.

## Highlights

- **`functions.py`** — paginates `lambda:ListFunctions`, then for each function calls `lambda:GetFunction`, pulls the presigned `Code.Location` URL, and downloads the deployment ZIP into a local directory. Handles thousands of functions with paginators.
- **`iam.py`** — paginates `iam:ListRoles`, and for each role captures the `AssumeRolePolicyDocument`, attached managed policies, and inline policy names into a single `iam_roles_export.json` file.
- **Region-stamped output** — the default download directory is `lambda_exports_virginia/`; re-run against a different region to produce region-specific dumps. The repo already contains one us-east-1 (Virginia) export alongside the primary Tokyo dump.
- **Dead-simple** — no config, no CLI flags; change the `download_dir=` default or swap AWS profile and go.

## Architecture

```
 AWS account
    │
    ├── functions.py ─► list_functions() → for each: get_function() → GET code_url
    │                                                                   │
    │                                                                   ▼
    │                                                      lambda_exports/<fn>.zip
    │                                                      lambda_exports_virginia/<fn>.zip
    │
    └── iam.py       ─► list_roles() → for each: get_role + list_attached + list_inline
                                                                         │
                                                                         ▼
                                                         iam_roles_export.json
```

## Tech stack

- **Language:** Python 3
- **Libraries:** `boto3`, `requests`, `os`, `json`
- **AWS services:** Lambda, IAM (read-only)

## Repository layout

```
CloudFront/                        # folder name is historical; content is Lambda+IAM export
├── README.md
├── .gitignore
├── functions.py                   # bulk-download Lambda deployment ZIPs
├── iam.py                         # dump all IAM roles + policies to JSON
├── iam_roles_export.json          # captured IAM dump
├── lambda_exports/                # captured Tokyo Lambda ZIPs
├── lambda_exports_virginia/       # captured us-east-1 Lambda ZIPs
└── new/                           # additional captures
```

> The folder is named `CloudFront/` for historical reasons — the original task was to inventory everything touching a CloudFront distribution and it grew into a full account dump. Rename on publishing (suggested: `aws-account-export/`).

## How it works

### `functions.py`

```
get_lambda_functions()  →  paginator('list_functions') → names[]
for name in names:
    response = get_function(FunctionName=name)
    code_url = response['Code']['Location']           # presigned S3 URL
    requests.get(code_url) → write <name>.zip to download_dir
```

### `iam.py`

```
get_iam_roles()  →  paginator('list_roles') → roles[]
for role in roles:
    get_role(RoleName)             → AssumeRolePolicyDocument
    list_attached_role_policies    → AttachedPolicies
    list_role_policies             → InlinePolicy names
    append to export list
json.dump(export, 'iam_roles_export.json')
```

## Prerequisites

- Python 3.8+
- `pip install boto3 requests`
- AWS credentials with `lambda:ListFunctions`, `lambda:GetFunction`, `iam:ListRoles`, `iam:GetRole`, `iam:ListAttachedRolePolicies`, `iam:ListRolePolicies`

## Usage

```bash
# Export every Lambda's deployment ZIP in the current region
python functions.py

# Export every IAM role + policy references to JSON
python iam.py
```

## Notes

- The presigned `Code.Location` URL is time-limited (~10 min) — the script downloads each ZIP in-line, so long runs across thousands of functions are fine as long as each individual call doesn't stall.
- `iam.py` captures only inline policy *names*; extend with `get_role_policy(RoleName, PolicyName)` to also serialise the inline policy documents verbatim.
- For a complete account snapshot, pair with Config or CloudTrail Lake; these scripts are the quick / manual equivalent.
- Demonstrates: boto3 paginator patterns, presigned-URL consumption, account-wide inventory scripting, region-differentiated exports.
