import os, sys, json, math
from statistics import median, quantiles

EPS = {
    "CC": 0.05,
    "CCMAX": 1.0,
    "SLOC": 5.0,
    "NEST": 1.0,
}
IMPROVED_DENOM = "all"

def fmt_num(x: float) -> str:
    if x is None: return "--"
    if math.isclose(x, round(x), rel_tol=1e-12, abs_tol=1e-12):
        return str(int(round(x)))
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0","") else s

def fmt_pct(p: float) -> str:
    if p is None: return "--%"
    s = f"{p:.3f}".rstrip("0").rstrip(".")
    if s == "": s = "0"
    return s + "%"

def med_iqr(vals):
    if not vals: return None, None
    m = median(vals)
    if len(vals) >= 2:
        q = quantiles(vals, n=4, method="inclusive")
        iqr = q[2] - q[0]
    else:
        iqr = 0.0
    return m, iqr

def load_deltas(root_dir):
    d = {"CC":[], "CCMAX":[], "SLOC":[], "NEST":[]}
    n = 0
    for dirpath, _, files in os.walk(root_dir):
        for name in files:
            if not name.endswith(".json") or name.startswith("processing_summary"):
                continue
            p = os.path.join(dirpath, name)
            try:
                data = json.load(open(p, encoding="utf-8"))
                m = data.get("metrics") or {}
                pre = m.get("original_metrics") or {}
                post = m.get("refactored_metrics") or {}
                keys = ("avg_cc","max_cc","file_sloc_nloc","max_nd_in_file")
                if not all(k in pre for k in keys) or not all(k in post for k in keys):
                    continue
                d["CC"].append(float(post["avg_cc"]) - float(pre["avg_cc"]))
                d["CCMAX"].append(float(post["max_cc"]) - float(pre["max_cc"]))
                d["SLOC"].append(float(post["file_sloc_nloc"]) - float(pre["file_sloc_nloc"]))
                d["NEST"].append(float(post["max_nd_in_file"]) - float(pre["max_nd_in_file"]))
                n += 1
            except Exception:
                continue
    return n, d

def share_improved(vals, changed_mask=None):
    if not vals: return None
    if IMPROVED_DENOM == "changed" and changed_mask is not None:
        v = [v for v, m in zip(vals, changed_mask) if m]
        if not v: return 0.0
        return 100.0 * sum(1 for x in v if x < 0) / len(v)
    # default: denominator = all paired files
    return 100.0 * sum(1 for x in vals if x < 0) / len(vals)

def metric_cell(vals, eps):
    if not vals:
        return "-- (--) / --%"
    # changed-only set for med/IQR
    changed_mask = [abs(v) >= eps for v in vals]
    changed_vals = [v for v in vals if abs(v) >= eps]

    m, i = med_iqr(changed_vals)
    imp = share_improved(vals, changed_mask)

    if not changed_vals:
        m, i = 0.0, 0.0
        if imp is None: imp = 0.0

    return f"{fmt_num(m)} ({fmt_num(i)}) / {fmt_pct(imp)}"

def main():
    if len(sys.argv) != 2:
        print("Usage: python metric_pooling_utils.py <directory>", file=sys.stderr)
        sys.exit(1)

    n, d = load_deltas(sys.argv[1])

    print(f"Files analysed: {n if n else '--'}")
    print(f"CC     (median (IQR) / % improved): {metric_cell(d['CC'],    EPS['CC'])}")
    print(f"CCMAX  (median (IQR) / % improved): {metric_cell(d['CCMAX'], EPS['CCMAX'])}")
    print(f"SLOC   (median (IQR) / % improved): {metric_cell(d['SLOC'],  EPS['SLOC'])}")
    print(f"NEST   (median (IQR) / % improved): {metric_cell(d['NEST'],  EPS['NEST'])}")

if __name__ == "__main__":
    main()
