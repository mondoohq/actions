# Mondoo cnspec lint Action

A [GitHub Action](https://github.com/features/actions) that runs `cnspec bundle lint` on cnspec policy bundles and produces a [SARIF](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) report so lint results show up in GitHub code scanning.

No Mondoo Platform service account or authentication is required.

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- Uploading the SARIF report to GitHub code scanning requires the `security-events: write` permission.

## Properties

The cnspec lint Action has properties that are passed to the action using `with`.

| Property      | Required | Default         | Description                                          |
| ------------- | -------- | --------------- | ---------------------------------------------------- |
| `path`        | true     | `.`             | Specifies the root path of the bundles.              |
| `output-file` | true     | `results.sarif` | Specifies the output path for the SARIF report file. |

## Lint policy bundles

```yaml
name: Lint Policies

on:
  pull_request:
  push:
    branches:
      - main

permissions:
  contents: read
  security-events: write # required to upload SARIF

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7
      - name: Lint Policies
        uses: mondoohq/actions/cnspec-lint@v13.2.0
        with:
          path: .
          output-file: "results.sarif"
      - name: Upload SARIF results file
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
