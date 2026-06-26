# Contributing to jh-claude-plugins

Thank you for your interest in contributing!

## Prerequisites

- [Claude Code](https://claude.com/claude-code) installed
- Git

## Code of Conduct

This project follows the [Contributor Covenant v2.1](CODE_OF_CONDUCT.md). Please read it before contributing.

## How to Add a New Plugin

1. Create `plugins/<name>/.claude-plugin/plugin.json` with name, version, description, author
2. Create `plugins/<name>/skills/<skill-name>/SKILL.md` with frontmatter (`name`, `description`) and workflow steps
3. Add the plugin entry to `.claude-plugin/marketplace.json` `plugins` array
4. Update root `README.md` plugin table

## Key Conventions

- **No runtime code.** Plugins are pure SKILL.md instructions that use Claude Code built-in tools
- **No hardcoded user paths.** Use config-driven paths with sensible relative defaults
- **SKILL.md description** must be under 120 characters

## Commit Convention

Conventional commits: `type(scope): message`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`
Scope: plugin name (e.g., `article-study`) or omit for repo-level changes.
Branch names: use `type/short-description` (e.g., `feat/new-quiz-format`, `fix/path-handling`).

Examples:
- `feat(article-study): add quiz patterns reference`
- `fix(yt-study): handle paywall fallback`
- `docs: update root README`

## Validation & Testing

```bash
# Validate plugin manifests (run from repo root, before push)
claude plugin validate .
claude plugin validate ./plugins/article-study

# Install locally for testing
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
claude plugin install article-study@jh-claude-plugins
```

## Pull Request Process

1. Fork the repository (maintainers may create branches directly)
2. Create a branch: `type/short-description` (e.g., `feat/new-quiz-format`)
3. Make your changes following the conventions above
4. Validate plugin manifests locally
5. Submit a PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
6. Await maintainer review

All PRs are **squash-merged**. Your PR title becomes the commit message on `main`, so it must follow conventional commit format: `type(scope): message`.

For security vulnerabilities, do not open a public issue — see [SECURITY.md](SECURITY.md).

## Versioning

The maintainer typically handles version bumps and CHANGELOG updates in a dedicated release PR. Contributors should not need to modify `plugin.json` version fields or `CHANGELOG.md` — if you do, CI will require both to change together.

Plugin versions follow [SemVer](https://semver.org/). The **public API surface** for each plugin is:
- User-facing setup wizard fields (`## Settings` in MEMORY.md)
- SKILL.md invocation pattern (skill name, required user inputs)
- Required external tools (e.g., yt-dlp for yt-study)
- Output format and save behavior

Bump rules:
- **major**: Breaking change to the API surface above (e.g., setup fields renamed, required tool added)
- **minor**: New feature or workflow change that does not break existing usage
- **patch**: Typos, reference doc fixes, bug fixes with no behavior change

## Releasing (Maintainers)

1. After merging contributor PRs, create a version-bump commit:
   - Update `plugins/<name>/.claude-plugin/plugin.json` version field
   - Update root `CHANGELOG.md` with new entry (Keep a Changelog format)
2. Open a PR for the version bump, merge via squash merge
3. For repo milestones: push a tag (`git tag 2026.03 && git push origin 2026.03`)
4. GitHub Actions auto-generates a Release from the tag

Repo milestone tags use **date-based format** (`YYYY.MM` or `YYYY.MM.N`), not semver — to avoid confusion with plugin versions. They are internal snapshots, not user-facing version numbers.

**When to tag:** New plugin added, any plugin major version bump, significant infra change, or quarterly milestone (optional).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
