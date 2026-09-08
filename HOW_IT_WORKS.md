# PhoWhisper: Cách Hoạt Động Chi Tiết

## Tổng Quan

PhoWhisper là một hệ thống **Nhận Dạng Giọng Nói Tự Động (ASR - Automatic Speech Recognition)** được tối ưu hóa cho tiếng Việt. Nó dựa trên mô hình **Whisper của OpenAI** nhưng được **tinh chỉnh (fine-tune)** trên 844 giờ dữ liệu tiếng Việt với nhiều giọng khác nhau.

---

## 🧠 Thuật Toán Cơ Bản

### 1. Tầng Xử Lý Âm Thanh (Audio Processing)

```
📊 File âm thanh (WAV/MP3)
    ↓
🎙️ Chuẩn hóa tần số: 16 kHz (16,000 mẫu/giây)
    ↓
📈 Mel-spectrogram: Biến đổi âm thanh thành hình ảnh tần số
    ↓
🔢 Encoder: Nén thông tin âm thanh
```

**Ví dụ cụ thể:** Nếu bạn nói "Xin chào", file WAV được:
- Chuyển thành dòng số có tần số 16kHz
- Tách thành các frame nhỏ (25ms mỗi frame)
- Tính FFT (Fast Fourier Transform) để lấy thành phần tần số
- Tạo Mel-spectrogram (hình ảnh ma trận của tần số)

### 2. Encoder - Xử Lý Tính Năng (Feature Extraction)

```
Mel-spectrogram 
    ↓
🔴 Convolutional Layers: Trích xuất đặc trưng cấp thấp
    (như: cạnh, kết cấu)
    ↓
🟢 Transformer Blocks: Học mối quan hệ giữa các phần
    (như: "âm 'x' khi nói nhanh nghe giống 'ch'")
    ↓
🔵 Context Vector: Mô tả âm thanh thành vector 512D
```

**Chi tiết:**
- **Convolutional Layers (Conv2D)**:
  - Tầng 1: 80 channel (mel-frequencies) → 128 channel
  - Tầng 2: 128 → 128 channel (với stride=2, giảm kích thước)
  - Mục đích: Tách các đặc trưng cấp thấp (pitch, amplitude)

- **Sinusoidal Positional Encoding**:
  - Thêm thông tin về vị trí của mỗi frame
  - Giúp mô hình biết "âm này nói lúc nào" trong câu

- **Transformer Encoder (12 tầng)**:
  - Self-Attention: Mỗi frame nhìn toàn bộ frame khác
  - Feed-Forward: Xử lý thông tin
  - Normalization: Ổn định đầu ra
  - Output: Vector [T/4, 768] (T là tổng frame)

### 3. Decoder - Chuyển Đổi Thành Văn Bản (Text Generation)

```
Context Vector từ Encoder
    ↓
🔤 Start Token (bắt đầu sinh lời)
    ↓
Attention Mechanism: Tập trung vào phần nào của âm thanh?
    ↓
Transformer Decoder: Dự đoán ký tự tiếp theo
    (Xác suất: 'X' 85%, 'S' 10%, ...)
    ↓
🎯 Output: "Xin chào"
```

**Quá trình từng bước (Autoregressive Generation):**

1. **Decoder bước 1**: 
   - Input: `[<start>]` + Encoder output
   - Cross-Attention: Lấy thông tin từ Encoder
   - Self-Attention: (chỉ có start token)
   - Output logits: [vocab_size]
   - Chọn: **"X"** (xác suất cao nhất)

2. **Decoder bước 2**:
   - Input: `[<start>, "X"]` + Encoder output
   - Cross-Attention: Lấy lại thông tin từ Encoder
   - Self-Attention: "X" nhìn start token
   - Output: **"i"**

3. **Decoder bước 3**:
   - Input: `[<start>, "X", "i"]` + Encoder output
   - Self-Attention: "Xi" nhìn toàn bộ
   - Output: **"n"**

4. **... Tiếp tục** cho đến khi xuất hiện token kết thúc `</end>`

**Attention Mechanism - Tầm Quan Trọng:**
- Khi đoán "i" trong "Xin", mô hình tập trung vào phần giữa của âm thanh
- Khi đoán "n", tập trung vào phần cuối
- Điều này giúp tránh lỗi khi đoán ký tự sai

---

## 📦 5 Phiên Bản Mô Hình

| Model | Kích Thước | Tốc Độ (CPU) | Tốc Độ (GPU) | Độ Chính Xác WER | Dùng Khi Nào |
|-------|-----------|--------------|--------------|------------------|-------------|
| **Tiny** | 39M | 1s | 0.5s | 10.41% | Điện thoại, IoT, tốc độ là ưu tiên |
| **Base** | 74M | 2s | 1s | 8.46% | Edge device, thời gian thực |
| **Small** | 244M | 5s | 2s | 6.33% | **Khuyến nghị** - cân bằng tốt |
| **Medium** | 769M | 10s | 4s | 4.97% | GPU server, chất lượng cao |
| **Large** | 1.55B | 20s | 8s | **4.67%** | Backup, yêu cầu chính xác tuyệt đối |

**WER (Word Error Rate)** - Tỷ lệ Lỗi Từ:
- Càng thấp càng tốt
- 4.67% = ~1 lỗi trên 21 từ
- Tương đương con người: ~4-6%

**Benchmark Datasets:**
- **CMV-Vi**: Dataset điều kiện đa âm tuyến (multi-accented)
- **VIVOS**: Dataset Vietnamese Voices
- **VLSP 2020**: Task-1 (speech) và Task-2 (noisy/challenging)

---

## 🔄 Quy Trình Chuyển Âm Thanh → Văn Bản (Chi Tiết)

### Bước 1: Tiền Xử Lý (Pre-processing)

```python
# server.py
audio_data = base64.b64decode(request["audio"])  # Giải mã từ Base64
# → Lưu vào tệp WAV tạm thời
```

**Quá trình:**
- Client gửi audio dưới dạng Base64 (vì JSON không hỗ trợ binary)
- Server giải mã Base64 → bytes nhị phân
- Lưu vào file WAV tạm thời (`/tmp/xxx.wav`)

### Bước 2: Load Mô Hình (Model Loading)

```python
transcriber = pipeline(
    "automatic-speech-recognition",
    model="vinai/PhoWhisper-small",
    device=0 if USE_GPU else -1
)
```

**Chi tiết:**
- **Lần đầu tiên:**
  - Tải từ HuggingFace: ~244MB (small) hoặc 1.55GB (large)
  - Lưu vào bộ nhớ cache: `~/.cache/huggingface/models/`
  - Thời gian: 1-5 phút (tùy tốc độ internet)

- **Lần tiếp theo:**
  - Đọc từ cache (nhanh hơn)
  - Thời gian: < 1 giây

- **Device Selection:**
  - GPU (device=0): NVIDIA CUDA, TensorRT
  - CPU (device=-1): PyTorch + NumPy

### Bước 3: Xử Lý Audio (Audio Processing)

```python
# Transformers tự động:
# 1. Đọc WAV file
# 2. Chuẩn hóa âm lượng (normalization)
# 3. Tính Mel-spectrogram
# 4. Padding/truncating để vừa với độ dài cố định
```

**Chi tiết:**

**3.1 Đọc WAV:**
```
Input: audio.wav (stereo, 44.1kHz)
↓
Resample: 44.1kHz → 16kHz
↓
Mono: Nếu stereo, chuyển sang mono
↓
Output: 16kHz mono PCM
```

**3.2 Chuẩn hóa (Normalization):**
```
Raw samples: [-32768, 32767]
↓
Normalize: [-1.0, 1.0]
↓
Standardize: mean=0, std=1
```

**3.3 Mel-Spectrogram:**
```
1. Tách thành frame (25ms, overlap 10ms)
2. Áp dụng FFT (Fast Fourier Transform)
3. Lấy magnitude: |FFT(frame)|²
4. Áp dụng Mel filter bank: 80 filters (0-8kHz)
5. Lấy log: log(1 + magnitude)

Output: [80 (mel-freq), ~3000 (time-frame)]
```

**3.4 Padding/Truncating:**
```
Nếu âm thanh < 30s: Padding với 0
Nếu âm thanh > 30s: Cắt lấy 30s đầu
Output: [80, 3000] (cố định)
```

### Bước 4: Encoder (Nhận Dạng Đặc Trưng)

```
Mel-spectrogram [80, 3000]
    ↓
Conv2d: 80 → 128 channel
Conv2d: 128 → 128 channel (stride=2)
    ↓ Output shape: [128, 1500]
    
Sinusoidal Positional Encoding
    ↓
12 × Transformer Encoder Block:
  ├─ Multi-Head Self-Attention (8 heads)
  │  ├─ Query, Key, Value projection
  │  ├─ Scaled dot-product attention
  │  └─ Concat + linear
  │
  ├─ Feed-Forward Network
  │  ├─ Linear(768 → 3072)
  │  ├─ ReLU activation
  │  └─ Linear(3072 → 768)
  │
  └─ Layer Normalization + Residual Connection
    ↓
Output Encoder: [1500, 768] (vector đặc trưng)
```

**Chi tiết Self-Attention:**
```
Giả sử có 5 frame: f1, f2, f3, f4, f5

Query:  [W_q · f1, W_q · f2, ..., W_q · f5]
Key:    [W_k · f1, W_k · f2, ..., W_k · f5]
Value:  [W_v · f1, W_v · f2, ..., W_v · f5]

Attention(f1) = softmax([
  (Q1·K1)/√d,  (Q1·K2)/√d,  (Q1·K3)/√d,  (Q1·K4)/√d,  (Q1·K5)/√d
]) @ [V1, V2, V3, V4, V5]

Mục đích: f1 "lắng nghe" tất cả frame khác để làm giàu đặc trưng
```

### Bước 5: Decoder (Sinh Lời - Text Generation)

```
Encoder Output: [1500, 768]
    ↓
Init: [<bos>] (Begin of Sequence token)
    ↓
12 × Transformer Decoder Block (autoregressive):
  ├─ Masked Self-Attention
  │  └─ Chỉ nhìn những token trước đó (causal)
  │
  ├─ Cross-Attention (từ Encoder)
  │  └─ Query từ Decoder, Key/Value từ Encoder
  │
  ├─ Feed-Forward Network
  │
  └─ Layer Normalization + Residual
    ↓
Linear: [768] → [51865] (vocab size)
    ↓
Softmax: Xác suất cho mỗi ký tự
    ↓
Top-1 (hoặc Beam Search): Chọn ký tự tốt nhất
    ↓
Output: "X"
```

**Autoregressive Loop:**
```python
tokens = [<bos>]
for step in range(max_steps):
    logits = decoder(tokens, encoder_output)
    next_token = argmax(logits[-1])  # hoặc sample()
    tokens.append(next_token)
    
    if next_token == <eos>:  # End of Sequence
        break
```

### Bước 6: Post-Processing

```python
result = transcriber(tmp_path)
# Kết quả: {"text": "Xin chào"}

# Cleanup
Path(tmp_path).unlink(missing_ok=True)
```

---

## 🎯 Tại Sao PhoWhisper Hiệu Quả?

### 1. Fine-Tuning trên Tiếng Việt

**Whisper gốc (OpenAI):**
- Huấn luyện trên 99 ngôn ngữ
- Mỗi ngôn ngữ: ~1-2% tổng dữ liệu
- Tiếng Việt: ~2-3 giờ dữ liệu

**PhoWhisper (VinAI):**
- Tinh chỉnh trên 844 giờ tiếng Việt
- 282 lần nhiều hơn so với Whisper gốc
- Học được:
  - Các tôn (tone) của tiếng Việt (tôn thứ 1-6)
  - Từ địa phương, từ mới (bằng, chuối, bàn tính, etc.)
  - Giọng Bắc, Tây, Nam, Tây Nguyên

### 2. Kiến Trúc Transformer

**Ưu điểm:**
- **Self-Attention**: Mỗi frame "nhìn" tất cả frame khác
  - Tránh vấn đề RNN (vanishing gradient)
  - Xử lý từ xa tốt
  
- **Parallelization**: Xử lý toàn bộ audio cùng lúc
  - RNN phải xử lý tuần tự (chậm)
  - Transformer xử lý song song (nhanh)

- **Multi-Head Attention**: 8 heads, mỗi head học 1 khía cạnh
  - Head 1: Nhận diện tone
  - Head 2: Nhận diện consonant (phụ âm)
  - Head 3: Nhận diện vowel (nguyên âm)
  - ...

### 3. Khả Năng Tổng Quát Hóa

**Cross-lingual Transfer:**
- Whisper học từ 99 ngôn ngữ
- Hiểu các cấu trúc âm thanh chung (pitch, formant, etc.)
- Fine-tune trên tiếng Việt "khôi phục" kiến thức này

**Robust to Noise:**
- Huấn luyện trên dữ liệu thực (không chỉ sạch)
- Học cách bỏ qua tiếng ồn nền

### 4. Beam Search (Tìm Kiếm Toàn Bộ)

Thay vì greedy (chỉ chọn top-1 từng bước):
```
Greedy:
  P(X) = 0.9 → chọn X
  P(i|X) = 0.7 → chọn i
  P(n|Xi) = 0.6 → chọn n
  Score: 0.9 × 0.7 × 0.6 = 0.378

Beam Search (beam_width=3):
  Giữ top-3 hypotheses sau mỗi bước:
  1. [X] P=0.9
  2. [Y] P=0.08
  3. [Z] P=0.02
  
  Mỗi bước, mở rộng từ 3 hypotheses:
  [Xi], [Xa], [Xu], [Yi], [Ya], ..., [Zi], ...
  → Giữ top-3 lại
  
  Kết quả: Tìm được "Xin chào" với xác suất cao hơn
```

---

## 📊 Ví Dụ Thực Tế

### Kịch Bản: "Giám đốc họp lúc mấy giờ?"

**Input:**
- File MP3: 5 giây, 44.1kHz stereo

**Bước 1-2: Pre-processing**
```
Resample: 44.1kHz → 16kHz
Mono: [L+R]/2
Normalize: [-32768, 32767] → [-1.0, 1.0]
```

**Bước 3: Mel-Spectrogram**
```
[80, 1280] matrix (5s × 16kHz = 80,000 samples)
```

**Bước 4: Encoder**
```
Conv2d × 2: [80, 1280] → [128, 640]
Positional Encoding: thêm vị trí
Transformer × 12: [640, 768] → [640, 768]
Output: Encoder state [640, 768]
```

**Bước 5: Decoder (Autoregressive)**
```
Step 1: [<bos>] + Encoder
  → logits[vocab=51865]
  → argmax() = token_id(G)
  → Output: "G"

Step 2: [<bos>, G] + Encoder
  → logits
  → argmax() = token_id(i)
  → Output: "i"

Step 3: [<bos>, G, i] + Encoder
  → argmax() = token_id(á)
  → Output: "á"

...continue...

Step N: [<bos>, G, i, á, m, _, đ, ó, c, _, h, ọ, p, _, l, ú, c, _, m, ấ, y, _, g, i, ờ, ?]
  → logits
  → argmax() = token_id(</eos>)
  → STOP
```

**Output:**
```json
{
  "text": "Giám đốc họp lúc mấy giờ?",
  "model": "vinai/PhoWhisper-small",
  "confidence": 0.96
}
```

---

## ⚙️ Trong Dự Án PhoWhisper Này

### Kiến Trúc Toàn Bộ

```
┌─────────────────┐
│  QLTB App       │  Ghi âm
└────────┬────────┘
         │ audio file
         │
┌────────▼────────────────┐
│  AI Gateway (Node.js)   │  POST /transcribe
│  gateway.js:3000        │
└────────┬────────────────┘
         │ HTTP + base64
         │
┌────────▼──────────────────────┐
│  PhoWhisper FastAPI Server    │
│  server.py:8000              │
│                              │
│  1. get_transcriber()         │
│     ↓ Load model từ cache    │
│  2. transcriber(audio_path)   │
│     ↓ Encoder: 80→768        │
│     ↓ Decoder: autoregressive │
│  3. result = {"text": "..."}  │
└────────┬──────────────────────┘
         │ JSON response
         │
┌────────▼────────────────┐
│  AI Gateway (Node.js)   │
└────────┬────────────────┘
         │ Optional: Ollama analysis
         │
┌────────▼────────────────┐
│  QLTB App               │  Display result
└─────────────────────────┘
```

### Code Flow (server.py)

```python
@app.post("/api/transcribe")
async def transcribe(request: dict):
    # 1. Validate
    if "audio" not in request:
        raise HTTPException(400, "Missing 'audio' field")
    
    # 2. Decode audio
    audio_data = base64.b64decode(request["audio"])
    
    # 3. Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_data)
        tmp_path = tmp.name
    
    # 4. Get transcriber (with caching)
    model = request.get("model", "vinai/PhoWhisper-small")
    transcriber = get_transcriber(model)  # Cached!
    
    # 5. Transcribe
    result = transcriber(tmp_path)
    # Internal: Encoder(audio) → Decoder(autoregressive)
    
    # 6. Cleanup
    Path(tmp_path).unlink(missing_ok=True)
    
    # 7. Return
    return {
        "text": result["text"],
        "model": model
    }
```

---

## 📈 Performance Metrics

### Tốc Độ

**Per minute of audio:**
| Model | CPU | GPU |
|-------|-----|-----|
| tiny | 1s | 0.5s |
| small | 5s | 2s |
| medium | 10s | 4s |
| large | 20s | 8s |

**Real-time factor (RTF):**
- RTF = processing_time / audio_duration
- RTF < 1 = xử lý nhanh hơn thời gian phát
- tiny: RTF = 1s / 60s = 0.017 (60× nhanh hơn)

### Độ Chính Xác (WER)

| Dataset | Tiny | Base | Small | Medium | Large |
|---------|------|------|-------|--------|-------|
| CMV-Vi | 19.05 | 16.19 | 11.08 | 8.27 | **8.14** |
| VIVOS | 10.41 | 8.46 | 6.33 | 4.97 | **4.67** |
| VLSP2020-1 | 20.74 | 19.70 | 15.93 | 14.12 | **13.75** |
| VLSP2020-2 | 49.85 | 43.01 | 32.96 | 26.85 | **26.68** |

---

## 🔧 Tuning & Optimization

### Để Tăng Tốc Độ

1. **Dùng GPU:**
   ```
   USE_GPU=1 docker-compose up -d
   ```
   → 2-4× nhanh hơn

2. **Dùng model nhỏ:**
   ```
   model="vinai/PhoWhisper-tiny"
   ```
   → 4-5× nhanh hơn (nhưng kém chính xác 2-3%)

3. **Quantization (INT8):**
   ```
   transcriber = pipeline(..., device=0, quantize="int8")
   ```
   → Giảm 75% memory, 1.5× nhanh hơn

### Để Tăng Độ Chính Xác

1. **Dùng model lớn:**
   ```
   model="vinai/PhoWhisper-large"
   ```
   → +1-2% WER (nhưng chậm hơn)

2. **Beam Search:**
   ```
   result = transcriber(audio_path, beam_size=5)
   ```
   → +0.5-1% accuracy (nhưng chậm hơn)

3. **Pre-processing:**
   - Giảm noise: librosa.effects.trim()
   - Chuẩn hóa volume: pyloudnorm

---

## 📚 Tham Khảo

- **PhoWhisper Paper**: https://openreview.net/pdf?id=qsif2awK2L
- **Whisper (OpenAI)**: https://github.com/openai/whisper
- **Transformers Library**: https://huggingface.co/transformers/
- **VinAI Research**: https://www.vinai.io/

---

**Cập nhật lần cuối:** 2026-09-08
