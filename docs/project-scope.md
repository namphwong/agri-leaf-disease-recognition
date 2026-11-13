# Phạm vi dự án

- Ngày lập: 12/11/2026 (Asia/Bangkok).
- Chủ dự án: namphwong.
- Học phần: Nhận dạng mẫu.
- Tên đề tài: Xây dựng ứng dụng nhận dạng bệnh trên lá khoai tây và cà chua sử dụng ResNet18.
- Repository: https://github.com/namphwong/agri-leaf-disease-recognition
- Trạng thái: Phase 0–5 hoàn thành; Phase 6 có kiểm chứng 776 ảnh, metrics/biểu đồ và CI. Đây không phải test độc lập của checkpoint kế thừa. Yêu cầu riêng giảng viên chờ xác nhận.

## 1. Mục tiêu và người dùng

Xây dựng ứng dụng phục vụ học tập cho phép người dùng tải ảnh một lá, xem kết quả phân loại, so sánh top 3 và lưu lịch sử. Người dùng chính là sinh viên, giảng viên và người xem demo. Phần đóng góp dự kiến gồm UI/UX tiếng Việt, tổ chức code, lưu lịch sử, kiểm chứng mô hình và tài liệu thực nghiệm.

## 2. Bài toán

Đây là phân loại ảnh đa lớp có giám sát. Đầu vào JPG/JPEG/PNG chứa một lá khoai tây hoặc cà chua. Đầu ra là một trong sáu nhãn, điểm softmax và top 3. Không phải bài toán khoanh vùng tổn thương, đo mức độ bệnh hoặc phát hiện nhiều lá.

| Nhãn gốc (thứ tự mô hình) | Hiển thị đề xuất |
|---|---|
| Potato___Early_blight | Khoai tây — Early blight |
| Potato___Late_blight | Khoai tây — Late blight |
| Potato___healthy | Khoai tây — Lá khỏe |
| Tomato___Early_blight | Cà chua — Early blight |
| Tomato___Late_blight | Cà chua — Late blight |
| Tomato___healthy | Cà chua — Lá khỏe |

Giữ tên bệnh tiếng Anh đến khi xác minh thuật ngữ tiếng Việt. Không đổi thứ tự nhãn hoặc tiền xử lý khi chỉ sửa UI. Điểm softmax không được trình bày như xác suất kết luận đúng đã được hiệu chuẩn.

## 3. Công nghệ và quyết định

- Python, PyTorch/torchvision, ResNet18, Streamlit; SQLite khi xây chức năng lịch sử.
- Kế thừa checkpoint và notebook gốc; đã kiểm chứng CPU tại Phase 2, xem `docs/baseline.md`.
- Môi trường đã kiểm chứng: Python 3.11.9 x64, torch 2.8.0+cpu, torchvision 0.23.0+cpu; phiên bản được ghim trong requirements và lockfile.
- Phase 6 thêm matplotlib 3.10.8 cùng dependency bổ sung ghim tại `requirements-dev.txt` để xuất hình; runtime lock không đổi. Báo cáo kiểm chứng và CI xem `docs/evaluation.md`.
- Không cần tài khoản người dùng, dịch vụ trả phí hoặc API bên ngoài cho luồng chính.
- Phase 4 tách dịch vụ vào `src/`; Phase 5 thêm `src/ui/`, SQLite cục bộ, thumbnail và CSV. Upload JPEG/PNG 20 MiB/16 triệu pixel. Xem `docs/architecture.md` và `docs/ui-ux.md`.
- Phase 5 có `.env.example` minh họa `AGRI_HISTORY_PATH` tùy chọn, không phải secret; app không tự đọc `.env`. Xem `docs/history.md`.

## 4. Yêu cầu chức năng và nghiệm thu

| ID | Chức năng bắt buộc | Điều kiện nghiệm thu |
|---|---|---|
| FR-01 | Tải ảnh, xem trước | JPG/JPEG/PNG hợp lệ hiển thị được; file lỗi có thông báo dễ hiểu |
| FR-02 | Nhận dạng | Hiển thị nhãn, top 3 và điểm softmax đúng thứ tự; không tự thay đổi pipeline gốc |
| FR-03 | UI tiếng Việt | Luồng tải ảnh → phân tích → kết quả rõ ràng; có trạng thái rỗng, xử lý, lỗi |
| FR-04 | Lịch sử SQLite | Lưu/đọc/xóa kết quả theo thao tác người dùng; hoạt động sau khi khởi động lại |
| FR-05 | Xuất CSV | Xuất lịch sử với thời gian, ảnh, nhãn, điểm và phiên bản mô hình |
| FR-06 | Trang đánh giá | Có nguồn số liệu, mô tả tập ảnh, accuracy, macro F1 và confusion matrix từ lần chạy thực tế |
| FR-07 | Hướng dẫn, giới thiệu | Công bố sáu lớp, nguồn kế thừa, giấy phép, hạn chế và điều kiện ảnh |

Mở rộng khi bản bắt buộc ổn định: Grad-CAM, batch, camera, triển khai online, so sánh mô hình. Không thuộc bản v1: tư vấn thuốc/liều lượng, phát hiện mọi loại bệnh, ứng dụng di động riêng, quản lý trang trại.

## 5. Yêu cầu chất lượng

- Chạy được trên CPU; ghi cấu hình và thời gian đo ở Phase 6, chưa cam kết độ trễ.
- Cache mô hình; xử lý file không hợp lệ, thiếu trọng số và lỗi lưu dữ liệu.
- Không đưa ảnh upload, database, token, môi trường ảo hoặc dataset lên Git.
- Người khác clone và chạy theo README từ môi trường sạch trước phát hành.
- Kiểm tra UI trên màn hình laptop và màn hình hẹp; nội dung và trạng thái không chỉ phân biệt bằng màu.

## 6. Dữ liệu và đánh giá

Nguồn: PlantVillage, chỉ chọn sáu lớp trong `raw/color`. Phase 3 đã tải và audit đủ 6.652 ảnh; 1.582 ảnh thiếu mapping nhóm lá được cách ly, 5.070 ảnh còn lại tạo split có seed theo nhóm. Nguồn/phiên bản, checksum, ảnh lỗi, trùng và mất cân bằng xem `docs/dataset.md` và `reports/dataset/`. Đây không phải bước huấn luyện hoặc đo test accuracy.

Checkpoint kế thừa có thể đã học trên ảnh được chọn để kiểm chứng. Nếu không truy được danh sách train/test gốc, không gọi lần chạy đó là test độc lập. Nếu cần thực nghiệm độc lập, huấn luyện lại với split theo lá vật lý (`leaf_id`), tách validation/test và cố định seed. Đổi split không khiến checkpoint có sẵn trở thành mô hình chưa từng thấy test.

Kết quả 93,69% trong tài liệu gốc là số liệu tác giả, không phải kết quả dự án này. Bảng kết quả tự chạy phải ghi checkpoint, pipeline, tập ảnh, cấu hình, ngày chạy và giới hạn. Ảnh ngoài đồng dùng khảo sát khả năng tổng quát, không gộp tùy tiện với benchmark.

## 7. Yêu cầu học phần chờ xác nhận

| Nội dung | Trạng thái | Tác động |
|---|---|---|
| Cho phép dùng trọng số có sẵn | Chưa có đề bài/rubric | Có thể cần huấn luyện lại |
| Bắt buộc so sánh thuật toán | Chưa xác định | Bổ sung baseline và thời gian thực nghiệm |
| Mẫu báo cáo, độ dài, trích dẫn | Chưa xác định | Chốt trước Phase 7 |
| Deadline, hình thức nộp, thành viên | Chưa xác định | Lịch hiện là ước lượng, không phải hạn nộp |

Chưa có thông tin không cản trở thiết lập repo và chạy baseline. Không mặc định giảng viên đã chấp thuận việc chỉ kế thừa mô hình.

## 8. Rủi ro

| Rủi ro | Cách xử lý |
|---|---|
| Dependency không tương thích | Chạy baseline trước, khóa môi trường sau khi kiểm chứng |
| Nhầm thứ tự lớp hoặc tiền xử lý | Đối chiếu app và notebook; kiểm tra hồi quy khi tách code |
| Rò rỉ dữ liệu, không rõ split checkpoint | Công khai giới hạn hoặc huấn luyện lại với split theo lá |
| Ảnh ngoài phạm vi vẫn được phân loại | Hướng dẫn rõ phạm vi; không coi confidence thấp/cao là bộ phát hiện ảnh lạ |
| Mất cân bằng lớp | Báo cáo per-class và macro F1 |
| Phình phạm vi | Hoàn thành chức năng bắt buộc trước các mục mở rộng |

## 9. Hoàn thành dự án

Repo public có nguồn gốc và lịch sử; app chạy theo README; có kết quả kiểm chứng đúng phạm vi; báo cáo, slide, video; kiểm tra cài mới và release v1.0.0. Tình trạng hoàn thành từng phase theo `docs/roadmap.md` và GitHub Issues.
