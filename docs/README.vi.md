# AI Local Engine — Kiến trúc hệ thống

## Tổng quan

AI Local Engine là coding agent full-stack với 2 provider:

| Provider | Engine | Yêu cầu | Khi nào dùng |
|---|---|---|---|
| **Local** | Ollama | Không cần (offline) | Riêng tư, miễn phí |
| **API** | Claude Agent SDK | `ANTHROPIC_API_KEY` | Chất lượng cao hơn |

## Kiến trúc hệ thống

```
┌─────────────────────────────────────────────┐
│              Frontend (React)                │
│  ProviderToggle → ModelSelector              │
│  WorkspaceBar → ChatWindow → InputBar        │
│  Slash commands: /review /refactor /test ... │
└──────────────┬──────────────────────────────┘
               │ HTTP SSE  /api/chat
┌──────────────▼──────────────────────────────┐
│              Backend (FastAPI)               │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ OllamaAgent  │  │   ClaudeAgent        │ │
│  │ tool loop    │  │   claude-agent-sdk   │ │
│  └──────┬───────┘  └──────────────────────┘ │
│         │ tools                              │
│  ┌──────▼────────────────────────────┐      │
│  │ file_tools + extended_tools       │      │
│  │ read/write/edit/bash/glob/grep    │      │
│  │ web_search/run_tests/git/lint     │      │
│  └───────────────────────────────────┘      │
└─────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         Thư mục project của người dùng       │
│  Bất kỳ thư mục nào trên hệ thống           │
└─────────────────────────────────────────────┘
```

## Giao thức SSE Events

```
POST /api/chat → text/event-stream

data: {"type": "text",        "content": "Đang đọc file..."}
data: {"type": "tool_call",   "name": "read_file", "input": {"path": "main.py"}}
data: {"type": "tool_result", "content": "def main():\n    ..."}
data: {"type": "done"}
```

## Danh sách Tools

### File Tools (cả 2 provider)
| Tool | Mô tả |
|---|---|
| `read_file(path)` | Đọc nội dung file |
| `write_file(path, content)` | Tạo / ghi đè file |
| `edit_file(path, old_string, new_string)` | Thay thế đoạn text chính xác |
| `run_bash(command)` | Chạy lệnh shell trong working dir |
| `list_files(pattern)` | Tìm file theo glob pattern |
| `search_in_files(text, pattern)` | Tìm text trong files (như grep) |

### Extended Tools
| Tool | Mô tả |
|---|---|
| `web_search(query)` | Tìm kiếm DuckDuckGo |
| `http_request(url, method, body)` | Gọi HTTP API |
| `run_tests(path, framework)` | Chạy pytest / jest |
| `git_status()` | git status + diff |
| `git_commit(message)` | Stage all + commit |
| `lint_file(path)` | flake8 / eslint |

## Slash Skills (lệnh tắt)

| Lệnh | Hành động |
|---|---|
| `/review` | Review code (git diff + phân tích) |
| `/refactor <file>` | Tái cấu trúc code |
| `/test <file>` | Tạo unit tests |
| `/explain <file>` | Giải thích code chi tiết |
| `/fix` | Tìm và sửa bugs |
| `/docs <file>` | Tạo documentation |
| `/commit` | Tạo git commit |
| `/lint` | Lint và sửa lỗi style |
