# Mondoo policy bundle action

A GitHub Action for publishing cnspec policy bundles to Mondoo Platform.

## Service Account Permissions

![Mondoo service account with elevated permissions](../assets/service-account-permissions.png)

Adding policies to Mondoo Platform requires a [Mondoo service account](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) with elevated permissions. Use the **Space Gateway Agent** permissions to add policies to Mondoo Platform.

## Properties

The Mondoo Policy Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default  | Description                                                                                                                                                                                                                      |
| ----------------------------- | -------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`                      | false    | validate | Sets the action for cnspec bundle command: publish, validate (default "validate")                                                                                                                                                |
| `log-level`                   | false    | info     | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                             |
| `path`                        | true     |          | Path to the policy file.                                                                                                                                                                                                         |
| `service-account-credentials` | false    |          | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                          |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |

## Add a policy to Mondoo Platform

The following example runs `cnspec bundle validate` on specified policies on all pull requests. Once a PR is approved and merged the workflow will run `cnspec bundle publish` on specified policies.

```yaml
name: Mondoo Policy Add Example
on:
  push:
    paths:
      - "policy/policy.mql.yaml"

jobs:
  cnspec-policy-validate:
    name: Validate cnspec policy bundle
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/policy@scottford/updates-policy-action
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          action: validate
          path: policy/policy.mql.yaml
  cnspec-publish-bundle:
    name: Publish cnspec policy bundle
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/policy@scottford/updates-policy-action
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          action: validate
          path: policy/policy.mql.yaml
      - uses: mondoohq/actions/policy@scottford/updates-policy-action
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
        with:
          action: publish
          path: policy/policy.mql.yaml
```
