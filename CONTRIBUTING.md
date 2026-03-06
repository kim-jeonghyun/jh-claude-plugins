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
Scope: plugin name (e.g., `blog-digest`) or omit for repo-level changes.

Examples:
- `feat(blog-digest): add quiz patterns reference`
- `fix(blog-digest): handle paywall fallback`
- `docs: update root README`

## Validation & Testing

```bash
# Validate plugin manifests (run from repo root, before push)
claude plugin validate .
claude plugin validate ./plugins/blog-digest

# Install locally for testing
claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
claude plugin install blog-digest@jh-claude-plugins
```

## Pull Request Process

1. Fork the repository
2. Create your changes following the conventions above
3. Validate plugin manifests locally
4. Submit a PR using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
5. Await maintainer review

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
