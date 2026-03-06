# jh-claude-plugins

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Claude Code plugins for learning and productivity. Each plugin is a pure configuration-based skill (SKILL.md) that extends Claude Code with specialized workflows -- no runtime code required.

### What are Claude Code plugins?

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugins are configuration-only packages that teach Claude new skills via `SKILL.md` files. They require no runtime code -- just structured instructions that Claude follows using its built-in tools (WebFetch, Write, etc.).

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [blog-digest](plugins/blog-digest/) | Blog article digest with study quizzes | 0.1.0 |
| [youtube-digest](plugins/youtube-digest/) | YouTube video digest with adaptive depth | 1.0.0 |

## Installation

1. Add marketplace:
   ```bash
   claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
   ```

2. Install plugin:
   ```bash
   claude plugin install blog-digest@jh-claude-plugins
   ```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

[kim-jeonghyun](https://github.com/kim-jeonghyun)
