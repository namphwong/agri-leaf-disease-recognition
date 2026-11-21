// Reusable callback for the existing Spaces deck; no standalone PPTX builder.
// Run batches through artifactSession.run(buildSlides, {artifactRef, input:{from,to}}).
export async function buildSlides({presentation, input}) {
  const ink='#18362E', green='#276B50', gray='#52635B';
  function txt(s,text,x,y,w,h,size=27,color=ink,bold=false) {
    const t=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
    t.text=text; t.text.style={fontFamily:'Arial',fontSize:size,color,bold}; return t;
  }
  function base(n,title,source) {
    const s=presentation.slides.add({width:1280,height:720});s.background.fill='#F8FAF7';
    txt(s,'AGRI LEAF  /  NHẬN DẠNG MẪU',64,28,1120,35,17,green,true);
    txt(s,title,64,86,1150,100,39,ink,true);
    txt(s,source,64,654,1080,42,15,gray);txt(s,String(n).padStart(2,'0')+' / 12',1130,654,95,35,16,gray);
    return s;
  }
  function lines(s,arr,x=70,y=218,w=1110,size=28,gap=88) {
    arr.forEach((a,i)=>txt(s,a,x,y+i*gap,w,gap-10,size));
  }
  function table(s,headers,rows,x,y,w,h,widths) {
    const vals=[headers,...rows];
    const t=s.tables.add({rows:vals.length,columns:headers.length,left:x,top:y,width:w,height:h,columnWidths:widths,values:vals});
    t.borders.assign({fill:'#D5DFD8',width:1,style:'solid'});
    for(let r=0;r<vals.length;r++)for(let c=0;c<headers.length;c++){
      const cell=t.getCell(r,c);cell.fill=r===0?green:(r%2?'#EDF2ED':'#FFFFFF');
      cell.text.style={fontFamily:'Arial',fontSize:22,color:r===0?'#FFFFFF':ink,bold:r===0};
    }return t;
  }
  for(let n=input.from;n<=input.to;n++){
    let s;
    if(n===2){
      s=base(n,'Một ảnh lá vào, một trong sáu nhãn ra','Nguồn: docs/project-scope.md; checkpoint kế thừa từ smart-leaf-ai.');
      txt(s,'2 cây × 3 trạng thái',70,205,1090,75,48,green,true);
      lines(s,['Khoai tây và cà chua','Early blight · Late blight · Lá khỏe','Đầu ra: nhãn, điểm softmax và top 3'],70,310,1100,30,80);
      txt(s,'Phạm vi học tập; chưa có cơ chế từ chối ảnh ngoài sáu lớp được kiểm chứng.',70,584,1100,52,22,gray);
      s.speakerNotes.text='Giới thiệu bài toán phân loại đa lớp. Chỉ nhận dạng một ảnh lá trong sáu nhãn. Không phân đoạn, không đo mức độ bệnh, không tư vấn thuốc. Nêu ngay đề tài tái sử dụng checkpoint.';
    }
    if(n===3){
      s=base(n,'Giữ đúng pipeline của checkpoint','Nguồn: src/validation.py; src/preprocessing.py; src/inference.py; He et al., CVPR 2016.');
      lines(s,['01   JPEG/PNG → kiểm tra nội dung và giới hạn','02   RGB → resize 224 × 224 → ToTensor','03   ResNet18 CPU, eval → softmax → top 3'],70,215,1110,30,102);
      txt(s,'Không thêm Normalize hoặc xoay EXIF vào pipeline đã kiểm chứng.',70,545,1100,62,26,green,true);
      s.speakerNotes.text='Giải thích CNN tạo đặc trưng từ ảnh. Khối dư ResNet có phép cộng nhánh tắt giúp tối ưu mạng sâu; nguồn He et al. https://arxiv.org/abs/1512.03385. Dùng kiến trúc và trọng số kế thừa, không nhận đã tự train. Không đổi preprocessing khi chỉ sửa UI.';
    }
    if(n===4){
      s=base(n,'Dữ liệu public có phiên bản và lý do cách ly','Nguồn: PlantVillage snapshot 7f7ecc7e1eac; reports/dataset/summary.json; CC BY-SA 3.0 theo dataset card.');
      table(s,['Audit','Số ảnh'],[['Sáu lớp được tải','6.652'],['Thiếu mapping nhóm lá, cách ly','1.582'],['Đủ điều kiện chia tập','5.070'],['Ảnh lỗi giải mã','0']],70,205,650,340,[475,175]);
      txt(s,'14 cặp ảnh trùng\nđều trong phần cách ly',785,260,410,130,31,green,true);
      txt(s,'Ảnh RGB 256 × 256\nKhông commit ảnh gốc',785,435,410,100,26);
      s.speakerNotes.text='Nguồn public https://github.com/spMohanty/PlantVillage-Dataset và card https://huggingface.co/datasets/mohanty/PlantVillage. Giữ riêng ảnh thiếu nhóm lá để tránh chia sai. Không đánh đồng giấy phép MIT của code với giấy phép ảnh.';
    }
    if(n===5){
      s=base(n,'Chia theo nhóm lá, chưa có test độc lập','Nguồn: reports/dataset/summary.json; reports/evaluation/latest.json; seed 42.');
      table(s,['Partition mới','Ảnh'],[['Train','3.546'],['Validation','748'],['Test','776']],70,210,590,278,[390,200]);
      txt(s,'Cùng leaf ID hoặc ảnh trùng\nở cùng thành phần nhóm.',735,218,450,135,30,green,true);
      txt(s,'Không biết thành viên train gốc.\nChia tập mới không xóa được\nkiến thức checkpoint đã học.',735,395,460,172,28);
      txt(s,'Không train lại · Không dò tham số trên test · Không công bố tổng quát ngoài đồng',70,574,1110,55,23,gray);
      s.speakerNotes.text='1.268 thành phần nhóm đủ điều kiện. Chia mục tiêu 70/15/phần còn lại theo nhóm từng lớp, nên tỷ lệ ảnh xấp xỉ. Nhấn mạnh partition test mới không đồng nghĩa test độc lập của mô hình cũ. Đây là điểm quan trọng nhất khi diễn giải kết quả.';
    }
    if(n===6){
      s=base(n,'Tách mô hình khỏi giao diện và lịch sử','Nguồn: src/; docs/architecture.md; docs/history.md.');
      lines(s,['Streamlit: nhận dạng · lịch sử · đánh giá · hướng dẫn','Core: validation → preprocessing → inference','Storage: SQLite, thumbnail, lọc và CSV'],70,215,1110,30,103);
      txt(s,'PredictionResult có nhãn, sáu điểm, top 3 và phiên bản theo SHA-256.',70,550,1100,74,26,green,true);
      s.speakerNotes.text='Trình bày sự phân lớp trách nhiệm. Inference không phụ thuộc Streamlit hoặc SQLite. Mô hình cache ở UI, tải CPU weights_only và strict. Dữ liệu người dùng không gửi đến dịch vụ AI bên ngoài.';
    }
    if(n===7){
      s=base(n,'UI tiếng Việt cho một luồng nhận dạng rõ ràng','Nguồn: docs/screenshots/phase5-desktop.jpg; ảnh lá train PlantVillage, CC BY-SA 3.0 theo card.');
      const fs=await import('node:fs/promises');
      s.images.add({blob:new Uint8Array(await fs.readFile((input.root??'D:/TLU/NDM')+'/docs/screenshots/phase5-desktop.jpg')),contentType:'image/jpeg',alt:'Giao diện nhận dạng Agri Leaf Phase 5',fit:'contain',position:{left:60,top:185,width:850,height:435}});
      txt(s,'Chọn ảnh\n\nXem trước\n\nPhân tích\n\nĐọc và lưu',940,220,290,365,28,green,true);
      s.speakerNotes.text='Ảnh chụp ứng dụng thật từ Phase 5, điểm trên một ảnh không phải accuracy. Demo bằng ảnh mẫu train đã ghim checksum. Không nhấn lưu trước khi người dùng chủ động chọn. Giao diện có trạng thái rỗng, lỗi và đang xử lý.';
    }
    if(n===8){
      s=base(n,'Lưu có chủ đích và truy vết được mô hình','Nguồn: src/storage.py; docs/history.md; ảnh gốc không được lưu trong lịch sử.');
      lines(s,['Chỉ lưu khi bấm Lưu kết quả','SQLite: metadata + thumbnail JPEG tối đa 320 × 240','Lọc tên, cây, nhãn, ngày · phân trang 10 bản ghi','CSV UTF-8 BOM xuất toàn bộ kết quả đang lọc'],70,210,1110,29,87);
      txt(s,'Xóa cần xác nhận. Mỗi kết quả có model_version và checkpoint SHA-256.',70,578,1100,52,24,green,true);
      s.speakerNotes.text='Giải thích vì sao cần lưu model version: kết quả phải truy ngược được checkpoint. Thumbnail là ảnh thu nhỏ, không phải bản gốc. Tất cả dữ liệu lịch sử ở máy chạy ứng dụng. CSV xuất toàn bộ tập lọc chứ không chỉ trang hiện tại.';
    }
    if(n===9){
      s=base(n,'776 ảnh: accuracy 92,27% và macro F1 91,85%','Nguồn: reports/evaluation/latest.json; lần chạy 13/11/2026; checkpoint kế thừa.');
      table(s,['Chỉ số','Kết quả'],[['Khớp nhãn','716 / 776'],['Macro precision','93,29%'],['Macro recall','90,76%'],['Weighted F1','92,24%']],70,205,690,315,[450,240]);
      txt(s,'194 nhóm lá\n60 ảnh dự đoán sai',820,245,370,130,36,green,true);
      txt(s,'Có thể trùng train gốc. Các chỉ số mô tả tập đo, chưa ước lượng tổng quát độc lập.',70,565,1110,66,27,gray);
      s.speakerNotes.text='Accuracy là 716/776. Macro F1 coi sáu lớp như nhau, cần thiết vì lệch lớp. Không so sánh trực tiếp với 93,69% tác giả gốc vì chưa cùng tập/giao thức. Bootstrap theo nhóm 1.000 lần: accuracy 89,82–94,46%; khoảng có điều kiện trên dữ liệu này.';
    }
    if(n===10){
      s=base(n,'Lỗi tập trung giữa hai bệnh cà chua','Nguồn: confusion_matrix và timing trong reports/evaluation/latest.json.');
      table(s,['Lớp thật → dự đoán','Ảnh sai'],[['Tomato LB → Tomato EB','16'],['Tomato EB → Tomato LB','11'],['Tomato LB → Potato LB','9'],['Potato healthy → Potato LB','5']],70,215,780,320,[590,190]);
      txt(s,'33,59 ms',910,240,310,80,48,green,true);txt(s,'median decode +\npreprocess + predict\nCPU, 8 luồng',913,337,300,145,24);
      txt(s,'p95 42,70 ms · Không tính đọc file/checksum · Chưa phải độ trễ trình duyệt',70,574,1120,55,24,gray);
      s.speakerNotes.text='EB là Early blight, LB là Late blight. Tomato LB F1 83,94%, thấp nhất. Potato healthy chỉ 28 ảnh/7 nhóm lá: precision 100% không có nghĩa hoàn hảo vì recall 82,14%. Không quy nguyên nhân sai từ ma trận mà chưa phân tích ảnh bổ sung.';
    }
    if(n===11){
      s=base(n,'Đóng góp nằm ở tích hợp và kiểm chứng','Nguồn: ACKNOWLEDGEMENTS.md; PR #11–16; tests/; .github/workflows/ci.yml.');
      table(s,['Kế thừa','Đã triển khai'],[['ResNet18; checkpoint; notebook','API, checksum, validation và hồi quy'],['PlantVillage và leaf metadata','Audit, cách ly, manifest và split nhóm'],['Pipeline và ý tưởng ứng dụng','UI/UX Việt, SQLite, CSV, 39 test và CI']],70,215,1130,300,[500,630]);
      txt(s,'Chưa huấn luyện hoặc so sánh mô hình mới. Mã và tài liệu có hỗ trợ Codex.',70,566,1110,62,26,green,true);
      s.speakerNotes.text='Nêu nguồn upstream smart-leaf-ai MIT và dữ liệu CC BY-SA theo card. Không nhận ResNet/checkpoint là tự tạo. Codex hỗ trợ triển khai; người nộp cần hiểu và chịu trách nhiệm theo quy định học phần. 39 test là chức năng và tính nhất quán, không phải bằng chứng accuracy ngoài đồng.';
    }
    if(n===12){
      s=base(n,'Demo ứng dụng và hướng phát triển','Repository: github.com/namphwong/agri-leaf-disease-recognition  |  Tài liệu Phase 7 trong docs/phase7/.');
      lines(s,['Demo 4 phút: chọn mẫu → phân tích → lưu → CSV → đánh giá','Giới hạn: train gốc chưa rõ, nền đơn giản, lớp ít mẫu','Tiếp theo: tập ngoài đồng độc lập, train lại và so sánh'],70,215,1110,29,108);
      txt(s,'Ứng dụng đã có luồng hoàn chỉnh và bằng chứng có thể truy vết.',70,560,1110,74,30,green,true);
      s.speakerNotes.text='Chuyển sang ứng dụng với kịch bản docs/phase7/defense-guide.md. Có video 4 phút từ ảnh chụp ứng dụng và phụ đề khi không demo trực tiếp được. Phân biệt phần đã làm và đề xuất. Phase 8 clone sạch/release chưa thực hiện. Mời câu hỏi.';
    }
  }
  return {addedFrom:input.from,addedTo:input.to,total:presentation.slides.items.length};
}

export async function buildCover({presentation}) {
  const s=presentation.slides.add({width:1280,height:720});s.background.fill='#123E32';
  const texts=[
    ['NHẬN DẠNG BỆNH LÁ CÂY',72,108,1110,220,52,'#FFFFFF',true],
    ['Khoai tây và cà chua · 6 lớp\nTái sử dụng ResNet18 và xây dựng ứng dụng Streamlit',76,340,1080,160,27,'#E6F2EC',false],
    ['Học phần Nhận dạng mẫu  |  Agri Leaf  |  22/11/2026',76,590,1080,64,20,'#E6F2EC',false]
  ];
  for(const [text,left,top,width,height,fontSize,color,bold] of texts){
    const t=s.shapes.add({geometry:'textbox',position:{left,top,width,height},fill:'none',line:{fill:'none',width:0}});
    t.text=text;t.text.style={fontFamily:'Arial',fontSize,color,bold};
  }
  s.speakerNotes.text='Đề tài học phần Nhận dạng mẫu: tái sử dụng checkpoint ResNet18, phát triển giao diện và kiểm chứng. Chưa tự huấn luyện. Điền thông tin sinh viên, lớp và giảng viên theo báo cáo trước khi nộp.';
}
