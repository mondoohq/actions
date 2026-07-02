# Mondoo Terraform Plan Action

A [GitHub Action](https://github.com/features/actions) for testing [HashiCorp Terraform](https://developer.hashicorp.com/terraform) plan files for security misconfigurations. Plan files must be saved in JSON format before they are scanned.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- A Terraform plan saved in JSON format (`terraform show -json`) must be available to the runner.

## Properties

The Terraform Plan Action has properties that are passed to the action using `with`.

| Property                      | Required | Default       | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info          | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact       | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report, sarif (default "compact")                                                                                              |
| `output-file`                 | false    | results.sarif | Path to write the scan report to. Combine with `output: sarif` to produce a SARIF report you can upload to GitHub code scanning.                                                                                       |
| `path`                        | false    | terraform     | Path to the directory containing the plan file.                                                                                                                                                                        |
| `plan-file`                   | false    | plan.json     | Name of the JSON plan file to scan.                                                                                                                                                                                    |
| `risk-threshold`              | false    | 101           | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `service-account-credentials` | false    |               | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |

## Scan a Terraform plan file

The following example uses HashiCorp's [setup-terraform](https://github.com/hashicorp/setup-terraform) to generate a Terraform plan file and convert it to JSON before running a scan with cnspec.

```yaml
name: Mondoo Terraform plan security scan

on:
  pull_request:
  push:
    branches: [main]

defaults:
  run:
    working-directory: ./terraform

jobs:
  generate-and-scan-terraform-plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: hashicorp/setup-terraform@v4
        with:
          terraform_wrapper: false

      - name: Terraform Init
        id: terraform-init
        run: terraform init

      - name: Convert Terraform plan to JSON
        id: plan-to-json
        run: |
          terraform plan -no-color -out plan.tfplan
          terraform show -json plan.tfplan >> plan.json
        continue-on-error: true

      - name: Scan Terraform plan file for security misconfigurations
        uses: mondoohq/actions/terraform-plan@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: terraform
          plan-file: plan.json
```

## Report findings to GitHub code scanning

Set `output: sarif` to write a [SARIF](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) report, then upload it so findings appear in the repository's Security tab and on pull requests.

```yaml
- name: Scan Terraform plan file for security misconfigurations
  uses: mondoohq/actions/terraform-plan@v13.3.0
  env:
    MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
  with:
    path: terraform
    plan-file: plan.json
    output: sarif
    output-file: results.sarif
- name: Upload SARIF results file
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: results.sarif
```

> The job needs `permissions: security-events: write` to upload SARIF. The action runs at the workspace root (the `defaults.run.working-directory` above only affects `run:` steps), so `--output-file results.sarif` is written there. It only contains SARIF when `output: sarif` is set; leave `output` at its default to keep the human-readable console output.

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
