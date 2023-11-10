# Mondoo Terraform Plan Action

A [GitHub Action](https://github.com/features/actions) for testing [HashiCorp Terraform](https://terraform.io) plan files for security misconfigurations. Plan files must be saved in JSON format before they are scanned.

## Properties

The Terraform Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default     | Description                                                                                                                                                                                                                      |
| ----------------------------- | -------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info        | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                             |
| `output`                      | false    | compact     | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                               |
| `path`                        | false    | ./terraform | Path to the Terraform working directory (default "./terraform")                                                                                                                                                                  |
| `path-file`                   | false    | plan.json   | Name of plan file to scan (default "plan.json")                                                                                                                                                                                  |
| `score-threshold`             | false    | 0           | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).                                                                  |
| `service-account-credentials` | false    |             | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                          |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Scan Terraform plan file

The following example uses HashiCorp's [setup-terraform](https://github.com/hashicorp/setup-terraform) to generate a Terraform plan file and convert it to JSON before running scan with cnspec.

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
    steps:
      - uses: actions/checkout@v3
    - uses: hashicorp/setup-terraform@v2
      with:
        terraform_wrapper: false

    - name: Terraform Init
      id: terraform-init
      run: terraform init

    - name: Convert Terraform plan to json
      id: plan-to-json
      run: |
        terraform plan -no-color -out plan.tfplan
        terraform show -json plan.tfplan >> plan.json
      continue-on-error: true

    - name: Scan Terraform plan file for security misconfigurations
      id: scan-tf-plan
      env:
        MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_CONFIG_BASE64 }}
      - uses: mondoohq/actions/terraform-plan@v2.0.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: terraform
          plan-file: plan.json
```
