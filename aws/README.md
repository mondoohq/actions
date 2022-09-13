# Mondoo AWS Action

A GitHub Action for using Mondoo to check for misconfigurations in your AWS accounts. This action can be used as a post-provisioning step when making changes to your AWS account.

## Properties

The Mondoo AWS Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                          |
| ----------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `args`                        | false    |         | Additional arguments to pass to Mondoo Client.                                                                                                                       |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                 |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                   |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).      |
| `service-account-credentials` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Scan AWS account example

You can use the AWS Action as follows:

```yaml
name: Scan AWS account
on: push

jobs:
  scan-aws-account:
    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-region: us-east-2
          role-to-assume: arn:aws:iam::123456789100:role/my-github-actions-role
          role-session-name: MySessionName

      - uses: mondoohq/actions/aws@main
        with:
          service-account-credentials: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          output: compact
          score-threshold: 0
```
