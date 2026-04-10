"""
Section 6 — Benchmark Queries
Load 6 Xanh SM files → chunk (SentenceChunker) → embed → run 5 queries → print results.
Usage: python benchmark.py
"""
from dotenv import load_dotenv
load_dotenv()

import openai
from pathlib import Path

from src import OpenAIEmbedder
from src.models import Document
from src.chunking import SentenceChunker
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent

# ── Data files + metadata ────────────────────────────────────────────────────
DATA_DIR = Path("data")
FILES = [
    ("Chính sách bảo vệ dữ liệu cá nhân.txt", {"category": "chính sách",  "source": "xanhsm.com"}),
    ("donhang.txt",                             {"category": "quy trình",   "source": "xanhsm.com"}),
    ("ĐIỀU KHOẢN CHUNG.txt",                   {"category": "điều khoản",  "source": "xanhsm.com"}),
    ("khach_hang.txt",                          {"category": "hỏi đáp",    "audience": "khách hàng"}),
    ("nhahang.txt",                             {"category": "nhà hàng",    "source": "xanhsm.com"}),
    ("tai_xe.txt",                              {"category": "tài xế",      "audience": "tài xế"}),
]

# ── Build index ──────────────────────────────────────────────────────────────
chunker  = SentenceChunker(max_sentences_per_chunk=3)
embedder = OpenAIEmbedder()
store    = EmbeddingStore(embedding_fn=embedder)

print("Indexing documents...")
docs = []
for fname, meta in FILES:
    text = (DATA_DIR / fname).read_text(encoding="utf-8", errors="ignore")
    for i, chunk in enumerate(chunker.chunk(text)):
        doc_id = f"{fname}::{i}"
        docs.append(Document(id=doc_id, content=chunk, metadata={**meta, "doc_id": doc_id}))

store.add_documents(docs)
print(f"Total chunks indexed: {store.get_collection_size()}\n")

# ── LLM wrapper ──────────────────────────────────────────────────────────────
_client = openai.OpenAI()

def llm_fn(prompt: str) -> str:
    resp = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0,
    )
    return resp.choices[0].message.content.strip()

agent = KnowledgeBaseAgent(store=store, llm_fn=llm_fn)

# ── Benchmark queries + gold answers ─────────────────────────────────────────
QUERIES = [
    "Khách hàng có thể hủy chuyến xe trong bao lâu mà không bị tính phí?",
    "Tài xế cần cung cấp những giấy tờ gì khi đăng ký tham gia Xanh SM?",
    "Xanh SM xử lý thông tin cá nhân của khách hàng như thế nào?",
    "Quy trình giao hàng Xanh Express diễn ra như thế nào?",
    "Nhà hàng cần đáp ứng các tiêu chuẩn gì để hợp tác với Xanh SM?",
]

GOLD = [
    "Khách hàng có thể hủy chuyến miễn phí trong vòng 5 phút sau khi đặt xe.",
    "Tài xế cần cung cấp bằng lái xe, CMND/CCCD, đăng ký xe và bảo hiểm còn hiệu lực.",
    "Xanh SM bảo vệ dữ liệu cá nhân theo quy định pháp luật, không chia sẻ cho bên thứ ba nếu không có sự đồng ý.",
    "Khách đặt đơn → tài xế nhận đơn → lấy hàng → giao hàng → xác nhận hoàn thành.",
    "Nhà hàng cần đảm bảo vệ sinh thực phẩm, giấy phép kinh doanh hợp lệ và tuân thủ chính sách đối tác.",
]

# ── Run ──────────────────────────────────────────────────────────────────────
SEP = "=" * 80
print(SEP)
for i, (query, gold) in enumerate(zip(QUERIES, GOLD), 1):
    top3    = store.search(query, top_k=3)
    top1    = top3[0]
    answer  = agent.answer(query, top_k=3)

    print(f"\n[Q{i}] {query}")
    print(f"  Gold       : {gold}")
    print(f"  Top-1 score: {top1['score']:.4f}")
    print(f"  Top-1 chunk: {top1['content'][:120].replace(chr(10), ' ')} ...")
    print(f"  Agent ans  : {answer[:200].replace(chr(10), ' ')}")
    print("-" * 80)

print(f"\nDone. Queries run: {len(QUERIES)}")
