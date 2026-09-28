# Create-Video-from-images

Hệ thống tạo video affiliate dài 30–40 giây từ ảnh sản phẩm, mô tả và kịch bản.

## Model sử dụng

| Chức năng | Model | Ghi chú |
|---|---|---|
| Ảnh → Video (chuyển động AI) | [Lightricks/LTX-Video](https://huggingface.co/Lightricks/LTX-Video) | Nhận ảnh và prompt, cần GPU CUDA (khoảng 12GB VRAM trở lên) |
| Viết kịch bản | [Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) | Viết tiếng Việt tốt, chạy được trên CPU/GPU |
| Giọng đọc (TTS) | Microsoft Edge TTS (`edge-tts`) | Giọng Việt Hoài My / Nam Minh, cần Internet |
| Hiệu ứng không cần GPU | Ken Burns (zoom/pan) | Chạy trên CPU, nhanh |

## Cấu trúc thư mục

```
Create-Video-from-images/
├── backend/                      # Python - FastAPI
│   ├── app/
│   │   ├── main.py               # Khởi tạo FastAPI, CORS, static /outputs
│   │   ├── config.py             # Cấu hình: đường dẫn, model id, độ phân giải
│   │   ├── api/
│   │   │   └── routes.py         # REST API endpoints
│   │   ├── schemas/
│   │   │   └── video.py          # Pydantic models (request/response)
│   │   ├── models/               # Lớp bọc (wrapper) các model AI
│   │   │   ├── i2v_model.py      # LTX-Video image-to-video
│   │   │   └── llm_model.py      # Qwen2.5 viết kịch bản
│   │   ├── services/             # Các function xử lý nghiệp vụ
│   │   │   ├── pipeline.py       # Điều phối toàn bộ quy trình tạo video
│   │   │   ├── script_service.py # Tạo và chia kịch bản theo cảnh
│   │   │   ├── tts_service.py    # Tạo giọng đọc
│   │   │   ├── animation_service.py # Ken Burns, phát frame AI, ghép phụ đề
│   │   │   ├── video_composer.py # Ghép cảnh + audio -> MP4
│   │   │   └── job_manager.py    # Quản lý trạng thái job
│   │   └── utils/
│   │       ├── file_utils.py     # Kiểm tra và lưu file upload
│   │       ├── image_utils.py    # Load / crop ảnh
│   │       └── subtitle.py       # Vẽ phụ đề tiếng Việt
│   ├── model_weights/            # Nơi lưu weights model tải từ HuggingFace
│   ├── storage/                  # uploads/, outputs/, temp/ (tự tạo)
│   ├── scripts/
│   │   └── download_models.py    # Tải trước model
│   ├── requirements.txt          # Gói cơ bản (chế độ Ken Burns)
│   ├── requirements-ai.txt       # Gói thêm cho LTX-Video & Qwen
│   └── .env.example
└── frontend/                     # React + Vite
    ├── index.html
    ├── vite.config.js            # Proxy /api, /outputs -> backend :8000
    └── src/
        ├── main.jsx
        ├── App.jsx               # Bố cục chính
        ├── api/client.js         # Gọi API backend
        ├── hooks/useVideoJob.js  # Tạo job + polling tiến độ
        ├── components/
        │   ├── ImageUploader.jsx # Upload, sắp xếp ảnh
        │   ├── ProductForm.jsx   # Tên, mô tả, kịch bản, nút viết kịch bản AI
        │   ├── VideoSettings.jsx # Giọng đọc, tỉ lệ, thời lượng, chế độ
        │   ├── JobProgress.jsx   # Thanh tiến độ
        │   └── VideoPreview.jsx  # Xem và tải video
        └── styles/app.css
```

## Quy trình xử lý

```
Ảnh + Mô tả/Kịch bản
   └─> (không có kịch bản) Qwen2.5 viết kịch bản
   └─> Chia kịch bản thành N cảnh (N = số ảnh)
   └─> Edge-TTS tạo giọng đọc cho từng cảnh
   └─> Mỗi ảnh -> clip chuyển động (LTX-Video hoặc Ken Burns), thời lượng khớp giọng đọc
   └─> Chèn phụ đề -> ghép toàn bộ -> MP4 (30–40s)
```

## Cài đặt & chạy

Yêu cầu: Python 3.10+, Node.js 18+.

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Tuỳ chọn: bật AI (LTX-Video + Qwen). Cài PyTorch CUDA trước:
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements-ai.txt
python -m scripts.download_models

copy .env.example .env   # đặt USE_LLM=0 nếu không cài requirements-ai.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Mở http://localhost:5173

## API

| Method | Endpoint | Mô tả |
|---|---|---|
| GET | `/api/voices` | Danh sách giọng đọc |
| POST | `/api/scripts/generate` | Tạo kịch bản từ tên và mô tả sản phẩm |
| POST | `/api/videos` | Tạo job video (multipart: `images[]`, `script`, `description`, ...) |
| GET | `/api/videos/{job_id}` | Trạng thái, tiến độ và link video |
