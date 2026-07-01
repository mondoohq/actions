# Mondoo Terraform State Action

A [GitHub Action](https://github.com/features/actions) for testing [HashiCorp Terraform](https://developer.hashicorp.com/terraform) state files for security misconfigurations.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- The Terraform state must be available in the workspace.

## Properties

The Terraform State Action has properties that are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                     |
| `path`                        | true     |         | Path to the Terraform working directory.                                                                                                                                                                               |
| `risk-threshold`              | false    | 101     | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |

## Scan a Terraform state file

```yaml
name: Mondoo Terraform State scan
on:
  push:
    paths:
      - "terraform/main.tf"
jobs:
  scan-tf:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/terraform-state@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: terraform
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
