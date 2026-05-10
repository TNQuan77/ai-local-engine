# Hướng dẫn cài đặt

## Yêu cầu

Chỉ cần **Python 3.10+**. Mọi thứ còn lại (Node.js, Ollama, model) đều được cài tự động.

## Cài đặt 1 lệnh

```bash
python scripts/install.py
```

Script tự động chạy 6 bước, không cần thao tác gì thêm:

| Bước | Hành động |
|---|---|
| 1/6 | Kiểm tra Python (≥ 3.10) |
| 2/6 | Cài Python dependencies cho backend |
| 3/6 | Cài Node.js dependencies cho frontend (tự cài Node.js nếu chưa có) |
| 4/6 | Kiểm tra / cài Ollama |
| 5/6 | Quét phần cứng → chọn model tốt nhất → pull về |
| 6/6 | Tạo file cấu hình `.env` |

Khi xong sẽ hiện bảng tóm tắt xác nhận mọi thứ đã sẵn sàng.

## Khởi động ứng dụng

```bash
python scripts/start.py
```

Khởi động cả 2 server cùng lúc:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173

Nhấn `Ctrl+C` để dừng cả hai.

## Những gì được cài tự động

### Node.js
- **Windows**: qua `winget install OpenJS.NodeJS.LTS`, fallback tải MSI trực tiếp
- **macOS**: qua `brew install node`
- **Linux**: qua NodeSource setup script

### Ollama
- **Windows**: qua `winget install Ollama.Ollama`, fallback tải file `.exe`
- **macOS**: qua `brew install ollama`
- **Linux**: qua `curl -fsSL https://ollama.com/install.sh | sh`

### Chọn model tự động (dựa trên phần cứng)

| RAM | GPU VRAM | Model được chọn |
|---|---|---|
| 4–6 GB | bất kỳ | `llama3.2:1b` |
| 6–10 GB | 0 | `llama3.2:3b` |
| 10–16 GB | 0 | `qwen2.5:7b` |
| 16+ GB | 0 | `qwen2.5:14b` |
| bất kỳ | 6–8 GB | `llama3.2:8b` |
| bất kỳ | 10+ GB | `qwen2.5:14b` |

Để xem trước hệ thống sẽ chọn model nào:
```bash
python scripts/scan_system.py
```

## Cấu hình

Installer tự tạo file `.env`. Để tuỳ chỉnh:

```env
# Provider local (mặc định — không cần API key)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
DEFAULT_PROVIDER=local

# Provider API (tùy chọn — cần nếu muốn dùng Claude)
ANTHROPIC_API_KEY=sk-ant-...
```

## Cài đặt thủ công (nếu cần)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Pull model thủ công
ollama pull llama3.2:3b
```
