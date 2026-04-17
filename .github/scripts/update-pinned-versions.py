#!/usr/bin/env python3
"""Scan workflow files for # auto-update annotations and propose version bumps.

Annotation format (place directly above the version line):

    # auto-update: source=github-releases repo=owner/repo
    version: v1.2.3

Optional ignore= constraint (aligned with Dependabot's update-types syntax)
controls which semver bumps to skip:

    ignore=major         — skip major bumps (allow minor + patch)
    ignore=minor         — skip minor bumps (allow major + patch)
    ignore=patch         — skip patch bumps (allow major + minor)
    ignore=major,minor   — skip major and minor (allow patch only)
    ignore=major,patch   — skip major and patch (allow minor only)
    ignore=minor,patch   — skip minor and patch (allow major only)

When omitted, all update types are allowed (equivalent to Dependabot's default).

Examples:

    # Only allow minor and patch updates (skip major):
    # auto-update: source=github-releases repo=goreleaser/goreleaser ignore=major
    version: v2.15.3

    # Only allow patch updates:
    # auto-update: source=github-releases repo=actions/checkout ignore=major,minor
    version: v6.0.2

    # Allow all updates (default):
    # auto-update: source=github-releases repo=hashicorp/terraform
    version: v1.9.0

Requirements:
    - Versions must be strict semver (v0.0.0), no pre-release suffixes
    - The version must appear exactly once on the line following the annotation
    - Only github-releases (not raw tags) are supported as a source
    - Python 3.8+ (available on all GitHub Actions ubuntu runners)
"""

import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SEMVER_RE = re.compile(r"\bv(\d+)\.(\d+)\.(\d+)\b")
ANNOTATION_RE = re.compile(r"#\s*auto-update:\s*(.*)")
KV_RE = re.compile(r"(\w+)=(\S+)")

BUMP_TYPES = {"major", "minor", "patch"}
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")


@dataclass
class SemVer:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, s: str) -> "SemVer | None":
        m = SEMVER_RE.search(s)
        if not m:
            return None
        return cls(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __gt__(self, other: "SemVer") -> bool:
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )


def bump_type(current: SemVer, latest: SemVer) -> str | None:
    """Return 'major', 'minor', or 'patch' describing what changed, or None if equal."""
    if latest.major != current.major:
        return "major"
    if latest.minor != current.minor:
        return "minor"
    if latest.patch != current.patch:
        return "patch"
    return None


def parse_ignore(ignore_str: str) -> set[str]:
    """Parse a comma-separated ignore string into a set of bump types.

    Returns an empty set if ignore_str is empty (allow all).
    Raises ValueError if any token is not a valid bump type.
    """
    if not ignore_str:
        return set()
    types = {t.strip() for t in ignore_str.split(",")}
    invalid = types - BUMP_TYPES
    if invalid:
        raise ValueError(
            f"invalid ignore types: {', '.join(sorted(invalid))}; "
            f"must be a comma-separated list of: {', '.join(sorted(BUMP_TYPES))}"
        )
    return types


def is_allowed(current: SemVer, latest: SemVer, ignored: set[str]) -> bool:
    """Check if the update from current to latest is allowed given ignored bump types."""
    bt = bump_type(current, latest)
    if bt is None:
        return False
    return bt not in ignored


def warn(msg: str) -> None:
    print(f"::warning::{msg}", flush=True)


def gh_api(endpoint: str) -> str | None:
    """Call gh api and return stdout, or None on error."""
    result = subprocess.run(
        ["gh", "api", endpoint, "--jq", ".tag_name"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


@dataclass
class Update:
    repo: str
    current: SemVer
    latest: SemVer
    file: str
    line_no: int
    ignored: set[str]

    @property
    def ignore_label(self) -> str:
        """Human-readable label for the ignore constraint."""
        if not self.ignored:
            return ""
        return f"ignore={','.join(sorted(self.ignored))}"


def parse_annotation(line: str) -> dict[str, str] | None:
    """Parse a # auto-update: key=value key=value line into a dict."""
    m = ANNOTATION_RE.search(line)
    if not m:
        return None
    return dict(KV_RE.findall(m.group(1)))


def scan_file(filepath: Path) -> list[Update]:
    """Scan a single file for auto-update annotations."""
    updates = []
    lines = filepath.read_text().splitlines()

    for i, line in enumerate(lines):
        attrs = parse_annotation(line)
        if attrs is None:
            continue
        if attrs.get("source") != "github-releases":
            continue

        repo = attrs.get("repo", "")
        if not repo or not REPO_RE.match(repo):
            warn(f"Invalid repo '{repo}' in annotation at {filepath}:{i + 1}")
            continue

        # Parse ignore constraint
        ignore_str = attrs.get("ignore", "")
        try:
            ignored = parse_ignore(ignore_str)
        except ValueError as e:
            warn(f"{e} at {filepath}:{i + 1}")
            continue

        # Version is on the next line
        version_line_no = i + 1
        if version_line_no >= len(lines):
            warn(f"Annotation at {filepath}:{i + 1} has no following line")
            continue

        version_line = lines[version_line_no]
        m = SEMVER_RE.search(version_line)
        if not m:
            warn(
                f"No semver found on line {version_line_no + 1} of {filepath} "
                f"(annotation for {repo})"
            )
            continue
        current = SemVer(int(m.group(1)), int(m.group(2)), int(m.group(3)))

        # Fetch latest release
        tag = gh_api(f"repos/{repo}/releases/latest")
        if not tag:
            warn(f"Failed to fetch latest release for {repo}")
            continue

        latest = SemVer.parse(tag)
        if not latest:
            warn(f"Latest tag '{tag}' for {repo} is not strict semver")
            continue

        if not latest > current:
            print(f"Up to date: {repo} {current} in {filepath}:{version_line_no + 1}")
            continue

        if not is_allowed(current, latest, ignored):
            bt = bump_type(current, latest)
            print(
                f"Skipped: {repo} {current} -> {latest} "
                f"({bt} bump blocked by ignore={','.join(sorted(ignored))}) "
                f"in {filepath}:{version_line_no + 1}"
            )
            continue

        print(
            f"Update available: {repo} {current} -> {latest} "
            f"in {filepath}:{version_line_no + 1}"
        )
        updates.append(
            Update(
                repo=repo,
                current=current,
                latest=latest,
                file=str(filepath),
                line_no=version_line_no + 1,  # 1-indexed
                ignored=ignored,
            )
        )

    return updates


def apply_updates(updates: list[Update]) -> None:
    """Apply version updates to files."""
    for u in updates:
        path = Path(u.file)
        lines = path.read_text().splitlines()
        line_idx = u.line_no - 1  # 0-indexed
        old_line = lines[line_idx]
        new_line = old_line.replace(str(u.current), str(u.latest), 1)
        if old_line == new_line:
            warn(f"Failed to replace {u.current} on line {u.line_no} of {u.file}")
            continue
        lines[line_idx] = new_line
        path.write_text("\n".join(lines) + "\n")
        print(f"Updated {u.file}:{u.line_no}: {u.current} -> {u.latest}")


def build_summary(updates: list[Update]) -> str:
    """Build a markdown summary grouped by repo."""
    lines = []
    prev_repo = ""
    for u in updates:
        if u.repo != prev_repo:
            safe_repo = u.repo.replace("`", "")
            lines.append(f"### [`{safe_repo}`](https://github.com/{safe_repo})")
            lines.append(
                f"Release notes: https://github.com/{safe_repo}/releases/tag/{u.latest}"
            )
            lines.append("")
            prev_repo = u.repo
        safe_file = u.file.replace("`", "")
        constraint = f" ({u.ignore_label})" if u.ignore_label else ""
        lines.append(
            f"- `{safe_file}:{u.line_no}`: `{u.current}` -> `{u.latest}`{constraint}"
        )
    return "\n".join(lines)


def set_output(name: str, value: str) -> None:
    """Set a GitHub Actions output variable."""
    output_file = os.environ.get("GITHUB_OUTPUT", "")
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"{name}={value}\n")


def set_env(name: str, value: str) -> None:
    """Set a GitHub Actions environment variable (multiline-safe)."""
    env_file = os.environ.get("GITHUB_ENV", "")
    if env_file:
        delimiter = f"ghadelim_{os.urandom(8).hex()}"
        with open(env_file, "a") as f:
            f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")


def main() -> None:
    scan_path = os.environ.get("SCAN_PATH", ".github/")
    root = Path(scan_path)

    if not root.exists():
        warn(f"Scan path '{scan_path}' does not exist")
        set_output("has_updates", "false")
        sys.exit(0)

    files = sorted(set(root.rglob("*.yml")) | set(root.rglob("*.yaml")))

    all_updates: list[Update] = []
    for filepath in files:
        all_updates.extend(scan_file(filepath))

    if not all_updates:
        print("All annotated versions are up to date.")
        set_output("has_updates", "false")
        sys.exit(0)

    set_output("has_updates", "true")
    apply_updates(all_updates)

    summary = build_summary(all_updates)
    set_env("SUMMARY", summary)


if __name__ == "__main__":
    main()
