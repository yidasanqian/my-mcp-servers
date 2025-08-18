# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Model Context Protocol (MCP) servers, specifically a PostgreSQL MCP server that provides tools and resources for interacting with PostgreSQL databases.

## Code Architecture

- `src/postgresql/pg_mcpserver.py` - Main PostgreSQL MCP server implementation with:
  - Database connection management
  - Schema resources (tables, table details, indexes)
  - SQL execution tools (read-only queries, sample data, table statistics)
  - Analysis prompts (data exploration, performance optimization, business insights, data quality)

## Common Development Tasks

### 运行uv命令前需要激活虚拟环境

```bash
source .venv/bin/activate
```

### debug the Server

```bash
uv run mcp dev mcpserver.py
```

### Dependencies

- Python >= 3.11
- mcp[cli]>=1.12.0
- psycopg2-binary>=2.9.10

Managed with uv package manager.