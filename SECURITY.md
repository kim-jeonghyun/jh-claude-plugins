# Security Policy

## About This Repository

This repository contains Claude Code plugin configuration files only (SKILL.md, plugin.json, markdown references). It has no runtime code, compiled binaries, or executable scripts.

## Reporting a Vulnerability

To report a security concern, please use [GitHub's private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) feature on this repository.

**Do not** open a public GitHub issue for security vulnerabilities.

## Scope

Since this repository contains only configuration and documentation files, the primary security concerns are:
- Prompt injection via SKILL.md instructions
- Unsafe file path handling in skill workflows
- Exposure of sensitive data in configuration files
