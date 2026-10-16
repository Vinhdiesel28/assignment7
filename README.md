# Assignment 07 - Knowledge Base, RAG và Agent

**Nguyễn Minh Vinh - B23DCCN934 - D23CTPM01**  
Môn Phát triển hệ thống thông minh - PGS.TS Trần Đình Quế.

Bài xây dựng trợ lý hỏi đáp về đái tháo đường theo yêu cầu trên bảng: Knowledge Base, Knowledge Graph, RAG, kết hợp mô hình dự đoán và triển khai Agent. Phiên bản web mặc định chạy offline bằng BM25 và graph traversal, trả lời kèm nguồn. Công cụ dự đoán dùng checkpoint MLP PyTorch tốt nhất của Assignment 3, xuất sang NumPy để suy luận nhẹ trên web.

## Thành phần

- `notebooks/01_knowledge_graph.ipynb`: entity, relationship, attribute, triple và truy vấn nhiều bước.
- `notebooks/02_rag_from_scratch.ipynb`: chunking, BM25, retrieval, augmentation, generation.
- `notebooks/03_diabetes_agent.ipynb`: ghép retrieval, graph và Agent; giải thích giới hạn y khoa.
- `report/A07_CT_vinhnm.934.pdf`: báo cáo nộp.
- `web/`: Flask UI và API `/api/chat` để deploy Render.
- `knowledge/`: sáu tài liệu nguồn và Knowledge Graph 14 triple.

## Chạy local

```bash
python -m pip install -r requirements.txt
python web/app.py
```

Mở `http://127.0.0.1:5008`. Deploy bằng Render Blueprint từ `render.yaml`.

## Luồng xử lý

1. Chuẩn hóa câu hỏi và tách token.
2. BM25 xếp hạng các đoạn trong Knowledge Base.
3. Knowledge Graph mở rộng các thực thể liên quan tối đa hai hop.
4. Agent ghép bằng chứng thành câu trả lời và luôn hiển thị nguồn.

## Giới hạn

Đây là bài tập học thuật. Nội dung và đầu ra mô hình không thay thế bác sĩ, không dùng để chẩn đoán, kê đơn hay quyết định điều trị. Hệ thống hiện dùng corpus nhỏ, generation theo bằng chứng và không gọi LLM bên ngoài để tránh phụ thuộc API key.
