# Mondoo cnspec lint Action

A [GitHub Action](https://github.com/features/actions) for linting cnspec policy bundles with Sarif output.

## Properties

The cnspec lint Action has properties that are passed to the action using `with`.

| Property      | Required | Default         | Description                                           |
| ------------- | -------- | --------------- | ----------------------------------------------------- |
| `path`        | true     | `.`             | Specifies the root path of the bundles .              |
| `output-file` | true     | `results.sarif` | Specifies the output path for the sarif report file'. |

## Scan policy bundles for lint errors

You can use the Action as follows:

```yaml
name: Lint Policies

on:
  pull_request:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      - name: Lint Policies
        uses: github/mondoohq/actions/cnspec-lint
        with:
          path: .
          output-file: "results.sarif"
      - name: Upload SARIF results file
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: results.sarif
```
