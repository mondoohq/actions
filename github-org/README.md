# Mondoo GitHub Organization Action

A GitHub Action for using Mondoo to scan a GitHub Organization for security misconfigurations such as branch protection, CI tests, required code-review, and more. This Action can be used to audit individual GitHub repositories. This Action can be easily used in [.github or .github-private](https://docs.github.com/en/organizations/collaborating-with-groups-in-organizations/customizing-your-organizations-profile) repositories.

**_Organizations with a large number of repositories (20+) are likely to hit GitHub's API Rate Limit causing this action to fail. Please refer to the 'Using App Tokens' section below!_**

## Permissions

Depending on the amount that should be covered, you need to provide the proper permissions to the token. Since Mondoo only reads values, only read only permissions are required.

| Permission     | Description                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------- |
| read:org       | e.g. required to verify GitHub organizations                                                 |
| admin:org_hook | e.g. required to verify that all hooks use https                                             |
| repo           | Ability to read configuration, required since GitHub does not provide a repo:read permission |
| workflow       | eg. allows the verification of workflow settings                                             |
| read:packages  | e.g. allows to verify that packages are not public                                           |

## Properties

The GitHub Organization Action has properties which are passed to the underlying image. These are passed to the action using `with`.

| Property                      | Required | Default | Description                                                                                                                                                                                                                      |
| ----------------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `organization`                | true     |         | GitHub organization to scan eg. `mondoohq`.                                                                                                                                                                                      |
| `log-level`                   | false    | info    | Sets the log level: error, warn, info, debug, trace (default "info")                                                                                                                                                             |
| `output`                      | false    | compact | Set the output format for scan results: compact, yaml, json, junit, csv, summary, full, report (default "compact")                                                                                                               |
| `score-threshold`             | false    | 0       | Sets the score threshold for scans. Scores that fall below the threshold will exit 1. (default "0" - job continues regardless of the score returned by a scan).                                                                  |
| `is-cicd`                     | false    | true    | Flag to disable the auto-detection for CI/CD runs. If deactivated it reports into the Fleet view                                                                                                                                 |
| `service-account-credentials` | false    |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform. You can also use the environment variable mentioned below. |

Additionally, you need to specify the service account and GitHub credentials as an environment variable.

| Environment            | Required | Default | Description                                                                                                                                                          |
| ---------------------- | -------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MONDOO_CONFIG_BASE64` | true     |         | Base64 encoded [service account credentials](https://mondoo.com/docs/platform/service_accounts/#creating-service-accounts) used to authenticate with Mondoo Platform |
| `GITHUB_TOKEN`         | true     |         | GitHub token used for authentication                                                                                                                                 |

## Scan GitHub organization

You can use the Action as follows:

```yaml
name: Scan GitHub organization
on: push

jobs:
  scan-github-org:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: mondoohq/actions/github-org@v2.1.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          organization: ${{ GITHUB_REPOSITORY_OWNER }}
```

## Using App Tokens

> GitHub implements an [aggressive API rate limit](https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#rate-limiting) which will impact organizational scans for orgs with a large number of repositories. Normal access tokens are limited to 5,000 requests per hour. By using a GitHub App Token you can increase this limit to 15,000 per hour.

To leverage an App Token:

1. As a GitHub Organization Owner, go to your Organizational Settings and then under "Developer Settings" select "GitHub Apps". The URL is `https://github.com/organizations/<org_name>/settings/apps`.
2. Select **New GitHub App**.
3. Name the app what ever you like, we suggest "Mondoo Org Scan (Internal)" and give it a description.
4. Set the **Homepage URL** to anything, we suggest "https://mondoo.com".
5. Uncheck the **Active** button under **Webhook**.
6. Set the permissions for your Repo, Org and Account to allow Mondoo to scan the resources.
7. Select the **Only on this account** button and then select **Create GitHub App** to finish.
8. Record the App ID, then scroll down and select the **Generate a private key** button. This will download the private key that you will use later.
9. Now, select **Install App** and then **Install** next to the Org your planning to scan. You can choose All Repositories or only the rep running this action, then select **Install**.
10. Finally, update your action to include the github-app-token action and use it's output token. This will require you to add the Apps ID and Private Key to Action Secrets. The new action will look like:

```
# ....
    steps:
      - uses: actions/checkout@v3
      - name: Generate token
        id: generate_token
        uses: tibdex/github-app-token@v1
        with:
          app_id: ${{ secrets.APP_ID }}
          private_key: ${{ secrets.APP_PRIVATE_KEY }}
      - uses: mondoohq/actions/github-org@v2.1.0
        env:
          MONDOO_CONFIG_BASE64: ${{ secrets.MONDOO_SERVICE_ACCOUNT }}
          GITHUB_TOKEN: ${{ steps.generate_token.outputs.token }}
        with:
          organization: <YOUR_ORGANIZATION>
          is-cicd: false
```
