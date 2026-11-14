import math
import re
from collections import Counter


def tokens(text):
    english = re.findall(r'[a-z0-9_]+', text.lower())
    chinese = re.findall(r'[\u4e00-\u9fff]+', text)
    return english + [part[i:i+2] for part in chinese for i in range(max(0, len(part)-1))]


def retrieve(documents, query, limit=4):
    """Deterministic local lexical retrieval; not an embedding service or fact verifier."""
    chunks = []
    for doc in documents:
        for index, start in enumerate(range(0, len(doc['text']), 600)):
            text = doc['text'][start:start+750]
            chunks.append(dict(id=f"{doc['id']}:{index}", title=doc['title'], source=doc['source'], text=text))
    query_terms = set(tokens(query))
    stats = [Counter(tokens(c['text'] + c['title'])) for c in chunks]
    for chunk, freq in zip(chunks, stats):
        score = 0.0
        for term in query_terms:
            if freq[term]:
                df = sum(1 for other in stats if other[term])
                score += math.log(1 + (len(chunks)+1)/(df+1)) * min(freq[term], 3)
        chunk['score'] = round(score, 3)
    return sorted((c for c in chunks if c['score'] > 0), key=lambda c: c['score'], reverse=True)[:limit]

