# Bộ tài liệu Phase 7

Ngày chuẩn bị: 22/11/2026. Chủ dự án: namphwong. Phạm vi là báo cáo và trình bày ứng dụng kế thừa; chưa train lại hoặc phát hành v1.0.0.

| Đầu ra | Nội dung và cách dùng |
|---|---|
| [Báo cáo Word](../../deliverables/phase7/bao-cao-agri-leaf.docx) | 12 trang, có thể sửa; điền thông tin bìa trước khi nộp |
| [Báo cáo PDF](../../deliverables/phase7/bao-cao-agri-leaf.pdf) | Bản cùng nội dung, bố cục đã kiểm tra từng trang |
| [Slide PowerPoint dự phòng](../../deliverables/phase7/slide-agri-leaf.pptx) | 12 slide editable, có speaker notes và nguồn; kiểm tra bằng LibreOffice sau khi native preview gặp lỗi |
| [Video demo](../../deliverables/phase7/demo-agri-leaf.mp4) | 4 phút, 1920×1080, H.264, 12 fps; phụ đề đã gắn vào hình; không có âm thanh |
| [Phụ đề SRT](../../deliverables/phase7/demo-agri-leaf.srt) | Nội dung nói tương ứng video; có thể dùng để thu giọng đọc riêng |
| [Kịch bản bảo vệ](defense-guide.md) | Lời nói theo 12 slide, demo 4 phút, chuẩn bị, xử lý lỗi và 13 câu hỏi thường gặp |
| [Nguồn các cảnh video](demo-scenes.json) | 12 cảnh, mỗi cảnh 20 giây, ảnh UI thật và 48 đoạn phụ đề |
| [Biên bản bàn giao](../../reports/delivery/phase7.json) | Hash các đầu ra, nguồn số liệu, phạm vi kiểm tra và giới hạn |

Slide editable cũng được lưu tại Spaces Page ID `page_c9ec92984c788191901495603ba250f3` trong tài khoản hiện tại, xem trực tiếp từ liên kết đính kèm câu trả lời Phase 7. Page này không phải liên kết chia sẻ public; người đọc GitHub dùng tệp PPTX trong repository. Không công khai quyền truy cập Spaces tự động. Có thể xuất PowerPoint từ viewer Spaces.

Video được dựng từ ảnh chụp phiên chạy thật ngày 22/11/2026, sau khi đã thao tác chọn mẫu, phân tích, lưu, mở lịch sử và tải CSV. Cảnh phân tích lỗi dùng hình ma trận từ artifact Phase 6 để đọc rõ các ô. Đây là video minh họa bằng ảnh chụp và biểu đồ với phụ đề, không phải screen recording liên tục. Ảnh gốc ở `docs/screenshots/phase7/`; lịch sử demo riêng trong `.phase7-build/` được ignore. Không đưa database hoặc CSV chứa dữ liệu cá nhân vào Git.

## Quy tắc số liệu và nguồn

Nguồn số liệu là `reports/evaluation/latest.json` (lần đo 13/11/2026), dự đoán CSV và manifest Phase 3. Báo cáo, slide và video cùng dùng 716/776, accuracy 92,27%, macro F1 91,85%, median decode+preprocess+predict 33,59 ms. Checkpoint kế thừa có thể trùng train; chưa có test độc lập. 6/6 ảnh chỉ là smoke check; 93,69% thuộc công bố của tác giả gốc.

Code nguồn MIT: [smart-leaf-ai](https://github.com/spneoarm/smart-leaf-ai). Ảnh lá trong screenshot, Word, slide và video từ [PlantVillage snapshot](https://github.com/spMohanty/PlantVillage-Dataset/tree/7f7ecc7e1eaca78107e3affe7cb5abd9427e139a), theo [manifest ảnh demo](../../reports/dataset/demo_samples.json); [dataset card](https://huggingface.co/datasets/mohanty/PlantVillage) công bố [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/). Ảnh được hiển thị trong UI rồi chụp màn hình/thu nhỏ để trình bày. Phần ảnh và bản chuyển thể ảnh giữ điều kiện CC BY-SA 3.0; giấy phép MIT của code không thay quyền dữ liệu. Metadata ví dụ test nằm ở `reports/evaluation/examples.json`.

Tham khảo lý thuyết: [He et al., ResNet](https://arxiv.org/abs/1512.03385) và [Mohanty et al., PlantVillage](https://doi.org/10.3389/fpls.2016.01419). Phân biệt nguồn kế thừa và phần triển khai tại [ACKNOWLEDGEMENTS](../../ACKNOWLEDGEMENTS.md) và mục 10 của báo cáo.

## Tái tạo tài liệu

Đây là công cụ authoring riêng, không thuộc runtime của ứng dụng hoặc CI. Trong Codex dùng Python/Node từ workspace dependency loader. Nếu chạy bên ngoài, tạo môi trường authoring riêng có `python-docx` và `Pillow`; cần LibreOffice, Poppler và FFmpeg để render/kiểm tra và encode. Không cần chúng để chạy Agri Leaf.

```powershell
# Dùng Python của môi trường authoring, thay đường dẫn tương ứng.
& $AuthoringPython scripts/phase7/build_report.py
& $AuthoringPython scripts/phase7/build_video.py --ffmpeg $FfmpegPath
# Fallback slide dùng Artifact Tool của runtime Codex.
& $BundledNode scripts/phase7/build_deck_fallback.mjs $RuntimeDependencies
```

Word phải chạy canonical `documents/render_docx.py --emit_pdf` và xem từng trang PNG trước khi thay PDF bàn giao. Slide dùng `build_slides.mjs` qua artifactSession cho bản Spaces; đường dự phòng dùng `build_deck_fallback.mjs`, sau đó finalizer theo skill Presentations và LibreOffice/Poppler để kiểm tra từng slide. Không commit `.tools/`, `.phase7-build/`, runtime hoặc dataset.

Kiểm tra file bàn giao offline bằng `python scripts/check_delivery.py`; chạy lại `scripts/phase7/record_delivery.py` bằng môi trường authoring khi cố ý cập nhật cả bộ. Script record dùng `pypdf` và `ffprobe` để ghi số trang/thời lượng; không tự sinh bằng chứng kiểm tra trực quan.

## Việc người nộp cần hoàn tất

Điền thông tin hành chính; đối chiếu rubric/mẫu của giảng viên; đọc hiểu và tập trình bày; tuân thủ quy định dùng AI. Nếu sửa số liệu, phải truy về artifact, sửa đồng bộ các đầu ra và kiểm tra lại. Phase 8 mới thực hiện clone sạch, rà soát link nộp và release v1.0.0.
