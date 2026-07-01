# Mondoo GitHub Repository Action

A [GitHub Action](https://github.com/features/actions) for using Mondoo to scan a GitHub repository for security misconfigurations such as branch protection, CI tests, required code-review, and more. This action can be used to audit individual GitHub repositories.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- A GitHub token with read permissions is required (see the Permissions section below).

## Permissions

Depending on the scope of the scan, you need to provide the proper permissions to the token. Since Mondoo only reads values, only read-only permissions are required.

| Permission    | Description                                                                                  |
| ------------- | -------------------------------------------------------------------------------------------- |
| repo          | Ability to read configuration, required since GitHub does not provide a repo:read permission |
| workflow      | e.g. allows the verification of workflow settings                                            |
| read:packages | e.g. allows you to verify that packages are not public                                       |

## Properties

The GitHub Repository Action has properties that are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `repository`                  | true     |         | GitHub repository to scan eg. `mondoohq/actions`.                                                                                                                                                                      |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                     |
| `risk-threshold`              | false    | 101     | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `is-cicd`                     | false    | true    | Flag to disable the auto-detection for CI/CD runs. If deactivated it reports into the Fleet view.                                                                                                                      |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account and GitHub credentials as environment variables.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |
| `GITHUB_TOKEN`         | true     |         | GitHub token used for authentication                                                                                                                       |

## Scan a GitHub repository

```yaml
name: Scan GitHub repository
on: push

jobs:
  scan-github-repo:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/github-repo@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          repository: ${{ github.repository }}
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
