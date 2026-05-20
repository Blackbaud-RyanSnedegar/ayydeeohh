# ADO CLI (`ado.py`)

Small command-line utility for creating and managing Azure DevOps work items from your terminal.

## What It Does

`ado.py` supports four operations:

- Create a work item
- Update fields on an existing work item
- Close a work item
- Get a work item by ID

All responses are printed as formatted JSON.

## Requirements

- Python 3.8+
- `requests` package if you don't already have it...
- Azure DevOps Personal Access Token (PAT) with work item permissions

Install dependency:

```bash
pip install requests
```

## Authentication and Required Global Arguments

Every command requires:

- `--org`: Azure DevOps organization name
- `--project`: Azure DevOps project name
- `--pat`: Personal Access Token

Example shared values:

```bash
python --org my-org --project MyProject --pat <YOUR_PAT>
```

## Command Usage

General pattern:

```bash
python ado.py --org <ORG> --project <PROJECT> --pat <PAT> <command> [options]
```

### 1. Create a Work Item

```bash
python ado.py --org my-org --project MyProject --pat <YOUR_PAT> create \
	--type Task \
	--title "Investigate login timeout" \
	--description "Repro in staging and capture logs" \
	--field System.AssignedTo="Jane Doe" \
	--field Microsoft.VSTS.Common.Priority=2
```

Required options:

- `--type` (examples: `Task`, `Bug`, `User Story`)
- `--title`

Optional:

- `--description` (defaults to empty)
- `--field key=value` (repeatable)

### 2. Update a Work Item

```bash
python ado.py --org my-org --project MyProject --pat <YOUR_PAT> update \
	--id 1234 \
	--field System.Title="Updated ticket title" \
	--field Microsoft.VSTS.Common.Priority=1
```

Required options:

- `--id`
- At least one `--field key=value`

### 3. Close a Work Item

```bash
python ado.py --org my-org --project MyProject --pat <YOUR_PAT> close --id 1234
```

This sets `System.State` to `Closed`.

### 4. Get a Work Item

```bash
python ado.py --org my-org --project MyProject --pat <YOUR_PAT> get --id 1234
```

## Field Format

Use `--field` as:

```text
Field.ReferenceName=value
```

Examples:

- `System.AssignedTo=Jane Doe`
- `System.State=Active`
- `Microsoft.VSTS.Common.Priority=1`
- `System.LinkTypes.Hierarchy-Reverse=4321` # this is the parent id link. Hierarchy-Forward is child link.
- `System.AreaPath=Products\Linux\Relocation`
- `System.IterationPath=Products\2026`

If a field is missing `=`, the script exits with an error.

## Notes

- The script exits with status code `1` on API errors and prints the Azure DevOps response text.
- Keep PATs secure. Prefer environment variables or a secret manager instead of hardcoding in scripts.
