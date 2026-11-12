# Agri Leaf Disease Recognition

Đồ án học phần **Nhận dạng mẫu** của **namphwong**: xây dựng ứng dụng nhận dạng bệnh trên lá khoai tây và cà chua sử dụng ResNet18.

Fork từ [Smart Leaf AI của spneoarm](https://github.com/spneoarm/smart-leaf-ai), giữ nguyên lịch sử và [MIT License](LICENSE). Chi tiết kế thừa tại [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md); [README gốc](docs/upstream-README.md) được lưu để đối chiếu.

## Trạng thái

Phase 0–1 đã hoàn thành. **Phase 2 đã chạy baseline trên CPU**: mô hình tải được, sáu ảnh mẫu khớp nhãn, luồng Streamlit qua kiểm tra tự động. Ứng dụng, notebook và checkpoint vẫn là bản kế thừa; chưa thay UI/UX. Các yêu cầu cụ thể của giảng viên về huấn luyện/so sánh thuật toán chờ xác nhận. Chi tiết và giới hạn trong [baseline](docs/baseline.md).

## Phạm vi

Ảnh một lá JPG/JPEG/PNG → một trong sáu lớp: Potato/Tomato × Early blight/Late blight/healthy. Bản gốc dùng PyTorch, ResNet18, Streamlit và có sẵn checkpoint trong `models/leaf_model_final.pth`.

Mục tiêu v1: UI/UX tiếng Việt, top 3 và điểm tin cậy, lịch sử SQLite, xuất CSV, trang đánh giá và tài liệu. Đây là kế hoạch phát triển, chưa phải các chức năng đã hoàn thành của fork.

## Lấy mã nguồn

```powershell
git clone https://github.com/namphwong/agri-leaf-disease-recognition.git
cd agri-leaf-disease-recognition
git remote add upstream https://github.com/spneoarm/smart-leaf-ai.git
```

`origin` trỏ đến repo namphwong; `upstream` trỏ đến tác giả gốc.

## Chạy bản kế thừa đã kiểm chứng trên Windows

Cần Git và Python 3.11.9 x64. Môi trường đã kiểm chứng: PyTorch 2.8.0 CPU, torchvision 0.23.0, Streamlit 1.67.0. Dùng lockfile để cài đúng toàn bộ phiên bản runtime.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1 --browser.gatherUsageStats=false
```

Mở http://localhost:8501. Không cần dataset để suy luận bằng checkpoint sẵn có. Windows trên máy kiểm chứng không tải được PyTorch 2.15.0/2.10.0, nên không tự nâng phiên bản đã ghim; xem [lịch sử tương thích](docs/baseline.md). Chưa chứng nhận lockfile trên OS/Python khác.

Chạy lại kiểm chứng bằng sáu ảnh đã ghim nguồn và checksum:

```powershell
.\.venv\Scripts\python.exe scripts/baseline_check.py --restore-samples --result-name local-results.json
```

## Dữ liệu và kết quả

- [PlantVillage GitHub](https://github.com/spMohanty/PlantVillage-Dataset), chọn sáu lớp trong `raw/color`.
- [Dataset card](https://huggingface.co/datasets/mohanty/PlantVillage), công bố CC BY-SA 3.0; dữ liệu có điều kiện riêng, không thuộc MIT của code.
- Tác giả gốc báo cáo test accuracy **93,69%**. Đây không phải kết quả namphwong tự đo.
- Baseline tự chạy: **6/6 ảnh mẫu khớp nhãn**, median CPU forward **27,06 ms/ảnh**; đây là smoke check, không phải accuracy test độc lập. [Kết quả thô](reports/baseline/results.json).
- Không coi tập ảnh lấy từ PlantVillage là test độc lập của checkpoint kế thừa khi chưa xác định giao nhau với tập huấn luyện.

Phase 2 chỉ tải sáu ảnh kiểm chứng vào `data/baseline/` bị ignore. Chưa tải toàn dataset; chuẩn bị và thống kê dữ liệu thuộc Phase 3. Quy trình dữ liệu và đánh giá nằm trong [phạm vi dự án](docs/project-scope.md).

## Tài liệu và quản lý công việc

- [Phạm vi và tiêu chí nghiệm thu](docs/project-scope.md).
- [Roadmap Phase 0–8](docs/roadmap.md).
- [Baseline CPU và cách tái lập](docs/baseline.md).
- [Quy trình đóng góp](CONTRIBUTING.md).
- [Changelog](CHANGELOG.md).
- [GitHub Issues](https://github.com/namphwong/agri-leaf-disease-recognition/issues).
- [Milestones](https://github.com/namphwong/agri-leaf-disease-recognition/milestones).

## Cấu trúc hiện tại

```text
app.py                     # App kế thừa, chưa thay đổi
models/                    # Checkpoint gốc
notebooks/                 # Notebook huấn luyện gốc
docs/                      # Phạm vi, roadmap, tài liệu nguồn
scripts/baseline_check.py   # Kiểm chứng CPU và app kế thừa
reports/baseline/          # Manifest và kết quả kiểm chứng
.github/                   # Mẫu PR
requirements.txt           # Dependencies trực tiếp đã ghim
requirements-lock.txt      # Toàn bộ runtime Windows/Python 3.11
ACKNOWLEDGEMENTS.md        # Nguồn và phân biệt đóng góp
CONTRIBUTING.md            # Quy trình GitHub
```

## Giới hạn

Mô hình luôn chọn một trong sáu lớp, chưa có cơ chế từ chối ảnh ngoài phạm vi được kiểm chứng. Điểm softmax không chứng minh ảnh hợp lệ hoặc kết luận đúng. Ảnh ngoài đồng có thể khác đáng kể với dữ liệu nền đơn giản. Ứng dụng phục vụ học tập; không đưa ra quyết định canh tác hoặc kê thuốc.
