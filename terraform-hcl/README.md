# Mondoo Terraform HCL Action

A [GitHub Action](https://github.com/features/actions) for testing [HashiCorp Terraform](https://terraform.io) [HCL code]](https://www.terraform.io/language/syntax/configuration) for security misconfigurations.

## Properties

The Terraform Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                          |
| ----------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `args`                        | false    |         | Additional arguments to pass to Mondoo Client.                                                                                                                       |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                 |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                   |
| `path`                        | true     |         | Path to the Terraform working directory.                                                                                                                             |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).      |
| `service-account-credentials` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Scan Terraform working directory

You can use the Action as follows:

```yaml
name: Mondoo Terraform scan
on:
  push:
    paths:
      - "terraform/main.tf"
jobs:
  steps:
    - uses: actions/checkout@v3
    - uses: mondoohq/actions/terraform@main
      with:
        service-account-credentials: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        path: terraform
```
