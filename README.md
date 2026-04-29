# Project # 26 - aws-lambda-iam-export-scripts

Two Python scripts that bulk-export AWS Lambda deployment packages and IAM role definitions from an account into local files. Useful for disaster-recovery snapshots, pre-migration audits, or producing a plain-text inventory of what's running.

## What Each Script Does

### `functions.py`

Paginates `lambda:ListFunctions`, then for each function calls `lambda:GetFunction`, retrieves the presigned `Code.Location` URL, and downloads the deployment ZIP to a local directory.

```
list_functions (paginated) -> names[]
for name in names:
    get_function(name) -> Code.Location (presigned S3 URL)
    download ZIP -> <download_dir>/<name>.zip
```

### `iam.py`

Paginates `iam:ListRoles` and captures, for each role: the trust policy (`AssumeRolePolicyDocument`), all attached managed policies, and the names of all inline policies. Output is a single JSON file.

```
list_roles (paginated) -> roles[]
for role in roles:
    get_role                       -> AssumeRolePolicyDocument
    list_attached_role_policies    -> AttachedPolicies
    list_role_policies             -> inline policy names
write iam_roles_export.json
```

## Stack

Python 3 · boto3 · requests · AWS Lambda · IAM (read-only)

## Repository Layout

```
aws-lambda-iam-export-scripts/
├── functions.py        # Bulk-download Lambda deployment ZIPs
├── iam.py              # Export IAM roles and policy references to JSON
├── .gitignore          # Excludes export output from version control
└── README.md
```

## Prerequisites

- Python 3.8+
- `pip install boto3 requests`
- AWS credentials with: `lambda:ListFunctions`, `lambda:GetFunction`, `iam:ListRoles`, `iam:GetRole`, `iam:ListAttachedRolePolicies`, `iam:ListRolePolicies`

## Usage

Export all Lambda deployment ZIPs in the current region:

```bash
python functions.py
```

Export all IAM roles and attached policy references to JSON:

```bash
python iam.py
```

The output directory for Lambda exports is set via the `download_dir=` default in `functions.py`. Re-run with a different AWS region (set `AWS_DEFAULT_REGION` or switch profile) to produce region-specific dumps.

## Security

Exported files contain sensitive data and should never be committed to a public repository:

- Lambda ZIPs may contain hardcoded secrets, API keys, or proprietary code
- IAM role exports reveal account structure, trust relationships, and permission boundaries

Both output paths are excluded by the `.gitignore` in this repo. Verify before pushing:

```
lambda_exports/
iam_roles_export.json
*.zip
```

## Notes

- The presigned `Code.Location` URL is short-lived (around 10 minutes). Each ZIP is downloaded inline as the function is fetched, so total runtime across thousands of functions is bounded by per-call latency rather than URL expiry.
- `iam.py` captures inline policy *names* only. To include the inline policy documents verbatim, extend with `iam:GetRolePolicy` calls keyed on `(RoleName, PolicyName)`.
- For full continuous account state, AWS Config or CloudTrail Lake is the structured equivalent. These scripts cover the quick manual snapshot case.
