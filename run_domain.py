import csv, json, sys, urllib.request

def urlopen_retry(req, timeout=600, tries=6):
    import time
    for a in range(tries):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception:
            if a == tries - 1: raise
            time.sleep(20 * (a + 1))

DOMAIN, LANG = sys.argv[1], sys.argv[2]
def ask(prompt, max_tokens=320):
    body = json.dumps({'model': 'local', 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0, 'max_tokens': max_tokens}).encode()
    req = urllib.request.Request('http://127.0.0.1:8080/v1/chat/completions', data=body, headers={'Content-Type': 'application/json'})
    return json.loads(urlopen_retry(req).read())['choices'][0]['message']['content'].strip().upper()
def pf(ans): return 'PASS' if ans.startswith('PASS') else ('FAIL' if ans.startswith('FAIL') else 'PARSE_FAIL')
def sv(ans): return 'SUPPORTED' if ans.startswith('SUPPORTED') else ('CONTRADICTED' if ans.startswith('CONTRADICTED') else 'PARSE_FAIL')
if DOMAIN == 'dose':
    rows = list(csv.DictReader(open('../benchmark_v1/dose_response/dose_cases.csv')))
    def ren(r):
        crit = "converged; bootstrap success rate >= 0.80; 95% CI width (log10) <= 0.5; outlier fraction <= 0.20; pseudo-R2 >= 0.80"
        crit_jp = "収束していること、ブートストラップ成功率 >= 0.80、95%CI幅（log10）<= 0.5、外れ値割合 <= 0.20、疑似R2 >= 0.80"
        m = f"replicates = {r['replicates']}, fitted IC50 = {r['ic50_est']} uM (95% CI {r['ci_low']}-{r['ci_high']}), Hill = {r['hill']}, converged = {r['converged']}, bootstrap success = {r['boot_success']}, CI width (log10) = {r['ci_log10_width']}, outlier fraction = {r['outlier_fraction']}, pseudo-R2 = {r['pseudo_r2']}"
        return (f"You are reviewing a dose-response curve fit. Quality criteria (all must hold): {crit}. Fit: {m}. Answer with exactly one word: PASS or FAIL." if LANG == 'en' else
                f"あなたは用量反応曲線のフィットをレビューしています。品質基準（すべて満たすこと）: {crit_jp}。フィット: {m}。PASS か FAIL のいずれか1語だけで答えてください。")
    out = open(f'bench_dose_{LANG}.csv', 'w', newline=''); w = csv.writer(out); w.writerow(['truth', 'band', 'pred'])
    for r in rows: w.writerow([r['truth'], r['band'], pf(ask(ren(r), 8))]); out.flush()
elif DOMAIN == 'microqc':
    rows = list(csv.DictReader(open('../benchmark_v1/microscopy/micro_qc_cases.csv')))
    def ren(r):
        crit = "miss rate <= 0.05; false-positive rate <= 0.05; area-fraction absolute error <= 0.5 percentage points; median diameter relative error <= 0.05"
        crit_jp = "見逃し率 <= 0.05、誤検出率 <= 0.05、面積分率の絶対誤差 <= 0.5 ポイント、径の相対誤差の中央値 <= 0.05"
        m = f"image {r['image_id']}: miss rate = {r['miss_rate']}, false-positive rate = {r['fp_rate']}, area-fraction absolute error = {r['area_fraction_abs_error_pp']} pp, median diameter relative error = {r['diameter_median_abs_rel_error']}"
        return (f"You are reviewing a microscopy quantification result. Acceptance criteria (all must hold): {crit}. Result: {m}. Answer with exactly one word: PASS or FAIL." if LANG == 'en' else
                f"あなたは顕微鏡定量の結果をレビューしています。受入基準（すべて満たすこと）: {crit_jp}。結果: {m}。PASS か FAIL のいずれか1語だけで答えてください。")
    out = open(f'bench_microqc_{LANG}.csv', 'w', newline=''); w = csv.writer(out); w.writerow(['truth', 'band', 'pred'])
    for r in rows: w.writerow([r['truth'], r['band'], pf(ask(ren(r), 8))]); out.flush()
elif DOMAIN == 'microverif':
    rows = list(csv.DictReader(open('../benchmark_v1/microscopy/micro_verification_items.csv')))
    def ren(r):
        return (f"""You are verifying a statement against a microscopy quantification record.
Record: {r['evidence']}
Statement: "{r['statement_en']}"
If the statement is fully consistent with the record, answer SUPPORTED; if any part contradicts the record, answer CONTRADICTED.
Answer with exactly one word: SUPPORTED or CONTRADICTED.""" if LANG == 'en' else
                f"""あなたは顕微鏡定量の記録と文の整合を検証しています。
記録: {r['evidence']}
文: 「{r['statement_jp']}」
文が記録と完全に整合していれば SUPPORTED、矛盾していれば CONTRADICTED と答えてください。
SUPPORTED か CONTRADICTED のいずれか1語だけで答えてください。""")
    out = open(f'bench_microverif_{LANG}.csv', 'w', newline=''); w = csv.writer(out); w.writerow(['truth', 'band', 'pred'])
    for r in rows: w.writerow([r['truth'], r['band'], sv(ask(ren(r)))]); out.flush()
print('DOMAIN DONE', DOMAIN, LANG)
