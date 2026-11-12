# Agri Leaf Disease Recognition

Đồ án học phần **Nhận dạng mẫu** của **namphwong**: xây dựng ứng dụng nhận dạng bệnh trên lá khoai tây và cà chua sử dụng ResNet18.

Fork từ [Smart Leaf AI của spneoarm](https://github.com/spneoarm/smart-leaf-ai), giữ nguyên lịch sử và [MIT License](LICENSE). Chi tiết kế thừa tại [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md); [README gốc](docs/upstream-README.md) được lưu để đối chiếu.

## Trạng thái

Đang thiết lập Phase 0–1: phạm vi, kế hoạch và quản lý GitHub. Ứng dụng, notebook và checkpoint vẫn là bản kế thừa. **Chưa cài môi trường, chạy baseline hoặc có kết quả thực nghiệm riêng.** Các yêu cầu cụ thể của giảng viên về huấn luyện/so sánh thuật toán chờ xác nhận.

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

## Chạy bản kế thừa — chờ xác minh ở Phase 2

Cần Git và Python phù hợp với PyTorch/torchvision. Phiên bản môi trường sẽ được xác định và khóa sau khi kiểm tra baseline.

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Mở http://localhost:8501. Bản gốc cấu hình tải checkpoint trên CPU. Không cần dataset để suy luận bằng checkpoint sẵn có. Hướng dẫn trên chưa được xác nhận chạy thành công tại fork này.

## Dữ liệu và kết quả

- [PlantVillage GitHub](https://github.com/spMohanty/PlantVillage-Dataset), chọn sáu lớp trong `raw/color`.
- [Dataset card](https://huggingface.co/datasets/mohanty/PlantVillage), công bố CC BY-SA 3.0; dữ liệu có điều kiện riêng, không thuộc MIT của code.
- Tác giả gốc báo cáo test accuracy **93,69%**. Đây không phải kết quả namphwong tự đo.
- Không coi tập ảnh lấy từ PlantVillage là test độc lập của checkpoint kế thừa khi chưa xác định giao nhau với tập huấn luyện.

Dataset chưa tải ở Phase 0–1. Quy trình dữ liệu và đánh giá nằm trong [phạm vi dự án](docs/project-scope.md).

## Tài liệu và quản lý công việc

- [Phạm vi và tiêu chí nghiệm thu](docs/project-scope.md).
- [Roadmap Phase 0–8](docs/roadmap.md).
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
.github/                   # Mẫu PR
requirements.txt           # Dependencies gốc, chưa khóa phiên bản
ACKNOWLEDGEMENTS.md        # Nguồn và phân biệt đóng góp
CONTRIBUTING.md            # Quy trình GitHub
```

## Giới hạn

Mô hình luôn chọn một trong sáu lớp, chưa có cơ chế từ chối ảnh ngoài phạm vi được kiểm chứng. Điểm softmax không chứng minh ảnh hợp lệ hoặc kết luận đúng. Ảnh ngoài đồng có thể khác đáng kể với dữ liệu nền đơn giản. Ứng dụng phục vụ học tập; không đưa ra quyết định canh tác hoặc kê thuốc.
