# Changelog

## Unreleased

### Added — Phase 6, 2026-11-13

- Kiểm chứng checkpoint kế thừa trên 776 ảnh/194 nhóm: accuracy 92,27%, macro F1 91,85%; không phải test độc lập.
- Dự đoán từng ảnh, per-class metrics, confusion matrix, group bootstrap, biểu đồ thời gian và ví dụ đúng/sai có nguồn.
- Runner đánh giá, kiểm tra hash/cohort/metrics từ CSV và test từ chối báo cáo sai; tổng 39 test.
- GitHub Actions Windows/Python 3.11.9, runtime lock, kiểm tra cú pháp/test/artifacts offline; không train trên mỗi commit.
- Trang Đánh giá hiển thị chỉ số có kiểm chứng và điều kiện diễn giải; JSON download, biểu đồ và screenshot.
- Dependencies vẽ hình bổ sung riêng; không đổi runtime lock, checkpoint, preprocessing hoặc dataset split.

### Added — Phase 5, 2026-11-12

- Giao diện Agri Leaf tiếng Việt: nhận dạng, lịch sử, đánh giá và hướng dẫn; theme sáng, bố cục responsive.
- Ảnh mẫu từ train có fallback tải snapshot/checksum, xem trước và lưu kết quả chủ động.
- SQLite schema 1, thumbnail, chống lưu trùng, tìm Unicode/lọc ngày/cây/nhãn, phân trang, xóa có xác nhận, CSV UTF-8 BOM theo toàn bộ bộ lọc.
- Biến đường dẫn history tùy chọn, `.env.example`, tài liệu và screenshot laptop/màn hình hẹp.
- Bộ test tổng 32 case và regression Phase 5 khớp baseline; QA browser lưu/xem/tải CSV.

### Changed — Phase 5, 2026-11-12

- Validation hiển thị lỗi tiếng Việt; app chỉ tải model khi phân tích, đổi ảnh xóa kết quả cũ.
- Công cụ baseline thao tác nút phân tích và nhãn tiếng Việt; giữ nguyên dữ liệu lịch sử.
- Không đổi model/preprocessing, checkpoint, notebook, dataset split hoặc dependencies. Trang đánh giá chưa có metrics độc lập đầy đủ; Phase 6 sẽ thực nghiệm.

### Added — Phase 4, 2026-11-12

- Module config, labels, validation, preprocessing, inference và storage record contract.
- PredictionResult có nhãn/index, sáu điểm, top 3, checksum và model version.
- Validation nội dung JPEG/PNG, giới hạn 20 MiB/16 triệu pixel; record lịch sử chưa thực hiện I/O.
- Chín unit test pipeline và báo cáo regression với mã trước refactor cùng baseline Phase 2.

### Changed — Phase 4, 2026-11-12

- Streamlit gọi dịch vụ, cache theo đường dẫn/mtime/dung lượng, giữ bố cục cũ.
- Công cụ dataset lấy nhãn từ module; baseline script giữ kết quả lịch sử, đối chiếu tham chiếu Git bất biến.
- Không đổi checkpoint, notebook, manifest/split dữ liệu hoặc dependencies. SQLite và UI/UX mới vẫn thuộc Phase 5.

### Added — Phase 3, 2026-11-12

- Script tải snapshot sáu lớp PlantVillage và audit 6.652 ảnh, checksum Git blob/pixel, metadata nhóm lá và bản trùng.
- Manifest, thống kê, nhãn, ứng viên demo từ train; split seed 42 theo nhóm và cách ly ảnh thiếu metadata.
- Sáu unit test cho liên kết bắc cầu, rò rỉ, mapping chưa rõ và phân bổ nhóm.
- Tài liệu nguồn/giấy phép, phân bố dữ liệu và phân biệt kiểm chứng checkpoint kế thừa với test sau huấn luyện lại.
- Git attributes giữ checksum metadata ổn định; ignore chỉ cho phép metadata CSV/JSON trong reports/dataset.

Không đổi ứng dụng, checkpoint, notebook hoặc dependencies runtime. Chưa huấn luyện hoặc đo metrics trên toàn dataset.

### Added — Phase 2, 2026-11-12

- Baseline CPU trên Windows/Python 3.11.9; six-class smoke check và Streamlit AppTest.
- Manifest sáu ảnh public đã ghim commit/checksum; kết quả JSON, kiểm tra HTTP server và ảnh lỗi.
- Script tái lập, tài liệu đối chiếu app/notebook và giới hạn đánh giá.

### Changed — Phase 2, 2026-11-12

- Ghim torch 2.8.0+cpu, torchvision 0.23.0+cpu và dependencies đã chạy thành công.
- Thêm lockfile runtime, cập nhật README/trạng thái và ignore môi trường kiểm chứng phụ.
- Không thay đổi logic ứng dụng, checkpoint hoặc notebook kế thừa.

### Added — 2026-11-12

- Đặc tả phạm vi và tiêu chí nghiệm thu học phần Nhận dạng mẫu.
- Roadmap Phase 0–8 và quy trình làm việc GitHub.
- Ghi nhận nguồn code, checkpoint, dữ liệu và số liệu tác giả.
- README dự án fork; lưu README gốc trong docs.
- Quy tắc bỏ qua dữ liệu và file runtime khi commit.

Tại thời điểm kết thúc Phase 0–1: chưa thay đổi logic ứng dụng, mô hình hoặc dependencies; chưa chạy baseline.
