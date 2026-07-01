# Mondoo xgrep Action

A [GitHub Action](https://github.com/features/actions) that runs [xgrep](https://mondoo.com/docs/xgrep/), a Semgrep-compatible SAST scanner, and produces a [SARIF](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) report so findings show up in GitHub code scanning.

The action runs `xgrep ci`, which auto-detects the CI environment, scans **diff-aware** against the pull request base on PRs, and uses xgrep's built-in `security` and `secrets` rules by default. No Mondoo Platform service account or authentication is required.

## Requirements

- Node.js is required to install the `@mondoohq/xgrep` npm package. It is preinstalled on GitHub-hosted runners; on self-hosted runners add [`actions/setup-node`](https://github.com/actions/setup-node) before this action.
- For diff-aware scanning on pull requests, check out the full git history with `fetch-depth: 0`.

## Properties

The xgrep Action has properties that are passed to the action using `with`.

| Property         | Required | Default         | Description                                                                                             |
| ---------------- | -------- | --------------- | ------------------------------------------------------------------------------------------------------- |
| `path`           | false    | `.`             | Path(s) to scan.                                                                                        |
| `rules`          | false    | `""`            | Path to a custom rule file or directory. When empty, xgrep's built-in security and secrets rules run.   |
| `with-builtin`   | false    | `""`            | When `rules` is set, also run these built-in categories (comma-separated, e.g. `security,secrets`).     |
| `output-file`    | false    | `results.sarif` | Path for the SARIF report file.                                                                         |
| `version`        | false    | `latest`        | Version of the `@mondoohq/xgrep` npm package to install. Pin (e.g. `0.9.0`) for reproducible scans.     |
| `sarif-category` | false    | `xgrep`         | SARIF category. Must match the `category` used when uploading the SARIF.                                |
| `fail-on`        | false    | `off`           | Fail the job when findings exist at or above this severity: `off` (report only), `error`, or `warning`. |
| `args`           | false    | `""`            | Extra raw flags passed through to `xgrep ci` (e.g. `--exclude vendor --decode`).                        |

## Outputs

| Output       | Description                         |
| ------------ | ----------------------------------- |
| `sarif-file` | Path to the generated SARIF report. |

## Scan a repository for security issues

```yaml
name: xgrep

on:
  push:
    branches:
      - main
  pull_request:

permissions:
  contents: read
  security-events: write # required to upload SARIF

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v7
        with:
          fetch-depth: 0 # required for diff-aware scanning on pull requests
      - name: Run xgrep
        uses: mondoohq/actions/xgrep@v13.3.0
        with:
          path: .
          output-file: "results.sarif"
      - name: Upload SARIF results file
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
          category: xgrep
```

## Fail the build on findings

By default the action only reports findings to code scanning. To make the job fail when findings are present, set `fail-on`:

```yaml
- name: Run xgrep
  uses: mondoohq/actions/xgrep@v13.3.0
  with:
    fail-on: error # or 'warning'
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
