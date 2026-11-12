# Quy trình phát triển

## Git

- `origin`: https://github.com/namphwong/agri-leaf-disease-recognition.git
- `upstream`: https://github.com/spneoarm/smart-leaf-ai.git
- `main`: bản ổn định; thay đổi qua nhánh ngắn và pull request.
- Ví dụ nhánh: `docs/phase-0-1`, `feat/vietnamese-ui`, `feat/history`, `fix/image-validation`.
- Commit mô tả một thay đổi rõ ràng: `docs: define scope and roadmap`, `feat: add prediction history`.
- Không force-push main hoặc viết lại lịch sử nguồn. Mỗi PR ghi vấn đề, thay đổi, cách xác minh và giới hạn; gắn issue tương ứng.
- Khi cập nhật upstream, xem diff và kiểm tra trên nhánh riêng trước khi tích hợp.

## Vòng đời issue

1. Issue ghi mục tiêu, phạm vi, checklist nghiệm thu và milestone.
2. Tạo nhánh từ main cho công việc đó.
3. Thực hiện, kiểm tra phù hợp, cập nhật tài liệu nếu hành vi thay đổi.
4. PR về **repo namphwong**, không gửi nhầm về upstream.
5. Tự review diff và kiểm tra nguồn/số liệu trước merge. Chỉ đóng issue khi nghiệm thu thực sự đạt.

## Definition of done

- Chức năng đáp ứng tiêu chí issue; trạng thái lỗi chính được xử lý.
- Kiểm tra tương xứng với mức ảnh hưởng; không cần test ứng dụng cho sửa thuần tài liệu.
- Sửa pipeline/mô hình phải kiểm tra nhãn, preprocessing và kết quả hồi quy.
- Số liệu không hard-code thành kết quả thực nghiệm; ghi rõ nguồn và cách chạy.
- Không có token, dataset, ảnh upload, database, môi trường ảo hoặc cache trong diff.
- Tài liệu nhất quán, PR đã merge; main đồng bộ origin.

## Mô hình và dữ liệu

Checkpoint gốc đã được theo dõi trong Git và tiếp tục được giữ. Không commit thêm checkpoint lớn ngoài kế hoạch; khi cần dùng release assets hoặc Git LFS và ghi cách tải. Dataset để trong `data/`, file runtime trong `storage/` hoặc `uploads/`, đều bị ignore. Không tự sửa thứ tự lớp theo bảng chữ cái tiếng Việt.
