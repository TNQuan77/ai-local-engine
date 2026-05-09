# Hướng dẫn cài đặt

## Yêu cầu

- Python 3.10+
- Node.js 18+
- Ollama (được cài tự động bởi installer)
- (Tùy chọn) Anthropic API key để dùng Claude models

## Cài đặt 1 lệnh

```bash
python scripts/install.py
```

Script sẽ tự động:
1. Kiểm tra phiên bản Python
2. Cài dependencies Python cho backend
3. Cài dependencies Node.js cho frontend
4. Cài Ollama nếu chưa có
5. Quét phần cứng và pull model phù hợp nhất
6. Tạo file `.env` với cấu hình mặc định

## Khởi động

```bash
python scripts/start.py
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Cài đặt thủ công

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

### Ollama
Tải từ https://ollama.com/download, sau đó pull model:
```bash
ollama pull llama3.2        # nhẹ
ollama pull qwen2.5:7b      # cân bằng
ollama pull qwen2.5:14b     # chất lượng cao (cần 16GB+ RAM)
```

## Cấu hình

Copy `.env.example` thành `.env` và chỉnh sửa:

```env
# Provider local (mặc định)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
DEFAULT_PROVIDER=local

# Provider API (tùy chọn)
ANTHROPIC_API_KEY=sk-ant-...
```

## Model đề xuất theo phần cứng

| RAM | GPU VRAM | Đề xuất |
|---|---|---|
| 4–6 GB | bất kỳ | `llama3.2:1b` |
| 6–10 GB | 0 | `llama3.2:3b` |
| 10–16 GB | 0 | `qwen2.5:7b` |
| 16+ GB | 0 | `qwen2.5:14b` |
| bất kỳ | 6–8 GB | `llama3.2:8b` |
| bất kỳ | 10+ GB | `qwen2.5:14b` |

Chạy scanner để nhận đề xuất riêng cho máy của bạn:
```bash
python scripts/scan_system.py
```
