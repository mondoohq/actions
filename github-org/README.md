# Mondoo GitHub Organization Action

A [GitHub Action](https://github.com/features/actions) for using Mondoo to scan a GitHub organization for security misconfigurations such as branch protection, CI tests, required code-review, and more. This action can be used to audit a GitHub organization and its repositories, and is easily used in [.github or .github-private](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile) repositories.

**_Organizations with a large number of repositories (20+) are likely to hit GitHub's API Rate Limit causing this action to fail. Please refer to the 'Using App Tokens' section below!_**

## Requirements

- This is a Docker container action and runs only on Linux runners (e.g. `ubuntu-latest`).
- A [Mondoo service account](https://mondoo.com/docs/maintain/access/non-human/service_accounts) is required to authenticate with Mondoo Platform (see `MONDOO_CONFIG_BASE64` below).
- A GitHub token with read permissions is required (see the Permissions section below).

## Permissions

Depending on the scope of the scan, you need to provide the proper permissions to the token. Since Mondoo only reads values, only read-only permissions are required.

| Permission     | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| read:org       | e.g. required to verify GitHub organizations                                                 |
| admin:org_hook | e.g. required to verify that all hooks use https                                             |
| repo           | Ability to read configuration, required since GitHub does not provide a repo:read permission |
| workflow       | e.g. allows the verification of workflow settings                                            |
| read:packages  | e.g. allows you to verify that packages are not public                                       |

## Properties

The GitHub Organization Action has properties that are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                            |
| ----------------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `organization`                | true     |         | GitHub organization to scan eg. `mondoohq`.                                                                                                                                                                            |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                   |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                     |
| `risk-threshold`              | false    | 101     | Fail the job (exit status 1) if any risk score is greater than or equal to this value. Risk scores range from 0 to 100, so the default of "101" never fails the job.                                                   |
| `is-cicd`                     | false    | true    | Flag to disable the auto-detection for CI/CD runs. If deactivated it reports into the Fleet view.                                                                                                                      |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account and GitHub credentials as environment variables.

| Environment            | Required | Default | Description                                                                                                                                                |
| ---------------------- | -------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/maintain/access/non-human/service_accounts) used to authenticate with Mondoo Platform |
| `GITHUB_TOKEN`         | true     |         | GitHub token used for authentication                                                                                                                       |

## Scan a GitHub organization

```yaml
name: Scan GitHub organization
on: push

jobs:
  scan-github-org:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: mondoohq/actions/github-org@v13.3.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          organization: ${{ github.repository_owner }}
```

## Using App Tokens

> GitHub implements an [aggressive API rate limit](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) which will impact organizational scans for orgs with a large number of repositories. Normal access tokens are limited to 5,000 requests per hour. By using a GitHub App Token you can increase this limit to 15,000 per hour.

To leverage an App Token:

1. As a GitHub Organization Owner, go to your Organizational Settings and then under "Developer Settings" select "GitHub Apps". The URL is `https://github.com/organizations/<org_name>/settings/apps`.
2. Select **New GitHub App**.
3. Name the app whatever you like, we suggest "Mondoo Org Scan (Internal)" and give it a description.
4. Set the **Homepage URL** to anything, we suggest "https://mondoo.com".
5. Uncheck the **Active** button under **Webhook**.
6. Set the permissions for your Repo, Org and Account to allow Mondoo to scan the resources.
7. Select the **Only on this account** button and then select **Create GitHub App** to finish.
8. Record the App ID, then scroll down and select the **Generate a private key** button. This will download the private key that you will use later.
9. Now, select **Install App** and then **Install** next to the Org you're planning to scan. You can choose All Repositories or only the repo running this action, then select **Install**.
10. Finally, update your action to include the github-app-token action and use its output token. This will require you to add the App ID and Private Key to Action Secrets. The new action will look like:

```yaml
# ....
steps:
  - uses: actions/checkout@v7
  - name: Generate token
    id: generate_token
    uses: actions/create-github-app-token@v3
    with:
      app-id: ${{ secrets.APP_ID }}
      private-key: ${{ secrets.APP_PRIVATE_KEY }}
  - uses: mondoohq/actions/github-org@v13.3.0
    env:
      MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
      GITHUB_TOKEN: ${{ steps.generate_token.outputs.token }}
    with:
      organization: <YOUR_ORGANIZATION>
      is-cicd: false
```

## Join the community!

Join the [Mondoo Community GitHub Discussions](https://github.com/orgs/mondoohq/discussions) to collaborate on policy as code and security automation.

## License

[Mozilla Public License v2.0](https://github.com/mondoohq/actions/blob/main/LICENSE)
