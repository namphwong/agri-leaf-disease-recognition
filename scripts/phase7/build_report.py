"""Build the editable academic report using the document-authoring Python runtime.

No model or experiment is executed. All numbers are read from versioned artifacts.
Render the result with the canonical documents/render_docx.py before delivery.
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "deliverables/phase7"
OUT.mkdir(parents=True, exist_ok=True)
E = json.loads((ROOT / "reports/evaluation/latest.json").read_text(encoding="utf-8"))
D = json.loads((ROOT / "reports/dataset/summary.json").read_text(encoding="utf-8"))
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin = sec.bottom_margin = Inches(.72)
sec.left_margin = sec.right_margin = Inches(.8)
for name in ["Normal", "Title", "Subtitle", "Heading 1", "Heading 2", "Caption"]:
    style = doc.styles[name]
    style.font.name = "Arial"
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.space_after = Pt(7)
    for border in list(style.element.iter(qn("w:pBdr"))):
        border.getparent().remove(border)
doc.styles["Normal"].font.size = Pt(11)
doc.styles["Normal"].paragraph_format.line_spacing = 1.15
doc.styles["Title"].font.size = Pt(27)
doc.styles["Title"].font.bold = True
doc.styles["Heading 1"].font.size = Pt(19)
doc.styles["Heading 2"].font.size = Pt(13)
doc.styles["Caption"].font.size = Pt(9)
header = sec.header.paragraphs[0]
header.text = "AGRI LEAF    •    HỌC PHẦN NHẬN DẠNG MẪU"
header.runs[0].font.size = Pt(8)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run("Agri Leaf  |  ")
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
footer._p.append(fld)


def p(text, style=None):
    return doc.add_paragraph(text, style)


def h(text):
    doc.add_heading(text, 1)


def sub(text):
    doc.add_heading(text, 2)


def page(title):
    doc.add_page_break()
    h(title)


def table(headers, rows, widths):
    t = doc.add_table(rows=1, cols=len(headers))
    t.autofit = False
    for col, width in zip(t.columns, widths):
        col.width = Inches(width)
    for i, value in enumerate(headers):
        t.rows[0].cells[i].text = str(value)
    for row in rows:
        for c, value in zip(t.add_row().cells, row):
            c.text = str(value)
    for ri, row in enumerate(t.rows):
        pr = row._tr.get_or_add_trPr()
        if ri == 0:
            pr.append(OxmlElement("w:tblHeader"))
        pr.append(OxmlElement("w:cantSplit"))
        for ci, cell in enumerate(row.cells):
            cell.width = Inches(widths[ci])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = cell._tc.get_or_add_tcPr()
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "333333" if ri == 0 else ("F2F4F5" if ri % 2 else "FFFFFF"))
            cp.append(shade)
            borders = OxmlElement("w:tcBorders")
            for edge in ["top", "left", "bottom", "right"]:
                el = OxmlElement("w:" + edge)
                for k, v in [("val", "single"), ("sz", "4"), ("color", "D9D9D9")]:
                    el.set(qn("w:" + k), v)
                borders.append(el)
            cp.append(borders)
            margins = OxmlElement("w:tcMar")
            for edge in ["top", "left", "bottom", "right"]:
                el = OxmlElement("w:" + edge)
                el.set(qn("w:w"), "85")
                el.set(qn("w:type"), "dxa")
                margins.append(el)
            cp.append(margins)
            for para in cell.paragraphs:
                para.paragraph_format.space_after = Pt(3)
                para.paragraph_format.space_before = Pt(3)
                para.paragraph_format.line_spacing = 1.05
                if ci > 0:
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in para.runs:
                    run.font.size = Pt(9.5)
                    if ri == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
    p("")
    return t


def image(path, width, caption):
    doc.add_picture(str(ROOT / path), width=Inches(width))
    p(caption, "Caption")


p("BÁO CÁO HỌC PHẦN", "Subtitle")
p("Nhận dạng bệnh trên lá khoai tây và cà chua", "Title")
p("Ứng dụng ResNet18 kế thừa và giao diện Streamlit", "Subtitle")
p("Học phần Nhận dạng mẫu\nDự án Agri Leaf\nPhiên bản báo cáo Phase 7 • ngày 22 tháng 11 năm 2026")
p("\nTrường: ______________________________________________\nKhoa và lớp: __________________________________________\nSinh viên: ____________________________________________\nMã sinh viên: _________________________________________\nGiảng viên hướng dẫn: _________________________________")
p("\nKho mã nguồn public\nhttps://github.com/namphwong/agri-leaf-disease-recognition")
p("Phạm vi thực hiện", "Heading 2")
p("Đề tài tái sử dụng checkpoint ResNet18 có sẵn, tổ chức lại pipeline, kiểm tra dữ liệu, xây dựng UI/UX tiếng Việt và kiểm chứng kết quả. Chưa tự huấn luyện hoặc so sánh mô hình mới. Các trường thông tin hành chính phía trên cần được người nộp điền trước khi nộp bài.")
p("Nguồn kế thừa được công khai tại mục 10 và tài liệu tham khảo. Yêu cầu mẫu báo cáo và tiêu chí riêng của giảng viên chưa được cung cấp; bố cục này là bản học phần thông dụng.")

page("Tóm tắt và nội dung báo cáo")
p("Agri Leaf nhận ảnh JPEG/PNG của một lá khoai tây hoặc cà chua và phân loại vào sáu nhãn. Sản phẩm gồm nhận dạng, top 3 dự đoán, lịch sử SQLite, xuất CSV và trang đánh giá. Luồng suy luận chạy CPU trên máy, không gửi ảnh đến dịch vụ AI bên ngoài.")
p("Kiểm chứng checkpoint kế thừa trên partition test mới gồm 776 ảnh cho 716 dự đoán đúng và 60 dự đoán sai; accuracy 92,27%, macro F1 91,85%. Median của giải mã, tiền xử lý và dự đoán là 33,59 ms/ảnh trong môi trường đã ghi nhận. Vì không biết các ảnh từng được dùng huấn luyện checkpoint, kết quả này chỉ mô tả hành vi trên tập đã chọn, chưa đo khả năng tổng quát độc lập.")
p("Đóng góp chính là khả năng truy vết và sử dụng mô hình: ghim nguồn/checksum, phân chia dữ liệu theo nhóm lá, tách code thành module, thiết kế giao diện bốn trang, lưu lịch sử có chủ đích, kiểm thử và CI. Báo cáo không nhận kiến trúc ResNet hoặc checkpoint là đóng góp thuật toán mới.")
table(["Phần", "Nội dung", "Trang"], [
    ("1", "Bài toán và mục tiêu", 3), ("2", "Cơ sở nhận dạng và mô hình", 4),
    ("3", "Nguồn và kiểm tra dữ liệu", 5), ("4", "Thiết kế thực nghiệm", 6),
    ("5", "Kiến trúc và luồng sử dụng", 7), ("6", "Giao diện và lịch sử", 8),
    ("7", "Kết quả định lượng", 9), ("8", "Phân tích sai và độ trễ", 10),
    ("9 và 10", "Kiểm thử và đóng góp", 11), ("11", "Giới hạn và tài liệu tham khảo", 12),
], [.7, 5.3, .9])
p("Quy ước: EB là Early blight; LB là Late blight; H là healthy. Giữ thuật ngữ bệnh tiếng Anh để tránh gán sai tên bệnh tiếng Việt. Số liệu làm tròn hai chữ số sau dấu phẩy; dữ liệu gốc và dấu vết thực nghiệm nằm trong reports/evaluation/latest.json.")

page("1 Bài toán và mục tiêu")
p("Bài toán nhận dạng là phân loại ảnh đa lớp có giám sát. Ảnh đầu vào x được ánh xạ tới nhãn y trong tập sáu lớp, gồm tích của hai loại cây và ba trạng thái lá. Mỗi ảnh chỉ có một nhãn mục tiêu; hệ thống không xác định vị trí tổn thương hay mức độ bệnh.")
table(["Chỉ số lớp", "Nhãn checkpoint", "Hiển thị"], [
    (0, "Potato___Early_blight", "Khoai tây EB"), (1, "Potato___Late_blight", "Khoai tây LB"),
    (2, "Potato___healthy", "Khoai tây khỏe"), (3, "Tomato___Early_blight", "Cà chua EB"),
    (4, "Tomato___Late_blight", "Cà chua LB"), (5, "Tomato___healthy", "Cà chua khỏe"),
], [.8, 3.6, 2.5])
sub("Mục tiêu sử dụng")
p("Người dùng chính là sinh viên, giảng viên và người xem demo. Một phiên nhận dạng cần thể hiện rõ các bước chọn ảnh, xem trước, phân tích, đọc kết quả và tùy chọn lưu. Giao diện phải giải thích điểm mô hình và thông báo lỗi bằng tiếng Việt, đồng thời cho phép xem lịch sử và bằng chứng thực nghiệm.")
sub("Điều kiện hoàn thành")
p("Ứng dụng hỗ trợ JPEG/PNG tối đa 20 MiB và 16 triệu pixel; từ chối nội dung không hợp lệ; giữ nguyên thứ tự lớp và tiền xử lý của checkpoint. Kết quả gồm nhãn, điểm softmax và top 3. Người dùng tự quyết định lưu, lọc, xuất CSV hoặc xóa lịch sử. Trang đánh giá phải hiển thị nguồn số liệu và cảnh báo giới hạn.")
p("Đề tài hiện tại là tích hợp và kiểm chứng hệ thống kế thừa. Nếu học phần yêu cầu huấn luyện lại hoặc so sánh thuật toán, cần bổ sung thực nghiệm theo cùng manifest, dùng validation cho lựa chọn mô hình và dành dữ liệu chưa bị checkpoint nhìn thấy cho đánh giá cuối.")

page("2 Cơ sở nhận dạng và mô hình")
p("Trong nhận dạng ảnh, mạng tích chập học các bộ lọc để biến đổi ảnh thành biểu diễn đặc trưng. Các tầng đầu có thể phản ứng với biên và kết cấu; biểu diễn sâu được dùng cho quyết định phân lớp. Với hệ thống này, đặc trưng được tính bởi mạng đã có trọng số, thay vì tự thiết kế một bộ đặc trưng thủ công mới.")
p("ResNet sử dụng kết nối tắt trong khối dư: y = F(x) + x khi kích thước phù hợp; nhánh chiếu có thể được dùng khi số kênh hoặc kích thước thay đổi. Cách xây dựng này hỗ trợ tối ưu mạng sâu [1]. Dự án dùng biến thể ResNet18 với tầng đầu ra sáu lớp được khôi phục từ checkpoint của smart-leaf-ai [3]. Báo cáo không suy luận lại quy trình tối ưu gốc từ riêng file trọng số.")
sub("Pipeline được giữ nguyên")
p("Bytes ảnh → xác minh định dạng và giới hạn → chuyển RGB → resize 224 × 224 → ToTensor → thêm chiều batch → ResNet18 ở eval mode → softmax → nhãn và top 3. Tensor sau ToTensor có miền giá trị 0–1. Không bổ sung Normalize theo ImageNet và không xoay ảnh theo EXIF, vì thay các bước này sẽ làm khác pipeline đã kiểm chứng.")
sub("Điểm phân lớp")
p("Với logits z, điểm của lớp i là exp(zᵢ) / Σⱼ exp(zⱼ). Nhãn dự đoán là lớp có điểm lớn nhất; top 3 trình bày ba điểm cao nhất. Softmax chỉ chuẩn hóa các điểm trong sáu lớp: tổng bằng 1 không có nghĩa ảnh thuộc phạm vi hoặc dự đoán đúng. Đề tài chưa hiệu chuẩn điểm và chưa kiểm chứng ngưỡng từ chối ảnh lạ.")
sub("Các chỉ số đánh giá")
p("Accuracy = số dự đoán đúng / tổng ảnh. Với mỗi lớp, precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2PR/(P+R). Macro F1 là trung bình F1 của đủ sáu lớp; weighted F1 dùng trọng số theo số ảnh mỗi lớp. Khi mẫu số bằng 0, quy ước giá trị 0 được ghi rõ trong artifact.")
p("Công thức chỉ số là định nghĩa đo lường; chúng không giải quyết thiên lệch dữ liệu hay ảnh trùng huấn luyện. Vì vậy, mọi kết luận phải kèm nguồn checkpoint và phạm vi tập ảnh.")

page("3 Nguồn và kiểm tra dữ liệu")
p("Dữ liệu đến từ PlantVillage public [2, 4]. Dự án ghim snapshot GitHub 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a và chọn sáu thư mục raw/color tương ứng sáu lớp. Dataset card [5] công bố CC BY-SA 3.0; giấy phép dữ liệu tách biệt với MIT của mã nguồn. Ảnh gốc và Git cache không được commit vào repository dự án.")
table(["Lớp", "Ảnh gốc", "Cách ly", "Train", "Val", "Test"], [
    (r["label"].replace("Potato___", "P ").replace("Tomato___", "T ").replace("Early_blight", "EB").replace("Late_blight", "LB").replace("healthy", "H"), r["images"], r["quarantine"], r["train"], r["validation"], r["test"]) for r in D["per_class"]
] + [("Tổng", 6652, 1582, 3546, 748, 776)], [1.4, 1.1, 1.1, 1.1, 1.1, 1.1])
p("Audit ghi nhận cả 6.652 ảnh đều RGB, 256 × 256 và giải mã được. Có 14 nhóm trùng byte và RGB, mỗi nhóm là một cặp; chúng đều nằm trong phần cách ly. Có 1.582 ảnh không ánh xạ được tới metadata nhóm lá nên chưa đủ điều kiện dùng cho split. Không xem cách ly là loại bỏ vĩnh viễn: giữ nguồn và lý do để xử lý lại khi có metadata đáng tin cậy.")
p("5.070 ảnh đủ điều kiện thuộc 1.268 thành phần nhóm được phân chia theo từng lớp với seed 42. Các liên kết cùng leaf ID hoặc trùng ảnh nằm trong cùng thành phần; thành phần không được tách qua train, validation và test. Tỷ lệ mục tiêu 70/15/phần còn lại tính theo số nhóm nên tỷ lệ số ảnh có thể chênh nhẹ.")
p("Potato healthy chỉ có 152 ảnh gốc và 28 ảnh test. Sự mất cân bằng làm accuracy tổng bị chi phối bởi lớp lớn; báo cáo thêm macro F1 và support từng lớp. Tính độc lập vật lý vẫn phụ thuộc chất lượng leaf metadata; audit chưa loại trừ hết các ảnh gần trùng.")

page("4 Thiết kế thực nghiệm")
sub("Câu hỏi và đối tượng kiểm chứng")
p("Câu hỏi thực nghiệm là checkpoint kế thừa hoạt động thế nào khi chạy qua API suy luận của dự án trên partition test mới. Đối tượng đo là trọng số có sẵn, không phải một mô hình được huấn luyện bằng split mới. Notebook gốc được giữ để ghi nhận nguồn; Phase 2–7 không thực hiện huấn luyện, dò tham số hoặc chọn checkpoint theo test.")
table(["Yếu tố", "Cấu hình"], [
    ("Checkpoint", "ResNet18 kế thừa; model_version resnet18-b20634ad7be7"),
    ("Tập đo", "776 ảnh test, 194 nhóm lá; bỏ phần cách ly"),
    ("Runtime", "Python 3.11.9; torch 2.8.0+cpu; torchvision 0.23.0+cpu"),
    ("Thiết bị và luồng", "CPU; torch_threads = 8; suy luận tuần tự từng ảnh"),
    ("Đo thời gian", "3 lần warm-up; không tính đọc file và checksum"),
    ("Bootstrap", "1.000 lần lấy mẫu lại theo group_id; seed 42"),
], [1.65, 5.25])
p("SHA-256 của checkpoint và manifest được ghi đầy đủ trong latest.json; file predictions.csv lưu từng nhãn thật, nhãn dự đoán, điểm và thời gian. Các hình được xuất từ cùng lần chạy ngày 13/11/2026. Báo cáo lập ngày 22/11/2026 sử dụng lại bằng chứng này, không công bố là một lần huấn luyện hay đo mới.")
sub("Nguy cơ giao nhau với huấn luyện")
p("Không có danh sách thành viên train gốc của checkpoint. Chia nhóm lá bây giờ chỉ ngăn rò rỉ giữa các partition mới; không thể làm checkpoint quên những ảnh từng thấy. Do đó 92,27% không phải accuracy trên test độc lập. Cũng không so sánh trực tiếp với 93,69% mà tác giả gốc công bố, vì chưa chứng minh cùng tập và cùng giao thức.")
p("Bootstrap theo nhóm phản ánh biến thiên trong tập ảnh đang có. Khoảng 95% của accuracy là 89,82–94,46%, của macro F1 là 89,04–94,25%. Chúng có điều kiện trên dữ liệu đã chọn và checkpoint cố định, không khắc phục được giao nhau train hoặc dịch chuyển miền ngoài đồng.")

page("5 Kiến trúc và luồng sử dụng")
p("Ứng dụng dùng Streamlit cho lớp trình bày, các module Python cho xử lý và SQLite cho lịch sử cục bộ. Luồng chính là app.py → src/ui → validation → preprocessing và inference → kết quả có cấu trúc → hiển thị; storage chỉ được gọi khi người dùng lưu hoặc quản lý lịch sử.")
table(["Thành phần", "Trách nhiệm"], [
    ("src/validation.py", "Xác minh bytes, JPEG/PNG, dung lượng, pixel; giải mã RGB"),
    ("src/preprocessing.py", "Giữ đúng resize, ToTensor và batch dimension"),
    ("src/inference.py", "Load CPU, kiểm tra checksum, eval, softmax và top 3"),
    ("src/labels.py", "Thứ tự nhãn và nội dung hiển thị tiếng Việt"),
    ("src/storage.py", "Record có phiên bản, SQLite, thumbnail, lọc và xuất CSV"),
    ("src/ui/ và app.py", "Bốn trang và trạng thái tương tác; cache tài nguyên"),
], [2, 4.9])
p("PredictionResult có index, label, confidence, top3, sáu probabilities, thiết bị, model_version và checkpoint_sha256. Điểm nằm trong miền 0–1; UI nhân 100 để trình bày. Nhờ hợp đồng này, phần giao diện không cần tự suy luận thứ tự lớp hoặc gọi trực tiếp tensor của mô hình.")
p("Mô hình được tải theo CPU với weights_only=True, strict=True và đưa về eval mode. Cache dựa trên đường dẫn, mtime và dung lượng; khi thay checkpoint cần xóa cache hoặc khởi động lại nếu cố ý giữ nguyên metadata. Ảnh upload chỉ được giải mã trong bộ nhớ; thao tác xem kết quả không tự lưu ảnh gốc vào đĩa.")
sub("Khả năng tái lập")
p("README hướng dẫn tạo môi trường Python 3.11.9 và cài requirements-lock.txt. Script baseline_check đối chiếu sáu ảnh ghim checksum; prepare_dataset khôi phục sáu lớp; evaluate tạo metrics; check_evaluation kiểm tra tính nhất quán. CI chỉ kiểm thử offline, không tải cả bộ ảnh và không huấn luyện mỗi commit.")

page("6 Giao diện và lịch sử")
image("docs/screenshots/phase5-desktop.jpg", 6.85, "Hình 1. Giao diện nhận dạng tiếng Việt của dự án ở Phase 5. Ảnh lá mẫu thuộc train PlantVillage, theo manifest; quyền ảnh theo [4, 5]. Điểm trên một ảnh minh họa không phải accuracy tổng.")
p("Trang Nhận dạng tách chọn ảnh và kết quả, hiển thị xem trước trước khi phân tích. Người dùng có thể chọn ảnh máy hoặc sáu mẫu đã ghim nguồn và SHA-256 từ train. Mẫu cục bộ được ưu tiên; nếu thiếu, ứng dụng chỉ tải ảnh mẫu được chọn từ nguồn public. Các mẫu này phục vụ thao tác demo, không được dùng để khẳng định chất lượng test.")
p("Trang Lịch sử hiển thị bản ghi đã lưu theo yêu cầu. Cơ sở dữ liệu SQLite chứa nhãn, thời gian, điểm, phiên bản mô hình và thumbnail JPEG tối đa 320 × 240, không chứa ảnh upload gốc. Có lọc theo tên Unicode, cây, nhãn, khoảng ngày; phân trang 10 bản ghi. CSV UTF-8 BOM xuất toàn bộ tập đang lọc. Xóa cần bước xác nhận và có tác động tới dữ liệu cục bộ.")
p("Trang Đánh giá đọc artifact Phase 6, hiển thị accuracy, macro F1, confusion matrix và cảnh báo. Trang Hướng dẫn giải thích phạm vi, cách đọc điểm và nguồn. UI không tự diễn giải softmax thành chẩn đoán canh tác; trạng thái rỗng, đang xử lý và lỗi được trình bày bằng ngôn ngữ người dùng.")

page("7 Kết quả định lượng")
table(["Chỉ số", "Kết quả"], [
    ("Ảnh khớp nhãn / tổng", "716 / 776"), ("Accuracy", "92,27%"),
    ("Macro precision", "93,29%"), ("Macro recall", "90,76%"),
    ("Macro F1", "91,85%"), ("Weighted F1", "92,24%"),
], [4.6, 2.3])
rows = []
for r in E["metrics"]["per_class"]:
    label = r["label"].replace("Potato___", "Khoai ").replace("Tomato___", "Cà chua ").replace("Early_blight", "EB").replace("Late_blight", "LB").replace("healthy", "H")
    rows.append([label] + [f"{r[k] * 100:.2f}".replace(".", ",") for k in ["precision", "recall", "f1"]] + [r["support"]])
table(["Lớp", "P %", "R %", "F1 %", "Support"], rows, [2.1, 1.2, 1.2, 1.2, 1.2])
p("Potato EB có F1 cao nhất trong tập đo, 99,02%. Tomato LB có F1 thấp nhất, 83,94%, với recall 82,14%. Khoảng cách giữa các lớp cho thấy cần đọc các chỉ số theo lớp; một accuracy chung không mô tả đủ các lỗi mà người dùng có thể gặp.")
p("Potato healthy đạt precision 100% trên 23 dự đoán lớp này, nhưng recall chỉ 82,14% vì 5/28 ảnh bị xếp sang Potato LB. Mẫu nhỏ, chỉ bảy nhóm lá, nên không suy ra lớp khỏe đã được nhận dạng hoàn hảo. Việc trình bày đồng thời precision, recall và support giúp tránh kết luận từ một con số riêng lẻ.")
p("Các số liệu trên mô tả checkpoint kế thừa trên partition mới. Không có test độc lập và chưa có bằng chứng ngoài đồng; kết luận này áp dụng cho toàn bộ bảng, không chỉ một lớp cụ thể.")

page("8 Phân tích sai và độ trễ")
image("reports/evaluation/confusion_matrix.png", 4.9, "Hình 2. Ma trận nhầm lẫn từ 776 dự đoán. Hàng là nhãn thật, cột là nhãn dự đoán; thứ tự sáu lớp đúng như mục 1. Nguồn: artifact Phase 6.")
p("Lỗi nổi bật nằm giữa hai nhóm bệnh cà chua: 16 ảnh Tomato LB bị dự đoán Tomato EB và 11 ảnh Tomato EB bị dự đoán Tomato LB. Có thêm 9 ảnh Tomato LB bị xếp Potato LB. Ma trận xác định các cặp cần kiểm tra; chưa đủ bằng chứng để quy nguyên nhân cho vùng tổn thương, ánh sáng hoặc nền mà không có phân tích bổ sung.")
p("Median giải mã + tiền xử lý + dự đoán là 33,59 ms, p95 là 42,70 ms; median riêng predict là 32,70 ms. Tổng vòng đo 776 ảnh là 28,81 giây. Giao thức dùng CPU tuần tự, ba lần warm-up, tám luồng torch; không tính đọc file và checksum. Đây không phải thời gian đáp ứng end-to-end của trình duyệt hoặc một cam kết trên mọi máy.")
p("reports/evaluation/examples.png và examples.json giữ 12 trường hợp đúng/sai có nguồn ảnh để kiểm tra trực quan. Việc chọn ví dụ chỉ minh họa lỗi; các chỉ số định lượng được tính trên toàn bộ 776 ảnh, không trên tập ảnh minh họa.")

page("9 Kiểm thử và quản lý dự án")
p("Bộ kiểm thử hiện có 39 test cho dữ liệu, validation, thứ tự lớp, suy luận hồi quy, metrics, SQLite và Streamlit. CI GitHub Actions trên Windows/Python 3.11.9 kiểm tra dependencies, cú pháp, test offline và tính nhất quán artifact. Đạt test không chứng minh độ chính xác ngoài đồng; đây là bằng chứng các hợp đồng chức năng và dữ liệu quan trọng hoạt động theo yêu cầu.")
p("Repository giữ lịch sử fork, origin và upstream, issues theo phase, nhánh chức năng và pull request. Các thay đổi Phase 0–6 đã được tích hợp qua PR #11–16. Phase 7 bổ sung gói trình bày và bằng chứng kiểm tra tài liệu. Phase 8 sẽ kiểm tra clone sạch và phát hành; chưa nhận công việc Phase 8 là đã hoàn thành.")
h("10 Nguồn kế thừa và đóng góp")
table(["Hạng mục", "Kế thừa", "Thực hiện trong dự án"], [
    ("Mô hình", "ResNet18; checkpoint và notebook smart-leaf-ai", "Tải CPU, checksum, API suy luận; không train mới"),
    ("Dữ liệu", "Ảnh và leaf metadata PlantVillage", "Audit, cách ly, split theo nhóm, manifest và SHA"),
    ("Ứng dụng", "Ý tưởng phân loại ảnh và pipeline gốc", "Tách module; UI/UX Việt bốn trang; SQLite/CSV"),
    ("Kiểm chứng", "93,69% do tác giả gốc công bố", "Sáu ảnh smoke check; 776 dự đoán có giới hạn"),
    ("Bàn giao", "MIT nguồn; CC BY-SA dữ liệu theo card", "GitHub, tests/CI, báo cáo, slide, kịch bản, video"),
], [1.1, 2.75, 3.05])
p("Các phần triển khai được tạo với hỗ trợ của Codex theo yêu cầu chủ dự án. Người nộp cần đọc hiểu code, kiểm chứng các phát biểu, tuân thủ quy định công cụ AI của học phần và tự chịu trách nhiệm về nội dung. Báo cáo không tự gán kinh nghiệm huấn luyện hoặc đóng góp thuật toán mà dự án chưa thực hiện.")
p("Bằng chứng của các đóng góp có thể xem tại src/, scripts/, tests/, reports/ và lịch sử PR. Giấy phép MIT của mã nguồn không thay thế giấy phép ảnh; các hình có lá PlantVillage trong báo cáo và video vẫn phải giữ nguồn và điều kiện dữ liệu.")

page("11 Giới hạn và hướng phát triển")
p("Hệ thống đã hoàn thiện luồng ứng dụng học tập và có kết quả kiểm chứng truy vết được. Giới hạn lớn nhất là thành viên train gốc không rõ. Tiếp theo là dữ liệu nền đơn giản, mất cân bằng, 1.582 ảnh cách ly, lớp Potato healthy nhỏ và chưa loại hết ảnh gần trùng. Mô hình luôn chọn một trong sáu lớp; chưa đánh giá ảnh cây khác, nhiều lá hoặc ảnh ngoài đồng.")
p("Hướng tiếp theo là thu thập tập ngoài đồng có nhãn đáng tin cậy và tách theo cây/địa điểm/thời gian; huấn luyện lại trên train, chọn mô hình bằng validation, rồi đánh giá một lần trên test giữ kín. Có thể bổ sung mô hình đặc trưng truyền thống và một CNN khác với cùng split, tài nguyên và chỉ số; hiệu chuẩn điểm và kiểm chứng cơ chế từ chối cần tập ngoài phạm vi riêng. Đây là đề xuất, chưa phải kết quả đã làm.")
sub("Tài liệu tham khảo")
refs = [
    "[1] He, K., Zhang, X., Ren, S., Sun, J. (2016). Deep Residual Learning for Image Recognition. CVPR. https://arxiv.org/abs/1512.03385",
    "[2] Mohanty, S. P., Hughes, D. P., Salathé, M. (2016). Using Deep Learning for Image-Based Plant Disease Detection. Frontiers in Plant Science, 7, 1419. https://doi.org/10.3389/fpls.2016.01419",
    "[3] spneoarm. smart-leaf-ai. Mã nguồn, checkpoint và notebook kế thừa; MIT. https://github.com/spneoarm/smart-leaf-ai",
    "[4] spMohanty. PlantVillage-Dataset. Snapshot 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a. https://github.com/spMohanty/PlantVillage-Dataset",
    "[5] mohanty/PlantVillage. Dataset card, công bố CC BY-SA 3.0. https://huggingface.co/datasets/mohanty/PlantVillage",
    "[6] namphwong. Agri Leaf. reports/evaluation/latest.json, predictions.csv; docs/dataset.md; requirements-lock.txt. https://github.com/namphwong/agri-leaf-disease-recognition",
]
for ref in refs:
    para = p(ref)
    para.paragraph_format.space_after = Pt(6)
    for run in para.runs:
        run.font.size = Pt(9)
p("Nguồn web được đối chiếu ngày 22/11/2026. Các số liệu dự án lấy từ artifact đã commit; số đo gốc ngày 13/11/2026. Hướng dẫn chạy, lệnh tái lập và bảng checksum đầy đủ nằm trong repository [6].", "Caption")

doc.core_properties.title = "Nhận dạng bệnh trên lá khoai tây và cà chua"
doc.core_properties.subject = "Báo cáo học phần Nhận dạng mẫu — Phase 7"
doc.core_properties.author = "namphwong"
doc.core_properties.keywords = "PlantVillage, ResNet18, Streamlit, inherited checkpoint"
target = OUT / "bao-cao-agri-leaf.docx"
doc.save(target)
print(target)
