# Mondoo Terraform HCL Action

A [GitHub Action](https://github.com/features/actions) for testing [HashiCorp Terraform](https://developer.hashicorp.com/terraform) [HCL code](https://developer.hashicorp.com/terraform/language/syntax/configuration) for security misconfigurations.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- The Terraform HCL files must be checked out into the workspace (use [`actions/checkout`](https://github.com/actions/checkout)).

## Properties

The Terraform HCL Action has properties that are passed to the action using `with`.

| Property                      | Required | Default       | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info          | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact       | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report, sarif (default "compact")                                                                                              |
| `output-file`                 | false    | results.sarif | Path to write the scan report to. Combine with `output: sarif` to produce a SARIF report you can upload to GitHub code scanning.                                                                                       |
| `path`                        | true     |               | Path to the Terraform working directory.                                                                                                                                                                               |
| `risk-threshold`              | false    | 101           | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `service-account-credentials` | false    |               | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |

## Scan a Terraform working directory

```yaml
name: Mondoo Terraform scan
on:
  push:
    paths:
      - "terraform/main.tf"
jobs:
  scan-tf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/terraform-hcl@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: terraform
```

## Report findings to GitHub code scanning

Set `output: sarif` to write a [SARIF](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) report, then upload it so findings appear in the repository's Security tab and on pull requests.

```yaml
name: Mondoo Terraform scan
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  security-events: write # required to upload SARIF

jobs:
  scan-tf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/terraform-hcl@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: terraform
          output: sarif
          output-file: results.sarif
      - name: Upload SARIF results file
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: results.sarif
```

> The report file is always written (default `results.sarif`, via cnspec's `--output-target`); it contains SARIF only when `output: sarif` is set.

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
