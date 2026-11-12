# Changelog

## Unreleased

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
