# UI/UX và nghiệm thu Phase 5

Ngày hoàn thành triển khai: 12/11/2026. Sản phẩm Streamlit **Agri Leaf**, tiếng Việt, tông xanh lá trên nền sáng. Bốn mục điều hướng: Nhận dạng, Lịch sử, Đánh giá, Hướng dẫn. Không thêm framework hoặc dependency runtime mới.

## Thiết kế và luồng

Thiết kế theo ba bước: chọn ảnh → phân tích → xem/lưu. Trước triển khai đã chọn bố cục hai cột ở laptop và xếp dọc ở màn hình hẹp; sidebar chứa điều hướng, nội dung chính có heading và card theo nhiệm vụ.

```text
Laptop
┌─────────────┬──────────────────────────────────────────┐
│ Agri Leaf   │ Tiêu đề và phạm vi                       │
│ Nhận dạng   │ Chọn ảnh từ máy        | Ảnh mẫu          │
│ Lịch sử     │ Xem trước + Phân tích  | Kết quả + Top 3  │
│ Đánh giá    │                       | Lưu kết quả      │
│ Hướng dẫn   │ Hướng dẫn ngắn / nguồn                   │
└─────────────┴──────────────────────────────────────────┘
Màn hình hẹp: sidebar thu gọn; các card xếp dọc.
```

- Người dùng thấy hướng dẫn và phạm vi ngay khi chưa có ảnh.
- Có ảnh mới: xóa kết quả cũ để không lưu nhầm kết quả của ảnh trước.
- Xem trước ảnh hợp lệ trước khi chủ động bấm **Phân tích ảnh**.
- Chỉ tải model khi phân tích; đổi tab hoặc lưu không tự chạy lại model.
- Kết quả có loại cây/nhóm lá, điểm softmax, top 3, mô tả có giới hạn. Dưới 60% có gợi ý ảnh rõ hơn; không gọi đây là bộ phát hiện ảnh lạ.
- **Lưu kết quả** là hành động riêng, không tự lưu khi upload hoặc phân tích.
- **Chọn ảnh khác** xóa ảnh/kết quả trong session, không xóa lịch sử đã lưu.
- Khi model hoặc lịch sử lỗi, hiển thị lỗi tiếng Việt; trang khác vẫn dùng được. Lỗi kỹ thuật được log ở server.

Giữ tên bệnh Early blight/Late blight theo nhãn nguồn, chưa tự dịch thành tên bệnh Việt có thể gây nhầm. Nội dung chính và các thao tác do dự án viết là tiếng Việt; một số chrome của Streamlit như Upload/Deploy vẫn theo giao diện framework.

## Chức năng theo trang

| Trang | Đã triển khai |
|---|---|
| Nhận dạng | Upload, kiểm tra JPEG/PNG 20 MiB/16 triệu pixel, ảnh mẫu, xem trước, phân tích, top 3, điểm thấp, lưu chủ động |
| Lịch sử | Ảnh xem trước, nhãn/thời gian/version, tìm tên có dấu không phân biệt hoa thường, lọc cây/nhãn/ngày, 10 mục/trang, CSV toàn bộ kết quả theo lọc |
| Đánh giá | Số liệu audit từ JSON đã chạy, biểu đồ phân bố lớp, bảng split, kiểm chứng 6 ảnh và giới hạn của mô hình kế thừa |
| Hướng dẫn | Chụp ảnh, sáu nhóm hỗ trợ, đọc softmax, vị trí lưu, nguồn code/dữ liệu, phạm vi học tập |

FR-01/02/03/04/05/07 đã có luồng ứng dụng. FR-06 đã có trang minh chứng và số liệu dữ liệu/baseline; accuracy, per-class precision/recall/F1 và confusion matrix trên bộ đánh giá đầy đủ vẫn thuộc **thực nghiệm Phase 6**. Không dựng số liệu để lấp chỗ trống hoặc gọi smoke check 6 ảnh là 100% test accuracy.

## Ảnh mẫu

Sáu lựa chọn lấy từ manifest train của Phase 3. Nếu nguồn ảnh có sẵn trong `data/plantvillage-source`, dùng bytes cục bộ và xác minh checksum. Nếu chưa tải dataset, chỉ tải ảnh đang chọn từ URL GitHub public có commit cố định, kiểm tra SHA-256 rồi cache trong bộ nhớ Streamlit. Không tải cả dataset khi mở app.

Ảnh mẫu/screenshot chứa ảnh PlantVillage: [nguồn](https://github.com/spMohanty/PlantVillage-Dataset), snapshot `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`; dataset card công bố [CC BY-SA 3.0](https://huggingface.co/datasets/mohanty/PlantVillage). Ảnh trong screenshot laptop là ứng viên train Potato Early blight ở `reports/dataset/demo_samples.json`, không lấy từ test mới.

## Kiểm chứng

- **32 test** (unit/AppTest) bao phủ pipeline/dữ liệu, SQLite, truy vấn/xuất CSV, lưu trùng/concurrency, đổi ảnh, lỗi model/lịch sử, điều hướng và xóa có xác nhận.
- Test UI dùng ảnh tổng hợp trong bộ nhớ và database tạm để chạy offline. Không xóa lịch sử người dùng. Mock mạng kiểm tra fallback ảnh mẫu và sai checksum.
- Regression sáu ảnh thật vẫn đối chiếu mã trước refactor và JSON Phase 2; toàn bộ sáu điểm đầu ra có chênh lệch lớn nhất bằng 0. Xem [phase5-results.json](../reports/baseline/phase5-results.json).
- Browser thực: chọn ảnh train → phân tích → kết quả → lưu → lịch sử → tải CSV thành công; đã mở các trang Đánh giá/Hướng dẫn.
- Đã kiểm tra laptop **1280×900** và màn hình hẹp **390×844**. Tại trang nhận dạng/đánh giá hẹp, DOM báo scrollWidth = innerWidth = 390, không tràn ngang toàn trang. Bảng có thể cuộn ngang bên trong khi cần.
- Screenshot đã xem và lưu: [laptop](screenshots/phase5-desktop.jpg), [màn hình hẹp](screenshots/phase5-mobile.jpg).
- [Biên bản QA dạng JSON](../reports/ui/phase5-checks.json) ghi số test, luồng browser, CSV và checksum screenshot.
- Native file chooser và trình duyệt điện thoại thật chưa được tự động hóa; upload bytes được kiểm tra qua AppTest. Chưa triển khai public hoặc có đăng nhập.

Trong lần phát triển, import pandas/chart đã gặp DLL bị Windows Application Control chặn. Trang thống kê được xây bằng thành phần Streamlit cơ bản và bảng Markdown, không import pandas trong code ứng dụng. Không đổi chính sách Windows hoặc dependencies đã khóa.

## Chạy và bước tiếp

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Xem [lịch sử và CSV](history.md) để cấu hình database. Phase 6 tiếp tục đánh giá mô hình với phạm vi công bố đúng, kiểm thử bổ sung và CI; Phase 5 không huấn luyện lại hoặc thay checkpoint.
