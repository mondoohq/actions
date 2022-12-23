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

All Mondoo GitHub Actions require a [service account](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) to authenticate with Mondoo Platform and run policies enabled for your assets in the Policy Hub.

### Create Service Account

To create a service account on Mondoo Platform:

1. Log in to [Mondoo Platform](https://console.mondoo.com)
2. Select the Space you want to integrate with your repository.
3. Click on **Settings** and then **Service Accounts**.
4. Click **ADD ACCOUNT**.
5. Select the **Base64-encoded** checkbox, and then click on the **GENERATE NEW CREDENTIALS** button.
6. Copy the base64 encoded credentials and then move on to the next section.

### Add new GitHub Actions Secrets

1. Click on **Settings** in your GitHub repository.
2. Under the **Security** section click on **Actions**.
3. Click **New repository secret**.
4. Name the secret `MONDOO_SERVICE_ACCOUNT` and paste the base64 encoded credentials from the previous section into the value input.
5. Click **Add secret**.

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
      - uses: mondoohq/actions/k8s-manifest@v0.8.0
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

    - uses: mondoohq/actions/terraform-hcl@v0.8.0
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
        uses: mondoohq/actions/docker-image@v0.8.0
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

## Suggested setup for public repos
There are some caveats for public repositories that should be taken into account when setting up actions that should run for forks. Below we describe the default GitHub behaviour with examples, list the potential risks with it and then provide our suggested solution.

### GitHub default behaviour
Our GitHub actions require a secret (the Mondoo service account) to be able to run a scan. By default, workflows from forks do not have access to the secrets in the upstream repository. However, in certain cases it might be required that a secret is made accessible for forks. For example, a repository that uses our actions to run security and misconfiguration checks would probably want to do so for forks as well.

### The behaviour we want
We would like to explicitly approve every change in PR before it is being executed with access to our repository's secrets. Only after all changes are reviewed we can allow the PR to run with such an access.

### The solution
Assume we have the following workflow that runs for every PR:
```yaml
name: K8s Manifest Scanning
on:
  pull_request:

jobs:
  k8s-manifest-tests:
    runs-on: ubuntu-latest
    name: Test k8s manifest scanning
    steps:
      - uses: actions/checkout@v3

      - name: Scan k8s manifest
        uses: ./k8s-manifest
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: ./.github/test_files/k8s-manifest.yaml
```

It would not work for forks because we are trying to access `${{ secrets.MONDOO_SERVICE_ACCOUNT }}`. To be able to support this use-case first, let's extract the job into a reusable workflow.
```yaml
name: K8s Manifest Scanning
on:
  workflow_call:
  secrets:
    MONDOO_SERVICE_ACCOUNT:
      required: true

jobs:
  k8s-manifest-tests:
    runs-on: ubuntu-latest
    name: Test k8s manifest scanning
    steps:
      - uses: actions/checkout@v3

      - name: Scan k8s manifest
        uses: ./k8s-manifest
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          path: ./.github/test_files/k8s-manifest.yaml
```

Then we need to adjust the workflow that runs for our PRs to use the reusable workflow. We also need to make sure it runs only for non-fork PRs.
```yaml
name: K8s Manifest Scanning
on:
  pull_request:

jobs:
  k8s-manifest-tests:
    name: Test k8s manifest scanning
    # Make sure the workflow runs only for non-forks and non-dependabot PRs
    if: |
      !github.event.pull_request.head.repo.fork && github.event.pull_request.user.login != 'dependabot[bot]'
    uses: ./.github/workflows/manifest-scan.yml # <- path to the reusable workflow
    secrets:
      MONDOO_SERVICE_ACCOUNT: ${{ secrets.MONDOO_SERVICE_ACCOUNT }} # <- pass the secret to the reusable workflow
```

Then we need to define another workflow that would run only for forked PRs. We also want to make sure that it will run after an explicit approval. For that we will use the labels on the PR itself. If the `run tests` label is present, we run the tests and remove it. Otherwise, we fail the pipeline because the tests have not run and we add a comment to the PR that states that. In this way, we make sure that the tests are always executed (and not forgotten) and we also have granular control of when they are run.
```yaml
name: K8s Manifest Scanning (forks)

on:
  pull_request_target: # <- this is an important change. Makes sure that secrets are accessible to the fork
    types: [opened, synchronize, reopened, labeled]

permissions:
  contents: read

jobs:
  check-label:
    name: Check label
    runs-on: ubuntu-latest
    # If this is not a fork do not start this step
    if: ${{ github.event.pull_request.user.login == 'dependabot[bot]' || github.event.pull_request.head.repo.fork }}
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v3
        with:
          persist-credentials: false
      - name: Check whether tests are enabled for this PR
        run: |
          echo "IS_FORK=${{ github.event.pull_request.user.login == 'dependabot[bot]' || github.event.pull_request.head.repo.fork }}" >> $GITHUB_ENV
          echo "HAS_LABEL=${{ contains(github.event.pull_request.labels.*.name, 'run tests') }}" >> $GITHUB_ENV
      - name: Remove 'run tests' label
        # If the PR is created by dependabot or is a fork and has the 'run tests' label, remove it.
        # This makes sure that the tests will be run now and a follow-up change would require a new approval.
        if: ${{ env.IS_FORK == 'true' && env.HAS_LABEL == 'true' }}
        run: |
          gh pr edit ${{ github.event.pull_request.number }} --remove-label "run tests"
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        # If the tests were not enabled, then we fail the workflow. We do this instead of skipping to make sure that
        # the tests are eventually executed. Failed workflow would not allow the PR to be merged.
      - name: Fail workflow
        if: ${{ env.IS_FORK == 'true' && env.HAS_LABEL == 'false' }}
        run: |
          echo "Not all tests have run for this PR. Please add the `run tests` label to trigger them."
          exit 1
        # Here we add a comment to the PR that states whether the tests are running or not. This is an optional step.
        # We have it for clarification. It does not add new comments for every change. It will edit the existing comment instead.
      - name: Update PR comment
        uses: mshick/add-pr-comment@v2
        if: always()
        with:
          message: |
            ✅ Tests will run for this PR. Once they succeed it can be merged.
          message-failure: |
            ❌ Not all tests have run for this PR. Please add the `run tests` label to trigger them.
  tests:
    name: Test k8s manifest scanning
    needs: [check-label] # <- only run this if the check-label job was successful
    uses: ./.github/workflows/manifest-scan.yml # <- path to the reusable workflow
    secrets:
      MONDOO_SERVICE_ACCOUNT: ${{ secrets.MONDOO_SERVICE_ACCOUNT }} # <- pass the secret to the reusable workflow
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
