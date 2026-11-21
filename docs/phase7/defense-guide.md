# Kịch bản thuyết trình và bảo vệ

## Chuẩn bị trước buổi trình bày

Điền trường, khoa/lớp, họ tên, mã sinh viên và giảng viên ở bìa Word. Kiểm tra yêu cầu giảng viên tại issue #2: chưa có thông tin xác nhận học phần bắt buộc tự train, so sánh thuật toán hay mẫu báo cáo riêng. Nếu có yêu cầu đó, cần bổ sung thực nghiệm; không sửa câu chữ thành “đã train” khi chưa thực hiện.

Đọc `docs/baseline.md`, `docs/dataset.md`, `docs/evaluation.md` và các module `src/`. Chạy ứng dụng, thử ảnh mẫu và mở video trước buổi bảo vệ. Báo cáo và code có hỗ trợ Codex; người nộp cần hiểu nội dung và theo quy định AI của học phần.

Chạy tại root dự án với môi trường đã cài theo README:

```powershell
$env:AGRI_HISTORY_PATH = "$PWD/storage/defense-demo.sqlite3"
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Dùng database demo riêng để không lẫn lịch sử cá nhân. Thử sáu ảnh mẫu khi có internet hoặc khôi phục trước bằng `scripts/baseline_check.py --restore-samples --result-name defense-results.json`. Giữ checkpoint, video MP4, báo cáo PDF và slide ở máy. Không cần tải cả dataset để demo sáu ảnh mẫu.

## Lời trình bày theo 12 slide

Mục tiêu khoảng 6–7 phút nói và 4 phút thao tác; điều chỉnh theo thời gian giảng viên cho phép.

| Slide | Thời lượng gợi ý | Nội dung nói |
|---|---:|---|
| 1 | 20 giây | “Đề tài xây dựng ứng dụng nhận dạng bệnh lá khoai tây và cà chua. Em sử dụng checkpoint ResNet18 public, phát triển ứng dụng và kiểm chứng; chưa tự huấn luyện lại.” |
| 2 | 25 giây | Phân loại một ảnh vào sáu nhãn; EB, LB, healthy của hai cây. Đầu ra nhãn, điểm và top 3; không định vị tổn thương. |
| 3 | 40 giây | Nêu CNN tạo đặc trưng, khối dư F(x)+x, pipeline RGB/224/ToTensor, eval/softmax; giữ preprocessing gốc. |
| 4 | 35 giây | PlantVillage public có snapshot; audit 6.652 ảnh, không lỗi giải mã, 14 cặp trùng; cách ly 1.582 ảnh thiếu leaf mapping. |
| 5 | 45 giây | Chia theo nhóm lá, seed 42; 3.546/748/776 ảnh. Giải thích checkpoint cũ có thể đã thấy test nên chưa có đánh giá độc lập. |
| 6 | 30 giây | Phân chia UI/core/storage; PredictionResult cho phép thay UI mà giữ pipeline. |
| 7 | 25 giây | Luồng chọn ảnh, xem trước, phân tích và lưu; UI tiếng Việt, trạng thái lỗi/rỗng rõ ràng. |
| 8 | 25 giây | SQLite cục bộ chỉ lưu khi bấm nút; metadata và thumbnail, lọc/CSV/xóa có xác nhận. |
| 9 | 45 giây | 716/776 khớp; accuracy 92,27%, macro F1 91,85%; macro F1 bổ sung góc nhìn khi lệch lớp. Nhắc giới hạn trùng train. |
| 10 | 35 giây | Tomato LB sang EB 16 ảnh và chiều ngược 11; median CPU 33,59 ms, không tính file I/O và checksum, chưa phải latency trình duyệt. |
| 11 | 35 giây | Nêu checkpoint/dữ liệu kế thừa; phần mới UI, module, audit, SQLite, kiểm chứng, 39 test/CI và tài liệu. |
| 12 | 25 giây | Giới hạn và hướng thu thập test ngoài đồng độc lập, train lại, so sánh. Chuyển sang demo ứng dụng. |

## Demo trực tiếp 4 phút

| Mốc | Thao tác | Điều cần giải thích và kết quả mong đợi |
|---|---|---|
| 0:00–0:25 | Mở Nhận dạng | Hai cây/sáu lớp. Ứng dụng chạy CPU trên máy; chưa có bộ từ chối ảnh ngoài phạm vi được kiểm chứng. |
| 0:25–0:55 | Chọn Khoai tây Early blight → Dùng ảnh mẫu | Ảnh train có nguồn và checksum. Xem trước ảnh, tên, kích thước; ảnh mẫu không chứng minh accuracy. |
| 0:55–1:30 | Bấm Phân tích ảnh | Mẫu đã kiểm tra cho nhãn Potato EB, điểm khoảng 85,58%; đọc top 3. Điểm softmax khác tỷ lệ dự đoán đúng trên tập ảnh. |
| 1:30–2:00 | Bấm Lưu kết quả, mở Lịch sử | Có bản ghi và thumbnail; chỉ lưu theo thao tác chủ động, không lưu ảnh gốc. |
| 2:00–2:30 | Tìm tên ảnh hoặc chọn bộ lọc; tải CSV | CSV giữ tiếng Việt, confidence miền 0–1, model_version và checksum. Không xóa lịch sử thật để minh họa. |
| 2:30–3:25 | Mở Đánh giá; xem Từng lớp và Ma trận | Accuracy 92,27%, macro F1 91,85% của 776 ảnh. Nhắc không độc lập; chỉ ra nhầm lẫn Tomato LB/EB và support nhỏ. |
| 3:25–4:00 | Mở Hướng dẫn, chỉ nguồn GitHub | Checkpoint/ảnh public, điều kiện giấy phép, giới hạn ngoài đồng, phần đóng góp và hướng tiếp theo. |

Nếu ứng dụng lỗi, dành tối đa 20 giây kiểm tra server/đường dẫn/mẫu cục bộ rồi mở `deliverables/phase7/demo-agri-leaf.mp4`. Video dài 4 phút, 1080p, phụ đề đã gắn vào hình; được dựng từ ảnh chụp ứng dụng thật, không phải bản ghi thao tác liên tục và không có giọng đọc. Có thể nói theo `demo-scenes.json` hoặc tệp SRT. Không trình bày video như phép đo tốc độ thực thi.

## Câu hỏi thường gặp

**Vì sao chọn đề tài này?** Có code MIT, checkpoint public và dữ liệu public; phạm vi sáu lớp đủ rõ để phát triển UI/UX và kiểm chứng có thể truy vết trong học phần.

**Em đã huấn luyện mô hình chưa?** Chưa. Dự án kế thừa checkpoint và notebook, kiểm tra pipeline, dữ liệu và ứng dụng. Muốn đáp ứng yêu cầu tự train cần một nhánh thực nghiệm bổ sung.

**ResNet có gì đặc biệt?** Khối dư cộng biểu diễn đầu vào vào kết quả nhánh biến đổi, giúp tối ưu mạng sâu. Dự án dùng ResNet18 theo nguồn He et al.; không phát minh kiến trúc mới.

**Vì sao không Normalize theo ImageNet?** Checkpoint được kiểm chứng với RGB → Resize224 → ToTensor. Tự thêm chuẩn hóa sẽ thay đầu vào mô hình; muốn đổi phải đánh giá lại có giao thức.

**Chia train/test rồi sao còn nói không độc lập?** Vì checkpoint đã huấn luyện trước khi dự án chia tập. Không có danh sách train gốc nên không biết ảnh test mới từng được học chưa. Chia theo nhóm chỉ ngăn rò rỉ giữa partition mới.

**92,27% khác 93,69% thế nào?** 92,27% là kiểm chứng của dự án trên 776 ảnh. 93,69% là tác giả gốc công bố. Chưa cùng tập/giao thức nên không kết luận mô hình giảm hay tăng chất lượng.

**Vì sao cần macro F1?** Accuracy bị ảnh hưởng bởi lớp có nhiều ảnh. Macro F1 lấy trung bình sáu F1 theo lớp, giúp nhìn rõ chất lượng của các lớp ít mẫu; vẫn cần đọc support.

**Precision 100% của Potato healthy có hoàn hảo không?** Không. Có 23 dự đoán lớp này đúng, nhưng bỏ sót 5/28 ảnh thật; recall 82,14%, test chỉ bảy nhóm lá.

**Điểm 85,58% có nghĩa ảnh đúng với xác suất đó không?** Đây là softmax trong sáu lựa chọn, chưa hiệu chuẩn xác suất đúng. Ảnh lạ vẫn nhận nhãn và có thể điểm cao.

**33,59 ms đo gì?** Median giải mã/validation, preprocessing, forward và softmax CPU của giao thức 776 ảnh, không tính đọc file/checksum hoặc tương tác trình duyệt.

**Dữ liệu cá nhân được lưu ở đâu?** Ảnh phân tích trong bộ nhớ. Khi chủ động lưu, SQLite trên máy giữ metadata và thumbnail, không giữ ảnh gốc; các phiên cùng máy chia sẻ lịch sử.

**Em tự làm được phần nào?** Nêu UI/UX Việt, module/API, audit và split, lịch sử/CSV, kiểm chứng/artifacts, tests/CI/GitHub và tài liệu; công khai hỗ trợ Codex và nguồn kế thừa.

**Sẽ cải thiện thế nào?** Tập ngoài đồng độc lập có nhãn, chia theo cây/địa điểm/thời gian, train lại và chọn bằng validation, so sánh cùng giao thức; hiệu chuẩn điểm và kiểm chứng từ chối ảnh lạ. Đây là đề xuất.
