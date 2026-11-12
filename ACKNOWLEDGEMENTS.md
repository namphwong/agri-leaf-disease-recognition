# Nguồn kế thừa và đóng góp

## Mã nguồn và mô hình

Dự án fork từ [Smart Leaf AI](https://github.com/spneoarm/smart-leaf-ai), tác giả **Supanut Eiamoon (spneoarm)**, giấy phép MIT. Điểm bắt đầu: commit `1c5be55` (bản đầy đủ xem lịch sử Git). Giữ nguyên `LICENSE` và lịch sử gốc.

Các thành phần kế thừa: `app.py`, checkpoint `models/leaf_model_final.pth`, notebook `notebooks/plant_leaf_disease_classification_training.ipynb`, dependencies, ảnh demo và mô tả kết quả trong README gốc. Bản README gốc được giữ tại `docs/upstream-README.md`; demo liên kết trong đó là của tác giả gốc.

93,69% test accuracy là số liệu tác giả công bố. Dự án namphwong chưa tự kiểm chứng kết quả hay chạy baseline tại Phase 0–1.

## Dữ liệu

- [PlantVillage GitHub](https://github.com/spMohanty/PlantVillage-Dataset).
- [Dataset card của mohanty/PlantVillage](https://huggingface.co/datasets/mohanty/PlantVillage), công bố CC BY-SA 3.0; giấy phép dữ liệu tách biệt với MIT của code. Khi tải hoặc phân phối lại, ghi phiên bản, tác giả và điều kiện áp dụng của nguồn dữ liệu cụ thể.
- Mohanty, S. P., Hughes, D. P., & Salathé, M. (2016). *Using deep learning for image-based plant disease detection*. Frontiers in Plant Science, 7, 1419. https://doi.org/10.3389/fpls.2016.01419

## Kiến trúc và thư viện

- ResNet: He et al. (2016), *Deep Residual Learning for Image Recognition*. https://arxiv.org/abs/1512.03385
- PyTorch/torchvision, Streamlit, Pillow và các thư viện theo dependencies; giấy phép riêng của từng thư viện vẫn áp dụng.

## Đóng góp của namphwong

Đã thực hiện trong Phase 0–1: thiết lập fork, đặc tả, kế hoạch, quy trình GitHub, tài liệu ghi nguồn và quản lý công việc.

Dự kiến ở các phase sau: tái cấu trúc code, UI/UX tiếng Việt, lịch sử SQLite, xuất CSV, thực nghiệm và báo cáo. Các mục dự kiến chưa được tính là đã triển khai.
