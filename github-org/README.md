# Mondoo GitHub Organization Action

A GitHub Action for using Mondoo to scan a GitHub Organization for security misconfigurations such as branch protection, CI tests, required code-review, and more. This Action can be used to audit individual GitHub repositories. This Action can be easily used in [.github or .github-private](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile) repositories.

## Permissions

Depending on the amount that should be covered, you need to provide the proper permissions to the token. Since Mondoo only reads values, only read only permissions are required.

| Permission     | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| read:org       | e.g. required to verify GitHub organizations                                                 |
| admin:org_hook | e.g. required to verify that all hooks use https                                             |
| repo           | Ability to read configuration, required since GitHub does not provide a repo:read permission |
| workflow       | eg. allows the verification of workflow settings                                             |
| read:packages  | e.g. allows to verify that packages are not public                                           |

## Properties

The GitHub Organization Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                          |
| ----------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `organization`                | true     |         | GitHub organization to scan eg. `mondoohq` Client.                                                                                                                   |
| `token`                       | true     |         | GitHub token used for authentication                                                                                                                                 |
| `args`                        | false    |         | Additional arguments to pass to Mondoo Client.                                                                                                                       |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                 |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                   |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).      |
| `service-account-credentials` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |
| `is-cicd`                     | false    | true    | Flag to disable the auto-detection for CI/CD runs. If deactivated it reports into the Fleet view                                                                     |

## Scan GitHub organization

You can use the Action as follows:

```yaml
name: Scan GitHub organization
on: push

jobs:
  scan-github-org:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/k8s@main
        with:
          organization: ${{ GITHUB_REPOSITORY_OWNER }}
          service-account-credentials: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
```
