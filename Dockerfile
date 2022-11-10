# use latest for now, move to major version tag later:
# https://github.com/mondoohq/cnspec/issues/174
# hadolint ignore=DL3007
FROM mondoo/cnspec:latest

COPY scripts/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]