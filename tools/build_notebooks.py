from __future__ import annotations

import json
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks"


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text)


def save(name, cells):
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata.language_info = {"name": "python", "version": "3.11"}
    nbf.write(nb, OUT / name)


common = """from pathlib import Path
import json, sys
ROOT = Path.cwd()
if not (ROOT / 'knowledge').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
print('Project:', ROOT)"""

save("01_knowledge_graph.ipynb", [
    md("# Assignment 07 - Notebook 01\n## Knowledge Base và Knowledge Graph\n\nNotebook giải thích từng bước cách biểu diễn tri thức về đái tháo đường bằng entity, relationship, attribute và triple. Chạy các cell từ trên xuống."),
    md("## 1. Khởi tạo\n\nXác định thư mục dự án để notebook chạy được cả từ JupyterLab và VS Code."),
    code(common),
    md("## 2. Đọc Knowledge Base\n\n`documents.json` là kho văn bản có tiêu đề, URL nguồn và nội dung. `graph.json` là danh sách triple `subject - relation - object`."),
    code("documents = json.loads((ROOT/'knowledge/documents.json').read_text(encoding='utf-8'))\ntriples = json.loads((ROOT/'knowledge/graph.json').read_text(encoding='utf-8'))\nprint('Số tài liệu:', len(documents))\nprint('Số triple:', len(triples))\ndocuments[:2]"),
    md("## 3. Entity - Relationship - Attribute\n\nEntity là đối tượng như `type 2`, relationship là liên hệ như `có yếu tố nguy cơ`, còn thuộc tính mô tả entity. Triple tạo một cạnh có hướng trong đồ thị."),
    code("for t in triples[:8]:\n    print(f\"({t['subject']}) -[{t['relation']}]-> ({t['object']})\")"),
    md("## 4. Dựng danh sách kề\n\nDanh sách kề giúp duyệt từ một thực thể sang các thực thể liên quan. Đây là bản đơn giản của property graph; khi triển khai lớn có thể chuyển sang Neo4j và Cypher."),
    code("from collections import defaultdict\nadj = defaultdict(list)\nfor t in triples:\n    adj[t['subject'].lower()].append((t['relation'], t['object']))\nadj['đái tháo đường']"),
    md("## 5. Truy vấn multi-hop\n\nCâu hỏi nhiều bước cần đi qua hơn một cạnh, ví dụ từ `type 2` tới yếu tố nguy cơ rồi tới hành động cải thiện."),
    code("from src.rag_agent import KnowledgeGraph\nkg = KnowledgeGraph(triples)\npaths = kg.expand('type 2 thừa cân ít vận động', max_hops=2)\npaths"),
    md("## 6. Nhận xét\n\nKnowledge Graph biểu diễn quan hệ rõ và hỗ trợ suy luận nhiều bước, nhưng tốn công xây dựng schema và kiểm soát chất lượng. Trong bài này graph nhỏ được lưu JSON để notebook chạy độc lập; Neo4j là hướng mở rộng phù hợp khi số node và truy vấn tăng.")
])

save("02_rag_from_scratch.ipynb", [
    md("# Assignment 07 - Notebook 02\n## RAG từ đầu với BM25\n\nNotebook trình bày chuỗi Indexing → Retrieval → Augmentation → Generation bằng code tự viết, không phụ thuộc API trả phí."),
    md("## 1. Khởi tạo và đọc corpus"), code(common),
    code("documents = json.loads((ROOT/'knowledge/documents.json').read_text(encoding='utf-8'))\n[(d['id'], d['title']) for d in documents]"),
    md("## 2. Chunking và indexing\n\nCorpus mẫu đã được biên tập thành sáu đoạn ngắn. Với PDF dài, cần chia theo tiêu đề hoặc cửa sổ token có overlap để tránh cắt mất ngữ nghĩa."),
    code("for d in documents:\n    print(d['id'], '->', len(d['text'].split()), 'từ')"),
    md("## 3. BM25 scratch\n\nBM25 dùng tần suất từ, độ hiếm của từ trong corpus và chuẩn hóa độ dài tài liệu. Nó là baseline nhanh, dễ giải thích nhưng không hiểu đầy đủ đồng nghĩa/ngữ cảnh."),
    code("from src.rag_agent import BM25Retriever, tokenize\nretriever = BM25Retriever(documents)\nprint('Kích thước từ vựng:', len(retriever.idf))"),
    md("## 4. Retrieval Top-K\n\nChỉ các đoạn có điểm lớn hơn 0 được đưa vào context, giúp giảm nhiễu so với đưa toàn bộ tài liệu vào prompt."),
    code("query = 'Yếu tố nguy cơ của đái tháo đường type 2 là gì?'\nhits = retriever.search(query, top_k=3)\n[(h['title'], h['score']) for h in hits]"),
    md("## 5. Augmentation và generation\n\nBản offline ghép các bằng chứng truy xuất và giữ URL nguồn. Khi có LLM, chính context này được đưa vào prompt với yêu cầu chỉ trả lời dựa trên nguồn."),
    code("context = '\\n'.join(f\"[{i+1}] {h['text']}\" for i,h in enumerate(hits))\nprint(context)"),
    md("## 6. Cải tiến RAG\n\nCó thể thêm query rewriting, query expansion, decomposition trước retrieval; sau retrieval dùng reranking và context compression. GraphRAG bổ sung các đường đi giữa thực thể để xử lý câu hỏi multi-hop.")
])

save("03_diabetes_agent.ipynb", [
    md("# Assignment 07 - Notebook 03\n## Diabetes Knowledge Agent và triển khai\n\nAgent phối hợp bộ truy xuất BM25 với Knowledge Graph, trả lời có nguồn và nêu giới hạn sử dụng."),
    md("## 1. Khởi tạo"), code(common),
    code("from src.rag_agent import DiabetesAgent\nagent = DiabetesAgent(ROOT/'knowledge')\nprint('Tài liệu:', len(agent.documents), '| Triple:', len(agent.triples))"),
    md("## 2. Luồng Agent\n\n1) nhận câu hỏi; 2) chọn công cụ BM25; 3) mở rộng entity bằng graph; 4) tổng hợp bằng chứng; 5) trả lời kèm nguồn. Agent không tự đặt chẩn đoán."),
    code("result = agent.answer('Đái tháo đường có thể gây biến chứng gì?', top_k=3)\nprint(result['answer'])\nprint('Nguồn:', [x['title'] for x in result['sources']])"),
    md("## 3. Ví dụ câu hỏi semantic và multi-hop"),
    code("questions = [\n 'Dấu hiệu nào thường gặp?',\n 'Xét nghiệm nào dùng để đánh giá?',\n 'Type 2 liên quan yếu tố nào và có thể cải thiện ra sao?'\n]\nfor q in questions:\n    r = agent.answer(q)\n    print('\\nQ:', q, '\\nA:', r['answer'][:320])"),
    md("## 4. API Flask\n\nWeb cung cấp `POST /api/chat` với JSON `{question, top_k}` và `GET /health`. Render chạy Gunicorn theo `render.yaml`."),
    code("print((ROOT/'render.yaml').read_text(encoding='utf-8'))"),
    md("## 5. Công cụ dự đoán của Agent\n\nCheckpoint MLP PyTorch tốt nhất từ Assignment 3 được xuất sang NumPy. Preprocessor giữ đúng 15 cột gốc; web nhận các chỉ số chính và điền giá trị mặc định cho trường còn lại. Điểm chưa calibration nên không được gọi là xác suất mắc bệnh."),
    code("sys.path.insert(0, str(ROOT/'web'))\nfrom app import predict_risk\npredict_risk({'age':45,'bmi':27.5,'hbA1c_level':5.7,'blood_glucose_level':120,'hypertension':0,'heart_disease':0})"),
    md("## 6. Giới hạn và đạo đức\n\nCorpus chỉ có sáu đoạn nên độ bao phủ thấp; BM25 nhạy với từ khóa; graph được xây thủ công. Hệ thống cần chuyên gia y tế thẩm định trước mọi ứng dụng thực tế. Đầu ra chỉ phục vụ học tập, không thay thế chẩn đoán, kê đơn hoặc điều trị.")
])

print("Đã tạo 3 notebook tại", OUT)
