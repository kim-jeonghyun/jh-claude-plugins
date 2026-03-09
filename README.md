# jh-claude-plugins

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Claude Code plugins for learning and productivity. Each plugin is a pure configuration-based skill (SKILL.md) that extends Claude Code with specialized workflows -- no runtime code required.

### What are Claude Code plugins?

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugins are configuration-only packages that teach Claude new skills via `SKILL.md` files. They require no runtime code -- just structured instructions that Claude follows using its built-in tools (WebFetch, Write, etc.).

## Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [article-study](plugins/article-study/) | Blog/web article study notes with comprehension quizzes | 0.2.0 |
| [yt-study](plugins/yt-study/) | YouTube video study notes with adaptive depth | 1.1.0 |

## Installation

1. Add marketplace:
   ```bash
   claude plugin marketplace add kim-jeonghyun/jh-claude-plugins
   ```

2. Install a plugin:
   ```bash
   # Blog/web article study notes
   claude plugin install article-study@jh-claude-plugins

   # YouTube video study notes (requires yt-dlp)
   claude plugin install yt-study@jh-claude-plugins
   ```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [MIT License](LICENSE).

The [yt-study](plugins/yt-study/) plugin is a fork of youtube-digest by Team Attention (MIT License). See [NOTICE](NOTICE) for attribution details.

## Author

[kim-jeonghyun](https://github.com/kim-jeonghyun)
