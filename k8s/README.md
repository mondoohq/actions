# Mondoo Kubernetes Cluster Action

A GitHub Action for using Mondoo to scan Kubernetes clusters for security vulnerabilities and misconfigurations. This Action can be used as a post-deploy job to provide continuous auditing of your cluster. This action requires a valid `KUBECONFIG` with access to the cluster(s) to be scanned.

For Kubernetes manifest scanning see Mondoo's [k8s-manifest](../k8s-manifest/) action.

## Properties

The Kubernetes Cluster Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property          | Required | Default | Description                                                                                                                                                     |
| ----------------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `args`            | false    |         | Additional arguments to pass to cnspec client.                                                                                                                  |
| `log-level`       | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                            |
| `output`          | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                              |
| `score-threshold` | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan). |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                          |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Scan Kubernetes cluster

You can use the Action as follows:

```yaml
name: Scan Kubernetes cluster
on: push

env:
  KUBECONFIG: ${{ secrets.KUBECONFIG }}

jobs:
  scan-k8s-cluster:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/k8s@main
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
```
