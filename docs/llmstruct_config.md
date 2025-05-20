# llmstruct Configuration Guide

**Status**: Draft  
**Version**: 0.1.0  
**Last Updated**: 2025-05-18T23:00:27.888546Z  
**Author**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Introduction

This guide explains how to configure llmstruct using `llmstruct.toml` and CLI options.

## 2. Configuration File

Create `llmstruct.toml` in the project root:

```toml
[goals]
goals = []

[cli]
language = "python"
include_patterns = ["*.py"]
exclude_patterns = ["tests/*"]
```

## 3. CLI Options

- Generate `struct.json`:
  ```bash
  python -m llmstruct .
  ```
- Specify goals:
  ```bash
  python -m llmstruct . --goals "Create universal JSON format" "Support LLM integration"
  ```
