# Mondoo Kubernetes Cluster Action

A [GitHub Action](https://github.com/features/actions) for using Mondoo to scan Kubernetes clusters for security vulnerabilities and misconfigurations. This action can be used as a post-deploy job to provide continuous auditing of your cluster.

For Kubernetes manifest scanning see Mondoo's [k8s-manifest](../k8s-manifest/) action.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- A valid `KUBECONFIG` with access to the cluster(s) to be scanned must be available to the runner.

## Properties

The Kubernetes Cluster Action has properties that are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                     |
| `risk-threshold`              | false    | 101     | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |

## Scan a Kubernetes cluster

```yaml
name: Scan Kubernetes cluster
on: push

env:
  KUBECONFIG: ${{ secrets.KUBECONFIG }}

jobs:
  scan-k8s-cluster:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/k8s@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
