# Mondoo GitHub Action

A set of GitHub Action for using Mondoo to check for vulnerabilities and misconfigurations in your GitHub projects. Actions have been organized into different asset types that Mondoo supports. We currently support the following asset types:

- [AWS](aws) - Scan AWS accounts for misconfigurations as a post-provisioning step in your pipeline.
- [Docker Image](docker-image) - Scan Docker images vulnerabilities and misconfigurations before pushing to a container registry.
- [GitHub Organization](github-org) - Scan a GitHub organization and repositories for security configuration best practices.
- [GitHub Repository](github-repo) - Scan a GitHub repository for security configuration best practices.
- [Kubernetes](k8s) - Scan Kubernetes Clusters post-deploy for continuous auditing and compliance of the cluster.
- [Kubernetes Manifest](k8s-manifest) - Scan Kubernetes manifests for misconfigurations before applying changes to the cluster.
- [Policy](policy) - Publish Mondoo policies to Mondoo Platform using GitHub Actions.
- [Terraform HCL](terraform-hcl) - Scan HashiCorp Terraform HCL code for security misconfigurations.
- [Terraform Plan](terraform-plan) - Scan HashiCorp Terraform Plan for security misconfigurations.
- [Terraform State](terraform-state) - Scan HashiCorp Terraform State output for security misconfigurations.

## Service Accounts

All Mondoo GitHub Actions require a [service account](https://mondoo.com/docs/platform/maintain/access/service_accounts/) to authenticate with Mondoo Platform and run policies enabled for your assets in the Policy Hub.

### Create Service Account

To create a service account on Mondoo Platform:

1. Log in to [Mondoo Platform](https://console.mondoo.com)
2. Select the Space you want to integrate with your repository.
3. Select **Settings** and then **Service Accounts**.
4. Select **ADD ACCOUNT**.
5. Select the **Base64-encoded** checkbox, and then select the **GENERATE NEW CREDENTIALS** button.
6. Copy the base64 encoded credentials and then move on to the next section.

### Add new GitHub Actions Secrets

1. Select **Settings** in your GitHub repository.
2. Under the **Security** section select **Actions**.
3. Select **New repository secret**.
4. Name the secret `MONDOO_SERVICE_ACCOUNT` and paste the base64 encoded credentials from the previous section into the value input.
5. Select **Add secret**.

## Examples Workflows

Simple scan of nginx.yml Kubernetes manifest:

```yaml
name: Mondoo Kubernetes Manifest scan
on:
  push:
    paths:
      - "k8s/*.yaml"
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/k8s-manifest@v2.1.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: k8s/manifest.yaml
```

Simple scan of Terraform files:

```yaml
name: Mondoo Terraform scan
on:
  push:
    paths:
      - "terraform/main.tf"
jobs:
  steps:
    - uses: actions/checkout@v3

    - uses: mondoohq/actions/terraform-hcl@v2.1.0
      env:
        MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
      with:
        path: terraform
```

Build a Docker image before pushing to a registry:

```yaml
name: docker-build-scan-push

on:
  push:

env:
  APP: myapp
  VERSION: 0.1.0

jobs:
  docker-build-scan-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to GHCR.io
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GHCR_TOKEN }}
      - name: Build and export to Docker
        uses: docker/build-push-action@v3
        with:
          context: .
          load: true
          tags: |
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:${{env.VERSION}}
          secrets: GIT_AUTH_TOKEN=${{ secrets.GIT_AUTH_TOKEN }}
      - name: Scan Docker Image with Mondoo
        uses: mondoohq/actions/docker-image@v2.1.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          image: ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
      - name: Build and push
        uses: docker/build-push-action@v3
        with:
          context: .
          tags: |
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:${{env.VERSION}}
          push: ${{ github.ref == 'refs/heads/main' }}

      - name: Image Digest
        run: echo ${{ steps.docker_build.outputs.digest }}
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
