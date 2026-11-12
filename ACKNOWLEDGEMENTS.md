# Nguồn kế thừa và đóng góp

## Mã nguồn và mô hình

Dự án fork từ [Smart Leaf AI](https://github.com/spneoarm/smart-leaf-ai), tác giả **Supanut Eiamoon (spneoarm)**, giấy phép MIT. Điểm bắt đầu: commit `1c5be55` (bản đầy đủ xem lịch sử Git). Giữ nguyên `LICENSE` và lịch sử gốc.

Các thành phần kế thừa: `app.py`, checkpoint `models/leaf_model_final.pth`, notebook `notebooks/plant_leaf_disease_classification_training.ipynb`, dependencies, ảnh demo và mô tả kết quả trong README gốc. Bản README gốc được giữ tại `docs/upstream-README.md`; demo liên kết trong đó là của tác giả gốc.

93,69% test accuracy là số liệu tác giả công bố. Phase 2 của namphwong chỉ kiểm chứng sáu ảnh mẫu và runtime CPU, không tái lập test set gốc; xem `docs/baseline.md`.

## Dữ liệu

- [PlantVillage GitHub](https://github.com/spMohanty/PlantVillage-Dataset).
- [Dataset card của mohanty/PlantVillage](https://huggingface.co/datasets/mohanty/PlantVillage), công bố CC BY-SA 3.0; giấy phép dữ liệu tách biệt với MIT của code. Khi tải hoặc phân phối lại, ghi phiên bản, tác giả và điều kiện áp dụng của nguồn dữ liệu cụ thể.
- Phase 3 dùng ảnh và leaf mapping ở commit `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`. Metadata dẫn xuất trong `reports/dataset/` ghi nguồn theo CC BY-SA 3.0; các script mới theo MIT của dự án. Không commit ảnh hoặc Git cache nguồn. Chi tiết ở `docs/dataset.md`.
- Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). *Using deep learning for image-based plant disease detection*. Frontiers in Plant Science, 7, 1419. https://doi.org/10.3389/fpls.2016.01419

## Kiến trúc và thư viện

- ResNet: He et al. (2016), *Deep Residual Learning for Image Recognition*. https://arxiv.org/abs/1512.03385
- PyTorch/torchvision, Streamlit, Pillow và các thư viện theo dependencies; giấy phép riêng của từng thư viện vẫn áp dụng.

## Đóng góp của namphwong

Đã thực hiện trong Phase 0–1: thiết lập fork, đặc tả, kế hoạch, quy trình GitHub, tài liệu ghi nguồn và quản lý công việc.

Đã thực hiện ở Phase 2: môi trường CPU đã kiểm chứng, ghim dependencies, manifest sáu ảnh mẫu, script kiểm chứng pipeline/app và kết quả baseline có giới hạn rõ ràng. Không thay đổi app, checkpoint hoặc notebook gốc.

Đã thực hiện ở Phase 3: tải đầy đủ sáu lớp, audit 6.652 ảnh, cách ly metadata chưa đủ, xử lý nhóm ảnh trùng, tạo split tái lập, chọn ứng viên demo từ train và kiểm thử chống rò rỉ. Chưa huấn luyện lại hoặc đánh giá toàn dataset.

Dự kiến ở các phase sau: tái cấu trúc code, UI/UX tiếng Việt, lịch sử SQLite, xuất CSV, đánh giá dataset và báo cáo. Các mục dự kiến chưa được tính là đã triển khai.
