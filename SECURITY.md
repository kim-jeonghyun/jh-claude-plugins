# Security Policy

## About This Repository

This repository contains Claude Code plugin configuration files (SKILL.md, plugin.json, markdown references) and lightweight helper shell scripts for external tool invocation (e.g., yt-dlp). It has no compiled binaries or application runtime code.

## Reporting a Vulnerability

To report a security concern, please use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) feature on this repository.

**Do not** open a public GitHub issue for security vulnerabilities.

## Response Timeline

- **Acknowledgment**: Within 7 days of report
- **Fix target**: Within 30 days for confirmed vulnerabilities
- **Disclosure**: A GitHub Security Advisory is published simultaneously with the fix release. Reporters are credited unless they prefer anonymity.

## Scope

The primary security concerns are:
- Prompt injection via SKILL.md instructions or untrusted web/transcript content
- Unsafe file path handling in skill workflows
- Shell injection via helper scripts that invoke external tools
- Exposure of sensitive data in configuration files
