import csv, json, sys, urllib.request

def urlopen_retry(req, timeout=600, tries=6):
    import time
    for a in range(tries):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception:
            if a == tries - 1: raise
            time.sleep(20 * (a + 1))

LANG = sys.argv[1]
items = list(csv.DictReader(open('../benchmark_v1/verification_items.csv')))
def render_en(it):
    return f"""You are verifying a statement against an experiment record.
Record excerpt:
{it['evidence']}
Statement: "{it['statement_en']}"
If the statement is fully consistent with the record, answer SUPPORTED. If any part contradicts the record (a wrong value, a wrong direction, or significance claimed where the values do not support it, or no-change claimed where the record shows significant change), answer CONTRADICTED.
Answer with exactly one word: SUPPORTED or CONTRADICTED."""
def render_jp(it):
    return f"""あなたは実験記録と文の整合を検証しています。
記録の抜粋:
{it['evidence']}
文: 「{it['statement_jp']}」
文が記録と完全に整合していれば SUPPORTED、数値・方向・有意性のいずれかが記録と矛盾していれば CONTRADICTED と答えてください。
SUPPORTED か CONTRADICTED のいずれか1語だけで答えてください。"""
render = render_en if LANG == 'en' else render_jp
out = open(f'bench_verif_{LANG}.csv', 'w', newline='')
w = csv.writer(out); w.writerow(['truth', 'band', 'pred'])
done = 0
for it in items:
    body = json.dumps({'model': 'local', 'messages': [{'role': 'user', 'content': render(it)}], 'temperature': 0, 'max_tokens': 320}).encode()
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=body, headers={'Content-Type': 'application/json'})
    ans = json.loads(urlopen_retry(req).read())['choices'][0]['message']['content'].strip().upper()
    pred = 'SUPPORTED' if ans.startswith('SUPPORTED') else ('CONTRADICTED' if ans.startswith('CONTRADICTED') else 'PARSE_FAIL')
    w.writerow([it['truth'], it['band'], pred]); out.flush(); done += 1
print('BENCH VERIF', LANG, done)
