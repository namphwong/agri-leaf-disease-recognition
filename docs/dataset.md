# Dữ liệu và thiết kế đánh giá — Phase 3

Ngày chuẩn bị: **12/11/2026**, Asia/Bangkok. Đã tải và audit đầy đủ sáu lớp trong phạm vi đề tài; chưa huấn luyện hoặc đánh giá toàn bộ mô hình ở phase này.

## 1. Nguồn, phiên bản và giấy phép

- Repository: [spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset).
- Commit cố định: [`7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`](https://github.com/spMohanty/PlantVillage-Dataset/tree/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a).
- Ảnh: `raw/color/`, chỉ tải sáu thư mục được app hỗ trợ bằng Git sparse checkout.
- Metadata nhóm lá: `leaf-map.json` ở cùng commit; cách lấy identifier đối chiếu với `plant_village.py` của nguồn.
- Dataset card `README_HF.md` tại commit trên công bố **CC BY-SA 3.0**. Thông tin trực tuyến: [dataset card](https://huggingface.co/datasets/mohanty/PlantVillage), [giấy phép](https://creativecommons.org/licenses/by-sa/3.0/).
- Trích dẫn: Mohanty, Hughes & Salathé (2016), *Using deep learning for image-based plant disease detection*, [DOI](https://doi.org/10.3389/fpls.2016.01419).

Code dự án giữ MIT; dữ liệu và metadata dẫn xuất được ghi nguồn theo CC BY-SA 3.0 của dataset card, không chuyển giấy phép dữ liệu sang MIT. Chỉ commit metadata, thống kê và thiết kế split; không commit các ảnh hoặc kho Git nguồn nằm trong `data/`.

## 2. Dữ liệu đã tải và kiểm tra

| Index mô hình | Lớp | Ảnh gốc | Không xác định nhóm lá |
|---:|---|---:|---:|
| 0 | Potato — Early blight | 1.000 | 0 |
| 1 | Potato — Late blight | 1.000 | 0 |
| 2 | Potato — healthy | 152 | 0 |
| 3 | Tomato — Early blight | 1.000 | 1 |
| 4 | Tomato — Late blight | 1.909 | 989 |
| 5 | Tomato — healthy | 1.591 | 592 |
| | **Tổng** | **6.652** | **1.582** |

- Tổng dung lượng ảnh: **115.668.187 bytes**, khoảng 110,31 MiB; không gồm Git metadata/cache.
- 6.652/6.652 ảnh xác minh Git blob SHA đúng snapshot nguồn, `Pillow.verify()` và giải mã pixel đầy đủ thành công.
- Tất cả ảnh có kích thước **256 × 256**, mode **RGB**.
- Không phát hiện file lỗi giải mã; không có nhãn ngoài sáu lớp trong checkout được chọn.
- Có **14 cặp trùng byte**, cũng trùng hoàn toàn sau giải mã RGB: 28 ảnh, 14 bản dư. Tất cả thuộc phần chưa ánh xạ được nhóm lá nên đã được cách ly cùng phần đó.
- Tỷ lệ lớp nhiều nhất/ít nhất trong dữ liệu gốc: **12,56 lần**. Lớp Potato healthy ít mẫu, cần báo cáo chỉ số từng lớp và macro F1.

Các kiểm tra trên không xác minh độ đúng của nhãn bệnh bằng chuyên gia và chưa tìm hết ảnh gần trùng qua perceptual similarity. Không suy diễn “không có ảnh lỗi” thành “nhãn hoàn toàn chính xác”.

## 3. Chính sách nhóm lá và cách ly

Nhiều ảnh có thể là các góc chụp của cùng một lá. Không chia ngẫu nhiên từng ảnh như notebook gốc.

1. Lấy identifier từ tên file theo logic của nguồn, tra `leaf-map.json`.
2. Chỉ nhận mapping có namespace lớp đúng; nếu có nhiều mapping cùng lớp thì liên kết tất cả một cách bảo thủ.
3. Nối các ảnh có chung leaf ID, hash byte hoặc hash pixel RGB thành một thành phần liên thông. Liên kết có tính bắc cầu.
4. Nếu thành phần có ảnh lỗi, ảnh không có leaf ID hoặc nhiều nhãn xung đột, đưa **toàn bộ thành phần** vào `quarantine`.
5. Với phần đủ điều kiện, giữ một đại diện cho mỗi ảnh RGB giống hệt; các bản dư không dùng huấn luyện/đánh giá.

Lần chạy hiện tại: **1.582 ảnh cách ly do thiếu mapping**, không phải do phát hiện chúng sai nhãn. Không xóa ảnh, không tự gán mỗi ảnh thiếu mapping thành một lá độc lập. Chỉ xem xét đưa trở lại khi có metadata hoặc bằng chứng nhóm lá đủ rõ; sau đó tạo phiên bản manifest mới và kiểm tra lại split.

Phần đủ điều kiện còn **5.070 ảnh thuộc 1.268 nhóm**. Trong phần này không có bản trùng RGB cần loại thêm. Việc bỏ các ảnh thiếu metadata làm thay đổi phân bố dữ liệu, đặc biệt lớp Tomato Late blight/healthy; phải công khai sự khác biệt khi so sánh kết quả.

## 4. Split mới dành cho huấn luyện lại

- Seed: **42**.
- Theo từng lớp, sắp xếp nhóm theo group ID ổn định, shuffle với seed gắn tên lớp.
- Phân bổ khoảng 70%/15%/phần còn lại **theo số nhóm**, bảo đảm ít nhất một nhóm ở mỗi tập. Tỷ lệ ảnh không nhất thiết đúng 70/15/15.
- Cả nhóm thuộc duy nhất một partition. Group ID là hash ổn định của danh sách đường dẫn nguồn trong thành phần.
- Không dùng bản cách ly hoặc bản trùng đã loại. Không tạo thêm bản copy ảnh theo thư mục train/test; dùng manifest.

| Lớp | Train | Validation | Test | Cách ly |
|---|---:|---:|---:|---:|
| Potato — Early blight | 700 | 148 | 152 | 0 |
| Potato — Late blight | 700 | 148 | 152 | 0 |
| Potato — healthy | 104 | 20 | 28 | 0 |
| Tomato — Early blight | 699 | 148 | 152 | 1 |
| Tomato — Late blight | 644 | 136 | 140 | 989 |
| Tomato — healthy | 699 | 148 | 152 | 592 |
| **Tổng** | **3.546** | **748** | **776** | **1.582** |

Số nhóm theo tập: train **887**, validation **187**, test **194**. Potato healthy test có 28 ảnh nhưng chỉ **7 nhóm lá**, nên chỉ số lớp này có độ bất định lớn.

Đã kiểm tra không có group ID, leaf ID hoặc hash ảnh chính xác đi qua nhiều partition. Chạy thuật toán lại với thứ tự ảnh đảo ngược vẫn cho cùng nhóm, split và đại diện được chọn. Điều này xác minh nhất quán theo metadata, không chứng minh metadata gốc mô tả hoàn hảo mọi lá vật lý.

## 5. Hai cách diễn giải kết quả phải tách biệt

### A. Tiếp tục dùng checkpoint kế thừa

Không biết train/test membership gốc. Dù đặt tên tập mới là `test`, checkpoint đó vẫn có thể đã học các ảnh trong tập. Kết quả chạy trên bất kỳ phần PlantVillage nào phải ghi **“kiểm chứng trên dữ liệu có thể trùng huấn luyện”**, kèm `not_independent_for_inherited_checkpoint=true`; không gọi là test accuracy độc lập, không so trực tiếp với 93,69% của tác giả như cùng một benchmark.

### B. Có yêu cầu thực nghiệm độc lập sau huấn luyện lại

1. Khởi tạo mô hình mới từ backbone ImageNet hoặc khởi tạo rõ nguồn; không fine-tune từ checkpoint bệnh lá kế thừa để rồi coi test này là chưa từng thấy.
2. Chỉ fit bằng các hàng train đủ điều kiện trong manifest. Mọi augmentation, cân bằng lớp hoặc trọng số lớp phải chỉ dựa trên train.
3. Dùng validation để chọn epoch, hyperparameters và mọi ngưỡng; không điều chỉnh từ kết quả test.
4. Giữ test để báo cáo lần đánh giá cuối sau khi chốt mô hình. Ghi các lần sử dụng test trong log thực nghiệm.
5. Báo cáo accuracy, macro F1, precision/recall/F1 và support từng lớp; confusion matrix ghi rõ thứ tự từ `labels.json`.
6. Ghi commit code, manifest SHA-256, checkpoint SHA-256, cấu hình, seed, phiên bản thư viện và thời gian chạy. Nếu tính khoảng tin cậy, lấy mẫu theo nhóm lá thay vì coi mọi ảnh là quan sát độc lập.

Split này là split tùy chỉnh của dự án, **không phải** train/test 80/20 do Hugging Face công bố và không tái lập split của tác giả Smart Leaf AI. Ngoài giới hạn metadata, ảnh vẫn thuộc môi trường PlantVillage; chưa đo khả năng tổng quát ngoài đồng.

Quyết định hiện tại: giữ checkpoint có sẵn cho ứng dụng; chuẩn bị split B để sẵn sàng nếu yêu cầu học phần cần huấn luyện. Chưa chạy huấn luyện hoặc xem metrics trên tập test mới.

## 6. Manifest và artifacts

| Artifact | Vai trò |
|---|---|
| [manifest.csv](../reports/dataset/manifest.csv) | 6.652 hàng, nguồn, nhãn/index, hash, kích thước, leaf IDs, group, split, cờ dùng và lý do loại |
| [summary.json](../reports/dataset/summary.json) | Phiên bản nguồn, checksum manifest/metadata, tổng hợp và checks |
| [class_distribution.csv](../reports/dataset/class_distribution.csv) | Số ảnh gốc, cách ly và số ảnh dùng theo lớp/split |
| [duplicates.json](../reports/dataset/duplicates.json) | Các nhóm trùng byte và pixel cùng đường dẫn |
| [labels.json](../reports/dataset/labels.json) | Thứ tự sáu nhãn đúng đầu ra checkpoint |
| [demo_samples.json](../reports/dataset/demo_samples.json) | Sáu ứng viên demo được chọn từ train, dành cho UI sau này |

Khi đọc bằng `csv.DictReader`, cờ boolean là chuỗi: chỉ lấy hàng có `use_for_training_evaluation == "True"` và split mong muốn. `leaf_ids` là chuỗi JSON cần parse; `local_path` tương đối với root dự án. Không dùng trực tiếp toàn bộ ảnh trong thư mục để huấn luyện vì sẽ bỏ qua cách ly và split.

`.gitattributes` giữ metadata CSV/JSON ở LF để checksum manifest không đổi khi checkout trên Windows. Timestamp summary có thể thay đổi khi chạy lại; membership và checksum manifest phải giữ nguyên với cùng dữ liệu/code/seed.

## 7. Tái lập và kiểm thử

Từ môi trường Phase 2 đã cài lockfile:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_dataset.py --download
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

`--download` cần Git và internet; tải sparse checkout ở commit ghim, từ chối ghi đè khi checkout nguồn có thay đổi. Các lần chỉ audit lại dùng `python scripts/prepare_dataset.py` bằng interpreter môi trường dự án. Script đọc metadata nguyên bản từ Git blob để tránh khác biệt line ending.

Đã chạy luồng tải và audit thực tế; mọi ảnh đúng Git blob. **Sáu unit test** đạt, bao phủ: liên kết bắc cầu qua lá/ảnh trùng, cách ly thành phần thiếu metadata, xung đột nhãn, trường hợp chỉ ba nhóm, ổn định khi đảo thứ tự và mapping mơ hồ cùng lớp.

Không thêm dependency runtime, không thay ứng dụng/checkpoint/notebook. Phase 4 tiếp theo sẽ tách pipeline mô hình khỏi giao diện; không tự chuyển sang huấn luyện trong Phase 3.
