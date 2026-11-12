# Lịch sử SQLite và xuất CSV

## Hành vi

Chỉ bấm **Lưu kết quả** mới tạo bản ghi. Database mặc định: `storage/history.sqlite3`, dưới thư mục bị Git ignore. Không lưu ảnh gốc; record có ảnh xem trước JPEG tối đa 320×240, giữ tỷ lệ. Ảnh upload và kết quả chưa lưu chỉ nằm trong session hiện tại.

Lịch sử dùng chung cho các phiên trên máy chạy app, chưa có tài khoản hoặc phân quyền. Chỉ chạy demo cục bộ theo hướng dẫn; không công bố app nhiều người dùng mà giả định có lịch sử riêng tư theo tài khoản.

Cùng SHA-256 ảnh và SHA-256 checkpoint chỉ có một bản ghi: nhấn lưu nhiều lần hoặc rerun không làm tăng số mục. Cùng ảnh nhưng checkpoint khác được phép tạo bản ghi riêng. Thời gian là lần lưu đầu, Asia/Bangkok (UTC+7).

## Schema phiên bản 1

SQLite `PRAGMA user_version=1`; bảng `predictions`:

- `id`: UUID, khóa chính.
- `created_at`: ISO 8601 kèm UTC+7.
- `image_name`, `image_sha256`.
- `label`, `confidence` (0–1).
- `model_version`, `checkpoint_sha256`.
- `prediction_json`: sáu điểm, top 3 và metadata đầu ra.
- `thumbnail`: JPEG BLOB, không phải ảnh gốc.

UNIQUE `(image_sha256, checkpoint_sha256)` xử lý lưu trùng kể cả khi hai kết nối đồng thời. Mỗi thao tác mở/đóng kết nối riêng, dùng transaction và timeout 10 giây; không dùng kết nối SQLite chung giữa các thread Streamlit. Query dùng parameters; tìm tên dùng Unicode casefold.

`HistoryStore` có save/list/count/delete/clear. Constructor chưa tạo database; thao tác lưu hoặc truy vấn lịch sử mới khởi tạo schema. Schema tương lai không được tự ghi đè; file hỏng/quyền ghi lỗi trả `HistoryError` có thông báo chung cho UI. Không tự xóa hoặc thay database khi lỗi.

## Lọc, phân trang và xóa

- Tìm một phần tên ảnh, không phân biệt hoa/thường kể cả tiếng Việt.
- Lọc loại cây, nhãn, ngày lưu đầu/cuối (bao gồm hai đầu theo giờ Việt Nam).
- 10 bản ghi mỗi trang; bộ đếm cho biết số phù hợp và tổng số đã lưu.
- Xóa một mục cần checkbox riêng. Xóa toàn bộ cần xác nhận riêng, tác động cả các mục ngoài bộ lọc.
- Xóa không có khôi phục qua UI. Việc xóa record cũng bỏ thumbnail của record khỏi truy vấn lịch sử; không phải công cụ xóa dữ liệu pháp chứng.

## CSV

Nút **Xuất CSV theo bộ lọc** xuất mọi bản ghi phù hợp, không giới hạn ở trang đang xem. Không đọc BLOB thumbnail vào export. UTF-8 BOM hỗ trợ tên tiếng Việt trong Excel.

Cột: `id, created_at, image_name, label, confidence, model_version, checkpoint_sha256, image_sha256`. Nhãn giữ nguyên mã nguồn; confidence là số **0–1**, khác phần trăm ở UI. Không có bytes ảnh trong CSV. Tên bắt đầu bằng ký tự công thức Excel được thêm dấu nháy đơn để giữ dạng text.

## Cấu hình và sao lưu

Biến môi trường tùy chọn:

```powershell
$env:AGRI_HISTORY_PATH = 'storage/history.sqlite3'
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address=127.0.0.1
```

Đường dẫn tương đối được tính từ root dự án; đường dẫn tuyệt đối cũng được hỗ trợ. `.env.example` chỉ là ví dụ, app không tự đọc `.env`. Database không phải secret nhưng có ảnh người dùng, luôn giữ ngoài Git.

CSV phù hợp sao lưu bảng kết quả, không bao gồm thumbnail. Muốn sao lưu đầy đủ, dừng app rồi copy file SQLite sang nơi riêng; không commit bản sao. Khởi động lại app với cùng đường dẫn vẫn đọc lịch sử đã lưu.

QA dùng database riêng `storage/qa-ui.sqlite3`; test tự động dùng thư mục tạm. Không trộn các record QA với lịch sử mặc định.
