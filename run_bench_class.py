import csv, json, sys, urllib.request

def urlopen_retry(req, timeout=600, tries=6):
    import time
    for a in range(tries):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception:
            if a == tries - 1: raise
            time.sleep(20 * (a + 1))

LANG = sys.argv[1]  # en or jp
cases = list(csv.DictReader(open('../benchmark_v1/classification_cases.csv')))
def render_en(r):
    return f"""You are reviewing a differential gene expression result (treatment vs control).
Gene: {r['index']}
baseMean: {float(r['baseMean']):.4g}
log2FoldChange: {float(r['log2FoldChange']):.3g}
padj (FDR-adjusted p-value): {float(r['padj']):.3g}
Decision rule: a gene is UP if padj < 0.05 and log2FoldChange >= 1; DOWN if padj < 0.05 and log2FoldChange <= -1; otherwise NO_CHANGE.
Answer with exactly one word: UP, DOWN, or NO_CHANGE."""
def render_jp(r):
    return f"""あなたは発現変動解析の結果（処置群 vs 対照群）をレビューしています。
遺伝子: {r['index']}
baseMean: {float(r['baseMean']):.4g}
log2FoldChange: {float(r['log2FoldChange']):.3g}
padj（FDR調整済みp値）: {float(r['padj']):.3g}
判定基準: padj < 0.05 かつ log2FoldChange >= 1 なら UP、padj < 0.05 かつ log2FoldChange <= -1 なら DOWN、それ以外は NO_CHANGE です。
UP、DOWN、NO_CHANGE のいずれか1語だけで答えてください。"""
render = render_en if LANG == 'en' else render_jp
out = open(f'bench_class_{LANG}.csv', 'w', newline='')
w = csv.writer(out); w.writerow(['truth', 'band', 'pred'])
done = 0
for r in cases:
    body = json.dumps({'model': 'local', 'messages': [{'role': 'user', 'content': render(r)}], 'temperature': 0, 'max_tokens': 8}).encode()
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=body, headers={'Content-Type': 'application/json'})
    ans = json.loads(urlopen_retry(req).read())['choices'][0]['message']['content'].strip().upper()
    pred = next((x for x in ['NO_CHANGE', 'UP', 'DOWN'] if x in ans), 'PARSE_FAIL')
    w.writerow([r['truth'], r['band'], pred]); out.flush(); done += 1
    if done % 100 == 0: print(f'{done}/{len(cases)}', flush=True)
print('BENCH CLASS', LANG, done)
