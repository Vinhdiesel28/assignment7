from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-ZÀ-ỹ0-9]+", text.lower())


class BM25Retriever:
    """BM25 viết từ đầu, phù hợp corpus nhỏ và chạy offline."""

    def __init__(self, documents: list[dict], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1, self.b = k1, b
        self.tokens = [tokenize(d["text"]) for d in documents]
        self.lengths = [len(x) for x in self.tokens]
        self.avgdl = sum(self.lengths) / max(len(self.lengths), 1)
        df = Counter()
        for terms in self.tokens:
            df.update(set(terms))
        n = len(documents)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        q = tokenize(query)
        ranked = []
        for doc, terms, dl in zip(self.documents, self.tokens, self.lengths):
            tf = Counter(terms)
            score = 0.0
            for term in q:
                freq = tf.get(term, 0)
                if not freq:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1))
                score += self.idf.get(term, 0.0) * freq * (self.k1 + 1) / denom
            ranked.append({**doc, "score": round(score, 4)})
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return [x for x in ranked[:top_k] if x["score"] > 0]


class KnowledgeGraph:
    def __init__(self, triples: list[dict]):
        self.triples = triples
        self.adj = defaultdict(list)
        for t in triples:
            self.adj[t["subject"].lower()].append((t["relation"], t["object"]))

    def expand(self, query: str, max_hops: int = 2) -> list[dict]:
        words = set(tokenize(query))
        starts = [n for n in self.adj if set(tokenize(n)) & words]
        out, seen = [], set(starts)
        queue = deque((node, 0) for node in starts)
        while queue:
            node, depth = queue.popleft()
            if depth >= max_hops:
                continue
            for relation, obj in self.adj.get(node, []):
                out.append({"subject": node, "relation": relation, "object": obj, "hop": depth + 1})
                key = obj.lower()
                if key not in seen:
                    seen.add(key)
                    queue.append((key, depth + 1))
        return out[:12]


class DiabetesAgent:
    def __init__(self, knowledge_dir: Path | None = None):
        knowledge_dir = knowledge_dir or ROOT / "knowledge"
        self.documents = json.loads((knowledge_dir / "documents.json").read_text(encoding="utf-8"))
        self.triples = json.loads((knowledge_dir / "graph.json").read_text(encoding="utf-8"))
        self.retriever = BM25Retriever(self.documents)
        self.graph = KnowledgeGraph(self.triples)

    def answer(self, question: str, top_k: int = 3) -> dict:
        if not question or not question.strip():
            raise ValueError("Câu hỏi không được để trống.")
        docs = self.retriever.search(question, top_k)
        graph = self.graph.expand(question)
        if not docs:
            answer = "Kho tri thức hiện chưa có đoạn đủ liên quan. Hãy hỏi cụ thể về dấu hiệu, yếu tố nguy cơ, xét nghiệm hoặc phòng ngừa."
        else:
            evidence = " ".join(d["text"] for d in docs)
            answer = evidence[:1200]
            if graph:
                links = "; ".join(f'{x["subject"]} -{x["relation"]}-> {x["object"]}' for x in graph[:4])
                answer += f"\n\nLiên kết trong Knowledge Graph: {links}."
        return {
            "question": question,
            "answer": answer,
            "sources": [{"title": d["title"], "url": d["url"], "score": d["score"]} for d in docs],
            "graph_paths": graph,
            "method": "BM25 + Knowledge Graph (offline)",
            "notice": "Nội dung phục vụ học tập, không thay thế tư vấn hoặc chẩn đoán y khoa.",
        }


if __name__ == "__main__":
    agent = DiabetesAgent()
    print(json.dumps(agent.answer("Yếu tố nguy cơ của đái tháo đường type 2 là gì?"), ensure_ascii=False, indent=2))
