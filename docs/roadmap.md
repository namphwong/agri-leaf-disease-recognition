# Kế hoạch triển khai

Ngày bắt đầu: 12/11/2026. Ước lượng 12 ngày làm việc và 2 ngày dự phòng; không phải deadline học phần. Đã triển khai Phase 0–4; ngày trong bảng là kế hoạch ước lượng ban đầu.

| Phase | Công việc và đầu ra | Gate trước khi chuyển tiếp | Ước lượng |
|---|---|---|---|
| 0 — Phạm vi | Đặc tả, FR-01..07, giả định, rủi ro, tiêu chí hoàn thành | Phạm vi có văn bản; yêu cầu giảng viên chưa rõ được ghi nhận | Ngày 1 |
| 1 — GitHub | Fork, origin/upstream, README, nguồn, nhánh, issues/milestones, PR | Fork public đúng tài khoản; tài liệu đã đồng bộ; lịch sử nguồn giữ nguyên | Ngày 1 |
| 2 — Baseline | Môi trường riêng; chạy 6 lớp; đối chiếu notebook; khóa dependencies; `docs/baseline.md` | Bản gốc chạy CPU; lưu cấu hình và bằng chứng; kiểm tra khả năng tái lập | Ngày 2 |
| 3 — Dữ liệu | Tải 6 lớp; thống kê; kiểm tra lỗi/trùng; xác định split; `docs/dataset.md` | Có nguồn/phiên bản/danh sách tập ảnh và giới hạn đánh giá | Ngày 3 |
| 4 — Code | Tách inference, preprocessing, labels, validation, storage | Cùng ảnh cho kết quả tương đương baseline | Ngày 4 |
| 5 — UI/UX | Wireframe, tiếng Việt, nhận dạng, SQLite, CSV, trang đánh giá/giới thiệu | FR-01..07 có luồng hoàn chỉnh và trạng thái lỗi | Ngày 5–7 |
| 6 — Kiểm chứng | Metrics, confusion matrix, latency, case sai; test chức năng quan trọng; CI nhẹ | Số liệu truy được về lần chạy; hết lỗi chặn demo | Ngày 8–9 |
| 7 — Báo cáo | Báo cáo, 10–12 slide, video, demo 3–5 phút, bảng đóng góp | Tài liệu khớp ứng dụng, nguồn và số liệu | Ngày 10–11 |
| 8 — Phát hành | Clone sạch, kiểm tra README, release v1.0.0 và ghi chú | Người khác có thể tái lập; artifacts và link nộp đủ | Ngày 12 |

## Thứ tự và thay đổi phạm vi

Phase 2 và 3 là cơ sở cho Phase 4–6. Nếu giảng viên yêu cầu tự huấn luyện hoặc so sánh, cập nhật scope và issue trước, dự trù thêm 2–4 ngày; thời gian thực tế phụ thuộc tài nguyên. Không tự công bố đã hoàn thành phase khi còn gate chưa đạt.

## Mốc GitHub

- M1 — Baseline chạy được: Phase 0–3.
- M2 — Hoàn thiện ứng dụng: Phase 4–5.
- M3 — Đánh giá và bàn giao: Phase 6–8.

Issue là nguồn theo dõi trạng thái thực thi. Phase 0–1 hoàn thành qua PR #11; Phase 2 qua PR #12; Phase 3 qua PR #13. Phase 4 có module pipeline, đầu ra thống nhất, record lưu trữ và hồi quy khớp mã gốc; xem `docs/architecture.md`, tích hợp theo issue #5. Yêu cầu riêng học phần chờ xác nhận tại issue #2. Phase 5–8 chưa thực hiện.
