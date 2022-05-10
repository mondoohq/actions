# Mondoo GitHub Action

With the Mondoo [GitHub Action](https://github.com/features/actions) you can scan Kubernetes manifests and Terraform configuration files for common security misconfigurations. These results are available in the GitHub Actions UI as well as the Mondoo console.

## Mondoo Service Account Setup

To fetch polices and send scan results to the Mondoo Platform you'll need to configure a Mondoo service account in your GitHub repository. This account should be securely stored using a [GitHub Actions Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).

In the Mondoo console go to Settings -> Service Accounts and click Add Acccount:
![Service Accounts Page](/assets/service_account.png)

In the left menu select Download Credentials, click Generate New Credentials and copy the generated credentials:
![Generate Credentials](/assets/credentials.png)

In your GitHub repo go to Settings -> Secrets and create a new secret named "MONDOO_AGENT_ACCOUNT" with the contents you copied from the Mondoo Console:
![Generate Credentials](/assets/secret.png)

## Configuration Options

The Mondoo GitHub Action has three required `with` values that must be set in your workflow configuration file:

**service_account_credentials**

The Mondoo service account credentials. These should be stored in a GitHub secret and not set in the workflow configuration file directly. Once a secret is setup as shown above you can reference that secret in your workflow configuration file as `${{ secrets.MONDOO_AGENT_ACCOUNT }}`.

**scan_type**

The type of Mondoo scan to perform:

- `docker_image_from_dockerfile` for scanning of Docker images from a Dockerfile. Note: This will build and then scan the image which make be a lengthy process.
- `docker_image` for scanning of Docker images from a Docker registry or from earlier GitHub actions steps.
- `k8s` for Kubernetes Manifest scanning.
- `tf` for Terraform configuration file scanning.

**path**

The file to scan with Mondoo or the path to the Dockerfile if `scan_type` is set to `docker_image_from_dockerfile`. ex: `nginx.yml` or `Dockerfile`

**docker_image_name**

The container image name to scan when `scan_type` is set to `docker_image`. ex: `nginx:22.04`

## Examples Workflows

Simple scan of nginx.yml Kubernetes manifest:

```yaml
name: mondoo

on:
  pull_request:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Scan with Mondoo
        uses: mondoohq/actions@main
        with:
          service_account_credentials: ${{ secrets.MONDOO_AGENT_ACCOUNT }}
          scan_type: k8s
          path: nginx.yml
```

Build a Docker container from a Dockerfile and scan the container:

```yaml
name: mondoo-scan

on:
  pull_request:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Scan with Mondoo
        uses: mondoohq/actions@main
        with:
          service_account_credentials: ${{ secrets.MONDOO_AGENT_ACCOUNT }}
          scan_type: docker_image_from_dockerfile
          path: Dockerfile
```

Scan a docker container from a previous built image or image in a registry:

```yaml
name: mondoo-scan

on:
  pull_request:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
      - name: Scan with Mondoo
        uses: mondoohq/actions@main
        with:
          service_account_credentials: ${{ secrets.MONDOO_AGENT_ACCOUNT }}
          scan_type: docker_image
          docker_image_name: ubuntu:22.04
```
