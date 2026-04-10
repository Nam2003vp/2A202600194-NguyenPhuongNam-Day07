from src.chunking import ChunkingStrategyComparator

files = {
    'khach_hang.txt': open('data/khach_hang.txt', encoding='utf-8').read(),
    'tai_xe.txt': open('data/tai_xe.txt', encoding='utf-8').read(),
    'donhang.txt': open('data/donhang.txt', encoding='utf-8').read(),
}

cmp = ChunkingStrategyComparator()
for fname, text in files.items():
    result = cmp.compare(text)
    print(f'=== {fname} ===')
    for strategy, stats in result.items():
        print(f'  {strategy}: count={stats["count"]}, avg_length={stats["avg_length"]:.0f}')
