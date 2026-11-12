# Baseline Phase 2 — CPU

Ngày kiểm chứng: **12/11/2026**, Asia/Bangkok. Mã ứng dụng và trọng số vẫn là bản kế thừa; không thay kiến trúc, preprocessing hoặc thứ tự nhãn. Bản gốc dùng để đối chiếu: commit `46c52bf` của repo này (ứng dụng kế thừa từ upstream `1c5be55`).

## 1. Môi trường đã chạy thành công

| Thành phần | Giá trị |
|---|---|
| OS | Windows x64, build 26200 (platform Python báo Windows-10-10.0.26200-SP0) |
| CPU | AMD Ryzen 7 H 255 w/ Radeon 780M Graphics, 8 nhân / 16 luồng |
| Python | CPython 3.11.9 |
| PyTorch | 2.8.0+cpu |
| torchvision | 0.23.0+cpu |
| Streamlit | 1.67.0 |
| Pillow | 13.0.0 |
| NumPy | 2.4.6 |
| Thiết bị suy luận | CPU, mặc định PyTorch 8 threads |

Phiên bản runtime trực tiếp nằm trong `requirements.txt`; toàn bộ 41 packages runtime được ghim trong `requirements-lock.txt`. Lockfile ghi môi trường Windows x64/Python 3.11.9, chưa được chứng nhận trên Linux/macOS hay Python khác.

## 2. Tương thích Windows đã xử lý

| Lần thử | Kết quả thực tế |
|---|---|
| torch 2.15.0+cpu / torchvision 0.29.2+cpu | `WinError 4551` khi import; log Code Integrity event 3077 xác nhận Smart App Control chặn `shm.dll` |
| torch 2.10.0+cpu / torchvision 0.25.0+cpu | `WinError 1114` khi khởi tạo `c10.dll`; chưa xác định nguyên nhân đầy đủ |
| Bộ cài VC++ x64 từ Microsoft, chữ ký hợp lệ | Kết thúc mã 1602; không có bằng chứng cập nhật thành công; không coi là biện pháp đã sửa lỗi |
| torch 2.8.0+cpu / torchvision 0.23.0+cpu | Import, load checkpoint, suy luận và chạy app thành công |

Không tắt hoặc chỉnh chính sách Windows, không sửa DLL. VC runtime hệ thống quan sát trước lần thử: 14.29.30040.0. Cặp PyTorch cuối cùng được lấy từ chỉ mục CPU chính thức. Phiên bản 2.8.0 được chọn vì đã kiểm chứng trên máy này, không phải tuyên bố là phiên bản mới nhất hay phù hợp mọi máy.

Tham khảo chẩn đoán: [PyTorch #182008 — Windows Application Control](https://github.com/pytorch/pytorch/issues/182008), [PyTorch #166628 — DLL initialization](https://github.com/pytorch/pytorch/issues/166628), [các phiên bản chính thức](https://pytorch.org/get-started/previous-versions/), [Microsoft Visual C++ Runtime](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist).

## 3. Đối chiếu app và notebook

- `resnet18(weights=None)` với lớp cuối `Linear(512, 6)`; tải state dict CPU, `model.eval()`.
- App và notebook evaluation đều dùng `Resize((224, 224))` rồi `ToTensor()`, không có ImageNet Normalize. Script so sánh tensor trên cùng ảnh và xác nhận bằng nhau. Không tự thêm normalization khi kế thừa trọng số này.
- Notebook in ba nhãn cà chua dạng `Tomato_Early_blight`, `Tomato_Late_blight`, `Tomato_healthy`; app dùng `Tomato___...`. Ý nghĩa và thứ tự sáu lớp khớp sau khi chuẩn hóa dấu gạch dưới.
- Notebook lưu tên `leaf_model_v2.pth`; repo đóng gói `leaf_model_final.pth`. Checkpoint tải được và head có sáu đầu ra, nhưng không thể chứng minh toàn bộ provenance huấn luyện chỉ từ việc load thành công.
- Notebook không lưu seed hoặc danh sách indices của split. Không tái dựng được chính xác test set gốc.

## 4. Ảnh kiểm chứng

Chỉ tải **một ảnh mỗi lớp**, tổng sáu ảnh, vào thư mục `data/baseline/` bị Git ignore. Không tải toàn bộ dataset hoặc thay thế Phase 3.

[Manifest](../reports/baseline/samples.json) ghi repository, commit dữ liệu, đường dẫn, URL nguồn, SHA-256 và Git blob SHA từng ảnh. Chọn tên ảnh đầu tiên theo thứ tự từ điển trong kết quả GitHub contents API, không chọn lại ảnh sau khi xem dự đoán; API có thể giới hạn 1.000 mục mỗi thư mục.

Dataset gốc: [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset), commit `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`. Thông tin giấy phép/tác giả xem [ACKNOWLEDGEMENTS](../ACKNOWLEDGEMENTS.md). Repo chỉ lưu manifest và kết quả, không phân phối lại ảnh mẫu.

## 5. Kết quả kiểm chứng lần đầu

| Nhãn ảnh | Dự đoán | Điểm softmax top 1 |
|---|---|---:|
| Potato — Early blight | Potato — Early blight | 98,29% |
| Potato — Late blight | Potato — Late blight | 94,03% |
| Potato — healthy | Potato — healthy | 80,91% |
| Tomato — Early blight | Tomato — Early blight | 96,58% |
| Tomato — Late blight | Tomato — Late blight | 96,77% |
| Tomato — healthy | Tomato — healthy | 99,84% |

**6/6 ảnh khớp nhãn chỉ là smoke check**, không phải accuracy test độc lập hoặc bằng chứng mô hình đạt 100%. Có thể các ảnh đã xuất hiện trong huấn luyện. 93,69% trong README gốc vẫn là số liệu tác giả, chưa tái lập test set gốc.

- Median CPU forward: **27,06 ms/ảnh** trên lần chạy đầu; không gồm đọc ảnh, preprocessing, softmax, UI.
- Cách đo: mỗi ảnh warm-up một lượt, đo 5 lượt, 30 phép đo tổng cộng; giữ mặc định 8 threads.
- Load mô hình lần đầu khoảng **240,70 ms** trong script; không phải thời gian khởi động toàn ứng dụng.
- Chi tiết top 3, timings, SHA-256 app/notebook/checkpoint: [results.json](../reports/baseline/results.json).
- SHA-256 checkpoint: `b20634ad7be7da28e6a2345b7def1c217a877ce89e10d581d9b30ab5d152a963`.

## 6. Kiểm tra ứng dụng

- Streamlit AppTest khởi tạo app không có exception hoặc lỗi tải mô hình.
- Sáu lần chạy upload: patch `st.file_uploader` trả về BytesIO của ảnh thật; app thực thi decode → preprocessing → model → softmax → render. Nhãn và điểm hiển thị khớp kết quả kiểm chứng từng ảnh.
- File không phải ảnh được app bắt lỗi và hiển thị `Prediction failed`, không crash ngoài luồng xử lý.
- Một process Streamlit thật được khởi động ở loopback; `/_stcore/health` trả `ok`, `/` trả HTTP 200; process được dừng sau kiểm tra.
- Đây là kiểm tra runtime và render tree tự động, **chưa phải kiểm thử thao tác upload bằng trình duyệt hoặc QA bố cục trực quan**. Kiểm tra toàn diện UI/UX thuộc Phase 5–6.
- Các cảnh báo `missing ScriptRunContext` ở main thread xuất hiện khi dùng AppTest; các assertion ứng dụng vẫn đạt.

## 7. Chạy lại

Trong PowerShell tại thư mục dự án, dùng Python 3.11.9 x64:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/baseline_check.py --restore-samples
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Mở http://localhost:8501. Script khôi phục đúng ảnh theo manifest và kiểm tra checksum; không chọn ảnh mới. Ảnh cần internet cho lần tải đầu, suy luận sau đó dùng CPU cục bộ. Lệnh chạy lại ghi đè `reports/baseline/results.json`; dùng `--result-name local-results.json` nếu muốn giữ kết quả ban đầu.

Script kiểm chứng lấy hàm load model và transform trực tiếp từ AST của app để không tự viết lại pipeline. AppTest vẫn chạy toàn bộ `app.py`. Script dừng với exit code khác 0 nếu một assertion không đạt.

`--download-samples` chỉ dùng khi chủ động lập manifest mới; không cần dùng khi tái lập baseline. Không commit dataset, ảnh tải về hoặc môi trường ảo.

## 8. Kiểm tra từ môi trường mới

Đã tạo `.venv-repro` riêng bằng CPython 3.11.9, cài đúng 41 packages từ lockfile, chạy `uv pip check` đạt và chạy lại toàn bộ script với `--result-name repro-results.json`. Sáu ảnh tiếp tục khớp nhãn; tất cả bảy nhóm assertion đạt, server HTTP khỏe. Median CPU forward lần này **27,79 ms/ảnh**, thay đổi nhẹ theo tải hệ thống. Chi tiết: [repro-results.json](../reports/baseline/repro-results.json).

Lệnh cài thực tế dùng uv 0.11.32:

```powershell
uv venv --python python .venv-repro
uv pip sync --python .venv-repro/Scripts/python.exe requirements-lock.txt --link-mode=copy --index-strategy unsafe-best-match
uv pip check --python .venv-repro/Scripts/python.exe
.\.venv-repro\Scripts\python.exe scripts/baseline_check.py --result-name repro-results.json
```

Với uv, chỉ mục CPU có một số package phụ trợ ở phiên bản khác PyPI; chiến lược mặc định `first-index` đã không giải được `certifi==2026.10.23`. Lệnh trên tra cả hai index cho các phiên bản đã ghim. Không cần cờ này khi dùng pip theo hướng dẫn cài chính. Đây là lock phiên bản, chưa phải lock kèm hash mọi wheel.

## 9. Giới hạn và bước tiếp

Phase 2 xác nhận được tính chạy được và nhất quán pipeline trên máy hiện tại. Chưa đánh giá độc lập, chưa có confusion matrix toàn dataset, chưa xử lý phát hiện ảnh ngoài phạm vi, chưa kiểm thử mọi loại ảnh. Phase 3 sẽ lập thống kê dữ liệu và phương pháp đánh giá phù hợp yêu cầu học phần.
