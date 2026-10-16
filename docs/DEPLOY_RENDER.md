# Deploy Render

1. Push toàn bộ repository lên GitHub.
2. Trong Render chọn **New > Blueprint**.
3. Kết nối repository `Vinhdiesel28/assignment7`.
4. Render tự đọc `render.yaml`; chọn gói Free và bấm Apply.
5. Khi build hoàn tất, mở `/health`. Kết quả hợp lệ có `status: ok`, số tài liệu và số triple.

Không cần biến môi trường hoặc API key. Corpus, graph, preprocessor và trọng số NumPy đã nằm trong repository.
