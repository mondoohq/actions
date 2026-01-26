# Mondoo Kubernetes Manifest Action

A GitHub Action for using Mondoo to scan Kubernetes manifests for security misconfigurations.

For Kubernetes cluster scanning see Mondoo's [k8s](../k8s/) action.

## Properties

The Kubernetes Manifest Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                     |
| `path`                        | true     |         | Path to Kubernetes manifest file.                                                                                                                                                                                      |
| `risk-threshold`              | false    | 101     | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).                                                        |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/maintain/access/service_accounts/) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/maintain/access/service_accounts/) used to authenticate with Mondoo Platform |

## Scan a Kubernetes manifests with Mondoo

You can use the Action as follows:

```yaml
name: Mondoo Kubernetes Manifest scan
on:
  push:
    paths:
      - "k8s/deployment.yaml"
jobs:
  scan-k8s-manifest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/k8s-manifest@v12.0.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: k8s/deployment.yaml
```
