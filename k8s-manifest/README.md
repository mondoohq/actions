# Mondoo Kubernetes Manifest Action

A GitHub Action for using Mondoo to scan Kubernetes manifests for security misconfigurations.

For Kubernetes cluster scanning see Mondoo's [k8s](../k8s/) action.

## Properties

The Kubernetes Manifest Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                          |
| ----------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `args`                        | false    |         | Additional arguments to pass to Mondoo Client.                                                                                                                       |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                 |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                   |
| `path`                        | true     |         | Path to Kubernetes manifest file.                                                                                                                                    |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).      |
| `service-account-credentials` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Scan a Kubernetes manifests with Mondoo

You can use the Action as follows:

```yaml
name: Mondoo Kubernetes Manifest scan
on:
  push:
    paths:
      - "k8s/deployment.yaml"
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/k8s-manifest@main
        with:
          service-account-credentials: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          path: k8s/deployment.yaml
```
