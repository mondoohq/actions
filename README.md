# Mondoo GitHub Action

With the Mondoo [GitHub Action](https://github.com/features/actions) you can scan Kubernetes manifests and Terraform configuration files for common security misconfigurations. These results are available in the GitHub Actions UI as well as the Mondoo console.

## Securely Store Credentials

To fetch polices and send scan results to the Mondoo Platform, configure a Mondoo service account in your GitHub repository. Store this account securely using a [GitHub Actions Secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).

In the Mondoo console, go to Integrations and click Add Another Integration:
![Add Another Integration](/assets/add_integration.png)

Scroll to the Supply Chain section and click Generate Long-Lived Credentials.

![Supply Chain Section](/assets/supply_chain.png)

Check the Base64-encoded checkbox, click Generate New Credentials, and copy the generated credentials:
![Generate Credentials](/assets/credentials.png)

In your GitHub repo, go to Settings -> Secrets -> Actions and click New repository secret. Create a new secret named "MONDOO_CLIENT_ACCOUNT" with the contents you copied from the Mondoo Console:
![Generate Credentials](/assets/secret.png)

## Workflow Configuration Options

The Mondoo GitHub Action has three required `with` values that must be set in your workflow configuration file:

**service_account_credentials**

The Mondoo service account credentials. Store these in a GitHub secret. Do not set them directly in the workflow configuration file. Once a secret is set up (as shown above) you can reference that secret in your workflow configuration file as `${{ secrets.MONDOO_CLIENT_ACCOUNT }}`.

**scan_type**

The type of Mondoo scan to perform:

- `k8s` for Kubernetes manifest scanning.
- `terraform` for Terraform configuration file scanning.
- `docker_image` for scanning of Docker images from a Docker registry or from earlier GitHub actions steps.
- `docker_image_from_dockerfile` for scanning of Docker images from a Dockerfile. Note: This will build and then scan the image which make be a lengthy process.

**path**

The file to scan with Mondoo or, if `scan_type` is set to `docker_image_from_dockerfile`, the path to the Dockerfile. Examples: `nginx.yml` or `Dockerfile`

**docker_image_name**

The container image name to scan when `scan_type` is set to `docker_image`. ex: `nginx:22.04`

**score_threshold**

The score threshold for scans. Value can be any number from `0-100`. If any score falls below the threshold, exit 1. Default value is `0`.

**output_format**

Set the output format (`compact`|`full`|`csv`|`json`|`junit`|`yaml`). Default `compact`.

**extra_args**

Allows specify extra command-line arguments for the Mondoo scan command.

## Examples Workflows

Simple scan of nginx.yml Kubernetes manifest:

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
          service_account_credentials: ${{ secrets.MONDOO_CLIENT_ACCOUNT }}
          scan_type: k8s
          path: nginx.yml
```

Simple scan of Terraform files:

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
          service_account_credentials: ${{ secrets.MONDOO_CLIENT_ACCOUNT }}
          scan_type: terraform
          path: '*.tf'
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
          service_account_credentials: ${{ secrets.MONDOO_CLIENT_ACCOUNT }}
          scan_type: docker_image_from_dockerfile
          path: Dockerfile
```

Scan a Docker image from a previous built image or image in a registry:

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
          service_account_credentials: ${{ secrets.MONDOO_CLIENT_ACCOUNT }}
          scan_type: docker_image
          docker_image_name: ubuntu:22.04
```

Build a Docker container from a Dockerfile, scan the container, and configure `output_format` and `score_threshold`:

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
          service_account_credentials: ${{ secrets.MONDOO_CLIENT_ACCOUNT }}
          scan_type: docker_image_from_dockerfile
          path: Dockerfile
          output_format: json
          score_threshold: 80
```
