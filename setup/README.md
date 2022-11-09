# Mondoo Setup Action

A [GitHub Action](https://github.com/features/actions) for installing [Mondoo Client](https://mondoo.com/docs/tutorials/mondoo/download-and-install/) within a workflow.

## Properties

The Mondoo Setup Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property    | Required | Default | Description                                                                                                        |
| ----------- | -------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| `log-level` | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                               |
| `output`    | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact") |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                          |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Mondoo Setup example

Use this action to install Mondoo into an existing workflow and run `mondoo` along with any subcommands using the `args` property:

```yaml
name: Mondoo status
on: push
jobs:
  install:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/setup@main
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
```
