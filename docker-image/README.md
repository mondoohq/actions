# Mondoo Docker Action

A GitHub Action for using Mondoo to check for vulnerabilities and misconfigurations in your Docker container images. 

## Properties

The Mondoo Docker Image Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                          |
|-------------------------------|----------|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `args`                        | false    |         | Additional arguments to pass to Mondoo Client.                                                                                                                              |
| `image`                       | true     |         | Docker image ID or `name:tag` to scan.                                                                                                                               |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                 |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                   |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).      |
| `service-account-credentials` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

You can use the Action as follows:

## Docker build scan and push to GHCR.io

The following example uses the Docker [build-push-action](https://github.com/marketplace/actions/build-and-push-docker-images) to build a Docker container, scan the built container with Mondoo, and then push to ghcr.io. Use the `score-threshold` property to ensure builds meet security requirements before publishing. 

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
      - 
        name: Checkout 
        uses: actions/checkout@v2
      -
        name: Set up QEMU
        uses: docker/setup-qemu-action@v2
      -
        name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      -
        name: Login to GHCR.io
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GHCR_TOKEN }}
      -
        name: Build and export to Docker
        uses: docker/build-push-action@v3
        with:
          context: .
          load: true
          tags: |
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:${{env.VERSION}}
          secrets: 
            GIT_AUTH_TOKEN=${{ secrets.GIT_AUTH_TOKEN }}
      -
        name: Scan Docker Image
        uses: mondoohq/actions/docker-image@master
        with:
          service-account-credentials: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          image: ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
      -
        name: Build and push
        uses: docker/build-push-action@v3
        with:
          context: .
          tags: |
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:latest
            ghcr.io/${{github.repository_owner}}/${{env.APP}}:${{env.VERSION}}
          push: ${{ github.ref == 'refs/heads/main' }}
      
      - 
        name: Image Digest
        run: echo ${{ steps.docker_build.outputs.digest }}
```
