from dotenv import load_dotenv
load_dotenv()

from src import OpenAIEmbedder
from src.chunking import compute_similarity

e = OpenAIEmbedder()

pairs = [
    (
        "Khách hàng có thể đặt xe qua ứng dụng Xanh SM.",
        "Người dùng đặt chuyến đi bằng app Xanh SM.",
        "high",
    ),
    (
        "Tài xế phải có bằng lái xe hợp lệ khi tham gia dịch vụ.",
        "Lái xe cần cung cấp giấy phép lái xe còn hiệu lực.",
        "high",
    ),
    (
        "Chính sách hoàn tiền khi hủy chuyến trong vòng 5 phút.",
        "Nhà hàng cần đảm bảo chất lượng vệ sinh thực phẩm.",
        "low",
    ),
    (
        "Xanh SM bảo vệ thông tin cá nhân của khách hàng theo quy định pháp luật.",
        "Dữ liệu người dùng được mã hóa và không chia sẻ cho bên thứ ba.",
        "high",
    ),
    (
        "Tài xế bị trừ điểm khi hủy chuyến nhiều lần.",
        "Khách hàng nhận khuyến mãi khi đặt xe lần đầu.",
        "low",
    ),
]

print(f"{'Pair':<5} {'Actual':>8}  {'Predict':>7}  {'Đúng?':<5}  Câu A / Câu B")
print("-" * 90)
for i, (a, b, predict) in enumerate(pairs, 1):
    score = compute_similarity(e(a), e(b))
    actual_label = "high" if score >= 0.5 else "low"
    correct = "✅" if actual_label == predict else "❌"
    print(f"  {i}   {score:>8.4f}  {predict:>7}  {correct}  {a[:55]}")
    print(f"                              {b[:55]}")
    print()
