# Mondoo GitHub Action

With the Mondoo [GitHub Action](https://github.com/features/actions) you can scan Kubernetes manifests and Terraform configuration files for common security misconfigurations. These results are available in the GitHub Actions UI as well as the Mondoo console.

## Configuration Options

**service_account_credentials**

The Mondoo service account credentials. These should be stored in a GitHub secret and not set in the workflow configuration file directly. ex: `${{ secrets.MONDOO_AGENT_ACCOUNT }}`

**path**

The file to scan with Mondoo. ex: `nginx.yml`

**scan_type**

The scan type to perform. `k8s` for Kubernetes Manifest scanning or `tf` for Terraform configuration file scanning.

## Mondoo Service Account Setup

To fetch polices and send scan results to the Mondoo Platform you'll need to configure a Mondoo service account in your GitHub repository. This account should be securely stored using the GitHub Secrets feature.

In the Mondoo console go to Settings -> Service Accounts and click Add Acccount:
![Service Accounts Page](/assets/service_account.png)

In the left menu select Download Credentials, click Generate New Credentials and copy the generated credentials:
![Generate Credentials](/assets/credentials.png)

In your GitHub repo go to Settings -> Secrets and create a new secret named "MONDOO_AGENT_ACCOUNT" with the contents you copied from the Mondoo Console:
![Generate Credentials](/assets/secret.png)

## Examples Workflow

Simple scan of nginx.yml Kubernetes manifest:

```yaml
name: mondoo

on:
  pull_request:
  branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Scan with Mondoo
        uses: mondoohq/actions@main
        with:
          service_account_credentials: ${{ secrets.MONDOO_AGENT_ACCOUNT }}
          scan_type: 'k8s'
          path: 'nginx.yml'
```
