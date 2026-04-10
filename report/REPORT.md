# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Bá Khánh
**Nhóm:** D3-C401
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:*
Cosine similarity đo góc giữa hai vector trong không gian nhiều chiều. Khi hai đoạn văn bản được chuyển thành embedding vector, high cosine similarity (gần 1.0) có nghĩa là hai vector đó cùng hướng — tức là hai đoạn văn nói về cùng một chủ đề, ý nghĩa tương tự nhau, dù có thể dùng từ ngữ khác nhau.

**Ví dụ HIGH similarity:**
- Sentence A:
"Con chó đuổi theo quả bóng."
- Sentence B: "Chó con chạy theo quả bóng ."
- Tại sao tương đồng:Cả 2 đều diễn tả con chó đang đuổi quả bóng

**Ví dụ LOW similarity:**
- Sentence A: "Con chó đuổi theo quả bóng."
- Sentence B: " Lá có thể quang hợp sinh ra oxi. "
- Tại sao khác: Câu A kể về "chó"
nhưng ở câu 2 lại nói về "khả năng quang hợp của lá"

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*
Cosine similarity chỉ đo góc giữa hai vector, không bị ảnh hưởng bởi độ dài— nên đoạn văn ngắn và đoạn văn dài cùng chủ đề vẫn có similarity cao. Euclidean distance đo khoảng cách tuyệt đối giữa hai điểm,khiến khoảng cách xa hơn dù là tương đồng nghĩa ngữ.
### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
- Formula: `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))` 

num_chunks = ceil (10000 - 50) / (500-50)
= ceil(2,11111) = 23 
> *Đáp án:*23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*
num_chunks_new = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = **25 chunks** 

#### tăng thêm 2 chunk so với overlap=50. Overlap lớn hơn giúp bảo toàn ngữ cảnh tại ranh giới giữa các chunk, tránh trường hợp một câu quan trọng bị cắt đứt.
---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:* Xanh SM , do thấy chatbot về chính sách xanh SM chưa được tối ưu.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | Chính sách bảo vệ dữ liệu cá nhân.txt | https://www.xanhsm.com/helps | 36,439 | category= chính sách, source=xanhsm.com |
| 2 | donhang.txt|https://www.xanhsm.com/news/so-tay-van-hanh-dich-vu-giao-hang-xanh-express |15,104 |category=quy trình , source=xanhsm.com |
| 3 | ĐIỀU KHOẢN CHUNG.txt|https://www.xanhsm.com/helps |208,756 |category= Điều khoản,dịch vụ, source=xanhsm.com|
| 4 |khach_hang.txt|https://www.xanhsm.com/terms-policies/general?terms=12 |52,702 |category = hỏi đáp hỗ trợ khách hàng, audience = khách hàng  |
| 5 |nhahang.txt|https://www.xanhsm.com/terms-policies/general?terms=10 |38,996 | category=chính sách nhà hàng, source=xanhsm.com |
|6  |tai_xe.txt | https://www.xanhsm.com/terms-policies/general?terms=6|11,424|category=điều khoản của tài xế, audience = tài xế|
### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
| category | string | `chính sách ` , `quy trình `,`Điều khoản ` | Lọc theo loại tài liệu, tránh trả về chunk không liên quan loại nội dung |
| source | string | `xanhsm.com` | Truy vết nguồn gốc tài liệu, hỗ trợ citation và kiểm tra độ tin cậy |
| audience | string | `tài xế`, `khách hàng ` | Lọc theo đối tượng người dùng, trả về nội dung phù hợp với từng nhóm |


---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| khach_hang.txt | FixedSizeChunker (`fixed_size`) | 264 | 200 | Không — cắt cứng theo ký tự |
| khach_hang.txt | SentenceChunker (`by_sentences`) | 116 | 339 | Có — giữ nguyên câu hoàn chỉnh |
| khach_hang.txt | RecursiveChunker (`recursive`) | 303 | 129 | Trung bình — ưu tiên dấu xuống dòng |
| tai_xe.txt | FixedSizeChunker (`fixed_size`) | 59 | 199 | Không — cắt cứng theo ký tự |
| tai_xe.txt | SentenceChunker (`by_sentences`) | 39 | 225 | Có — giữ nguyên câu hoàn chỉnh |
| tai_xe.txt | RecursiveChunker (`recursive`) | 65 | 135 | Trung bình — ưu tiên dấu xuống dòng |
| donhang.txt | FixedSizeChunker (`fixed_size`) | 81 | 199 | Không — cắt cứng theo ký tự |
| donhang.txt | SentenceChunker (`by_sentences`) | 50 | 240 | Có — giữ nguyên câu hoàn chỉnh |
| donhang.txt | RecursiveChunker (`recursive`) | 86 | 139 | Trung bình — ưu tiên dấu xuống dòng |




****  Sử dụng compare.py để in ra các thông số để so sánh ****

- Output: 
  === khach_hang.txt ===
  fixed_size: count=264, avg_length=200
  by_sentences: count=116, avg_length=339
  recursive: count=303, avg_length=129
=== tai_xe.txt ===
  fixed_size: count=59, avg_length=199
  by_sentences: count=39, avg_length=225
  recursive: count=65, avg_length=135
=== donhang.txt ===
  fixed_size: count=81, avg_length=199
  by_sentences: count=50, avg_length=240
  recursive: count=86, avg_length=139


### Strategy Của Tôi

**Loại:** SentenceChunker

**Mô tả cách hoạt động:**
SentenceChunker tách văn bản thành các câu dựa trên dấu` ., !, ?` theo sau bởi khoảng trắng hoặc xuống dòng, rồi gom các câu liên tiếp thành một chunk theo max_sentences_per_chunk. Mỗi chunk luôn chứa câu hoàn chỉnh, không cắt giữa câu. Nếu văn bản không có dấu kết thúc câu, toàn bộ đoạn sẽ là một chunk.

**Tại sao tôi chọn strategy này cho domain nhóm?**

Các tài liệu Xanh SM (FAQ tài xế, khách hàng, nhà hàng, điều khoản) được viết theo dạng hỏi-đáp với từng câu mang một ý nghĩa độc lập và rõ ràng. SentenceChunker khai thác đặc điểm này: mỗi chunk giữ nguyên câu hoàn chỉnh nên khi retrieval, context trả về luôn có nghĩa đầy đủ, không bị cắt cụt ở giữa một quy định hay hướng dẫn. So với FixedSizeChunker (avg_length ~200) thì SentenceChunker tạo chunk dài hơn (~225–339 ký tự) và ít chunk hơn, phù hợp để embed ngữ nghĩa trọn vẹn hơn.

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| khach_hang.txt | SentenceChunker — best baseline | 116 | 339 | Tốt — giữ nguyên câu hoàn chỉnh |
| khach_hang.txt | **SentenceChunker — của tôi** | **116** | **339** | **Tốt — câu hoàn chỉnh, ngữ nghĩa đầy đủ** |
| tai_xe.txt | SentenceChunker — best baseline | 39 | 225 | Tốt — câu hoàn chỉnh, ít chunk |
| tai_xe.txt | **SentenceChunker — của tôi** | **39** | **225** | **Tốt — ít chunk hơn, mỗi chunk giữ đủ ý** |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | SentenceChunker | 8 | Giữ câu hoàn chỉnh, ngữ nghĩa đầy đủ, ít chunk hơn | Chunk dài hơn, tốn nhiều token hơn khi embed |
| [Thư] | RecursiveChunker | 6 | Linh hoạt với nhiều loại văn bản, chunk nhỏ hơn | Chunk quá ngắn (~130–139 ký tự), dễ mất ngữ cảnh |
| [Lực] | FixedSizeChunker | 5 | Đơn giản, dễ kiểm soát kích thước | Cắt giữa câu, chunk mất nghĩa, retrieval kém chính xác |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*
SentenceChunker phù hợp nhất với domain Xanh SM vì tài liệu FAQ và điều khoản được viết theo từng câu hoàn chỉnh, mỗi câu mang ý nghĩa độc lập. Chunk có độ dài trung bình 225–339 ký tự và số lượng ít giúp embedding đầy đủ ngữ nghĩa, cải thiện retrieval và tránh mất thông tin tại ranh giới. Trong khi đó, RecursiveChunker tạo chunk quá ngắn dễ tách rời Q&A, còn FixedSizeChunker cắt theo ký tự nên không phù hợp với cấu trúc câu tiếng Việt.
---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*

Sử dụng regex `(?<=[.!?])[\s]+|(?<=[.])\n `(lookbehind) để tách văn bản thành các câu dựa trên khoảng trắng sau` ., !, ? `hoặc xuống dòng sau` .. ` Các câu sau khi tách được loại bỏ khoảng trắng thừa, rồi gom max_sentences_per_chunk câu liên tiếp thành một chunk bằng " ".join(...). Edge case được xử lý rõ ràng: text rỗng trả về [], còn văn bản không có dấu kết thúc câu thì được xem như một câu duy nhất.
Cung cấp Phản hồi của bạn trên BizChat


**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*
`Hàm _split` hoạt động theo cơ chế đệ quy: lần lượt thử tách text bằng các separator theo mức độ ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Các phần sau khi tách được gom vào buffer; khi vượt quá chunk_size, buffer sẽ được flush và phần còn lại tiếp tục được xử lý đệ quy với separator tiếp theo nếu vẫn quá dài.
Có hai base case: `(1) độ dài current_text nhỏ hơn hoặc bằng chunk_size thì trả về nguyên văn`; `(2) không còn separator nào thì cắt cứng theo chunk_size`. Trường hợp đặc biệt với separator rỗng "", text được tách thành từng ký tự bằng list(current_text). 

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*
Hàm `add_documents `thực hiện embedding cho từng document bằng` _embedding_fn(doc.content)`, sau đó tạo một record gồm ` id, content, embedding và metadata (metadata gốc kèm thêm doc_id)`, rồi lưu vào `self._store `dưới dạng list in-memory.
Hàm search embed query thành vector, tính dot product giữa vector query và embedding của mỗi record trong store, sắp xếp kết quả theo score giảm dần và trả về top_k item đầu dưới dạng` {"content", "score", "metadata"}`. Do embedding đã được normalize sẵn, dot product ở đây tương đương với cosine similarity.
**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*

`search_with_filter` thực hiện **filter trước** rồi mới search: lọc `self._store` giữ lại các record có metadata khớp toàn bộ key-value trong `metadata_filter`, sau đó gọi `_search_records` trên tập đã lọc. Nếu `metadata_filter` là `None` thì fallback về `search` thông thường trên toàn bộ store. `delete_document` xóa bằng cách dùng list comprehension tạo lại `self._store` chỉ giữ các record có `metadata["doc_id"] != doc_id`, trả về `True` nếu kích thước store giảm, `False` nếu không có record nào bị xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*
`answer` thực hiện RAG pattern 3 bước: (1) gọi `store.search(question, top_k)` lấy `top_k` chunk liên quan nhất; (2) nối các chunk thành context bằng `"\n\n".join(f"[{i+1}] {r['content']}")` để đánh số thứ tự; (3) build prompt theo cấu trúc `"You are a helpful assistant. Use the context below...\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"` rồi truyền vào `llm_fn`. Context được inject trực tiếp vào giữa system instruction và câu hỏi, giúp LLM biết phải dựa vào đó để trả lời.
### Test Results

```
# Paste output of: pytest tests/ -v
```
========================= test session starts ==========================
platform win32 -- Python 3.12.4, pytest-8.4.0, pluggy-1.6.0 -- C:\ProgramData\miniconda3\python.exe
codspeed: 3.2.0 (disabled, mode: walltime, timer_resolution: 100.0ns)
cachedir: .pytest_cache
benchmark: 5.1.0 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: K:\VIN_AI\Buoi_7\2A202600135-NguyenBaKhanh-Day07
plugins: anyio-3.7.1, langsmith-0.3.45, asyncio-0.26.0, benchmark-5.1.0, codspeed-3.2.0, recording-0.13.4, socket-0.7.0, syrupy-4.9.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 42 items                                                                                                            

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                                   [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                            [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                                     [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                                      [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                           [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                           [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                                 [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                                  [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                                [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                                  [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                                  [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                             [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                         [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                                   [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                          [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                              [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED                        [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                              [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                                  [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                                    [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                                      [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                            [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                                 [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                                   [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED                       [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                                    [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                             [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                            [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                                       [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                                   [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                              [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                                  [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                                        [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                                  [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED               [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                             [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                            [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED                [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                           [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED                    [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED          [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED              [100%]

===================================================== 42 passed in 1.06s =====================================================
**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |


| 1 | Khách hàng có thể đặt xe qua ứng dụng Xanh SM. | Người dùng đặt chuyến đi bằng app Xanh SM. | high | 0.7336 |  |
| 2 | Tài xế phải có bằng lái xe hợp lệ khi tham gia dịch vụ. | Lái xe cần cung cấp giấy phép lái xe còn hiệu lực. | high | 0.5705 |  |
| 3 | Chính sách hoàn tiền khi hủy chuyến trong vòng 5 phút. | Nhà hàng cần đảm bảo chất lượng vệ sinh thực phẩm. | low | 0.2616 |  |
| 4 | Xanh SM bảo vệ thông tin cá nhân của khách hàng theo quy định pháp luật. | Dữ liệu người dùng được mã hóa và không chia sẻ cho bên thứ ba. | high | 0.4209 |  |
| 5 | Tài xế bị trừ điểm khi hủy chuyến nhiều lần. | Khách hàng nhận khuyến mãi khi đặt xe lần đầu. | low | 0.4609 |  |

- Sử dụng  `predictions.py` để làm bảng so sánh với các test case ở trên

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*
Pair 4 bất ngờ nhất: hai câu nói về cùng chủ đề bảo vệ dữ liệu cá nhân nhưng chỉ đạt 0.4209 — thấp hơn kỳ vọng "high". Điều này cho thấy embedding không chỉ nắm bắt chủ đề mà còn bị ảnh hưởng bởi cách diễn đạt: câu A dùng ngôn ngữ pháp lý ("theo quy định pháp luật") còn câu B dùng ngôn ngữ kỹ thuật ("mã hóa", "bên thứ ba"), khiến vector hai câu lệch nhau dù ý nghĩa tương đồng. Điều này nhắc nhở rằng embedding biểu diễn ngữ cảnh bề mặt lẫn ngữ nghĩa, nên cách dùng từ vẫn ảnh hưởng đến similarity score.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |

| 1 | Khách hàng có thể hủy chuyến xe trong bao lâu mà không bị tính phí? | Khách hàng có thể hủy chuyến miễn phí trong vòng 5 phút sau khi đặt xe. |
| 2 | Tài xế cần cung cấp những giấy tờ gì khi đăng ký tham gia Xanh SM? | Tài xế cần cung cấp bằng lái xe, CMND/CCCD, đăng ký xe và bảo hiểm còn hiệu lực. |
| 3 | Xanh SM xử lý thông tin cá nhân của khách hàng như thế nào? | Xanh SM bảo vệ dữ liệu cá nhân theo quy định pháp luật, không chia sẻ cho bên thứ ba nếu không có sự đồng ý. |
| 4 | Quy trình giao hàng Xanh Express diễn ra như thế nào? | Khách đặt đơn → tài xế nhận đơn → lấy hàng → giao hàng → xác nhận hoàn thành. |
| 5 | Nhà hàng cần đáp ứng các tiêu chuẩn gì để hợp tác với Xanh SM? | Nhà hàng cần đảm bảo vệ sinh thực phẩm, giấy phép kinh doanh hợp lệ và tuân thủ chính sách đối tác. |

### Kết Quả Của Tôi

> Chạy bằng `benchmark.py` — 788 chunks từ 6 file, SentenceChunker (max_sentences=3), text-embedding-3-small, top_k=3


| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Hủy chuyến xe không bị tính phí? | Tài xế không được thỏa thuận riêng hoặc hủy chuyến ngoài app | 0.6168 | Một phần | Khách có thể hủy trước khi tài xế đến lấy hàng mà không bị tính phí |
| 2 | Giấy tờ đăng ký tài xế Xanh SM? | FAQ: giấy hẹn bằng lái + yêu cầu đăng ký Xanh SM Bike | 0.7315 | Có  | CCCD/Hộ chiếu + bằng lái xe còn hiệu lực tối thiểu 1 tháng |
| 3 | Xanh SM xử lý dữ liệu cá nhân thế nào? | Thông tin đơn hàng do khách nhập — Xanh SM không chịu trách nhiệm nếu sai | 0.7258 | Một phần | Yêu cầu thông tin chính xác; khách cần có quyền ủy quyền hợp lệ |
| 4 | Quy trình giao hàng Xanh Express? | QUY TRÌNH XỬ LÝ ĐƠN — Bước 1: Nhận đơn, kiểm tra thông tin... | 0.6138 | Có  | Nhận đơn → kiểm tra thông tin → lấy hàng → giao hàng → xác nhận |
| 5 | Tiêu chuẩn nhà hàng hợp tác Xanh SM? | FAQ đăng ký đối tác nhà hàng/quán ăn trên Xanh SM Ngon | 0.6817 | Có  | Tiêu chuẩn cụ thể không nêu rõ, cần liên hệ Xanh SM để biết thêm |



**Bao nhiêu queries trả về chunk relevant trong top-3?**   4 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
Từ [Thư] tôi học được cách dùng RecursiveChunker với nhiều loại tài liệu có cấu trúc khác nhau . Từ [Lực] tôi thấy rằng FixedSizeChunker dù đơn giản nhưng vẫn cho kết quả chấp nhận được khi tài liệu ngắn, giúp tôi hiểu rõ hơn đánh đổi giữa độ phức tạp và hiệu quả.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
Một nhóm khác dùng metadata filter để chỉ search trong tập con tài liệu phù hợp với ngữ cảnh câu hỏi (ví dụ: lọc `audience=tài xế` trước khi search), giúp tăng độ chính xác rõ rệt.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
Tôi sẽ bổ sung thêm trường metadata `topic` (ví dụ: `hủy chuyến`, `thanh toán`, `đăng ký`) để có thể filter theo chủ đề cụ thể thay vì chỉ theo category chung. Ngoài ra tôi sẽ tách file `ĐIỀU KHOẢN CHUNG.txt` (208,756 ký tự) thành các file nhỏ hơn theo từng dịch vụ, vì file quá lớn tạo ra nhiều chunk nhiễu làm loãng kết quả retrieval.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5/ 5 |
| Document selection | Nhóm | 7/ 10 |
| Chunking strategy | Nhóm | 10/ 15 |
| My approach | Cá nhân | 7/ 10 |
| Similarity predictions | Cá nhân | 4/ 5 |
| Results | Cá nhân | 8/ 10 |
| Core implementation (tests) | Cá nhân | 30/ 30 |
| Demo | Nhóm | 3/ 5 |
| **Tổng** | | **74 / 100** |
