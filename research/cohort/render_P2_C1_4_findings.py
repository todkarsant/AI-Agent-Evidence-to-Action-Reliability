"""Render the P2-C1.4 confirmatory findings report (manuscript section 9.3) from the frozen gate outputs.

  python render_P2_C1_4_findings.py --stage1 stage1/ --stage2 stage2/ --out findings/ \
      [--evidence-availability research/cohort/results/P2_C1_4_EVIDENCE_AVAILABILITY_AUDIT.json]

It only formats numbers the frozen pipeline already produced; it computes no new statistic and applies
no significance rule (none is frozen). Before rendering it checks the hash chain:
  * results.json matches STAGE2_VERDICT.results_json_sha256;
  * the reliability report matches STAGE1_VERDICT.reliability_sha256;
  * Stage 1 and Stage 2 name the same raw-annotation lock (and the same sampling record, if any).
Synthetic or test-mode inputs are rendered with a NOT-A-FINDING banner.
Outputs: P2_C1_4_FINDINGS.md and P2_C1_4_FINDINGS.json (with the hashes of every input).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DIMS = ("W1", "W2", "W3", "W4", "W5", "W6", "W7")
SENS = ("S1", "S2_low", "S2_high")
CLAIM_BOUNDARY = ("The claim is restricted to incremental predictive validity in the newly collected evaluation "
                  "population and protocol. No causal protection, universal reliability, or deployment-safety claim "
                  "is authorized (frozen protocol P2-C1.4-CONFIRMATORY-V1, section 1).")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def refuse(msg: str) -> None:
    sys.stderr.write(f"REFUSED: {msg}\n")
    raise SystemExit(2)


def f(x, d=4) -> str:
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, int):
        return f"{x:,}"
    if isinstance(x, float):
        return f"{x:.{d}g}" if abs(x) < 1e-3 and x != 0 else f"{x:.{d}f}"
    return str(x)


def iv(pair, d=4) -> str:
    return "n/a" if not pair or pair[0] is None else f"[{f(pair[0], d)}, {f(pair[1], d)}]"


def metric(m: dict | None, d=4) -> str:
    if not m or m.get("mean") is None:
        return "n/a"
    return f"{f(m['mean'], d)} {iv([m.get('p2_5'), m.get('p97_5')], d)}"


def side(lo, hi) -> str:
    if lo is None or hi is None:
        return "not available"
    if lo > 0:
        return "entirely above 0"
    if hi < 0:
        return "entirely below 0"
    return "includes 0"


def build(s1: Path, s2: Path, avail: Path | None) -> tuple[str, dict]:
    v1, v2 = load(s1 / "STAGE1_VERDICT.json"), load(s2 / "STAGE2_VERDICT.json")
    rel_p, res_p = s1 / "construction" / "P2_C1_4_XW_RELIABILITY.json", s2 / "analysis" / "results.json"
    if sha(res_p) != v2.get("results_json_sha256"):
        refuse("results.json does not match the Stage 2 verdict")
    if sha(rel_p) != v1.get("reliability_sha256"):
        refuse("reliability report does not match the Stage 1 verdict")
    if v1.get("raw_annotation_lock_sha256") != v2.get("raw_annotation_lock_sha256"):
        refuse("Stage 1 and Stage 2 name different raw-annotation locks")
    if v1.get("sampling_record_sha256") != v2.get("sampling_record_sha256"):
        refuse("Stage 1 and Stage 2 name different sampling records")
    rel, res = load(rel_p), load(res_p)
    rec_p = s1 / "SAMPLING_RECORD.json"
    rec = load(rec_p) if rec_p.is_file() else None
    av = load(avail) if avail else None
    av_note = None
    if av and av.get("n_decisions") != res.get("cohort_flow", {}).get("n_records"):
        av_note = f"Evidence-availability audit omitted: it covers {av.get('n_decisions')} decisions, the cohort {res.get('cohort_flow', {}).get('n_records')}."
        av = None
    test = bool(res.get("test_mode") or res.get("input_marked_synthetic") or v2.get("test_mode"))
    verdicts = res.get("verdicts", {})
    primary_v = verdicts.get("primary")
    pc = res.get("population_counts", {})
    an = res.get("analyses", {})
    L: list[str] = []
    w = L.append

    w("# P2-C1.4 confirmatory findings")
    w("")
    if test:
        w("> **SYNTHETIC / TEST-MODE INPUT — NOT A FINDING.** These numbers exist only to check the report pipeline.")
        w("")
    w(f"**Primary verdict:** `{primary_v}`  ")
    w(f"**Riley verdict:** `{verdicts.get('riley')}`  ")
    rob = verdicts.get("robustness", {})
    w(f"**Robustness flag:** `{rob.get('flag', 'n/a')}`  ")
    w(f"**Inferential rule:** {verdicts.get('inferential_decision_rule', 'none frozen')}")
    w("")
    w("## Provenance")
    w("")
    w("| Item | SHA-256 |")
    w("|---|---|")
    prov = {
        "locked cohort": v2.get("cohort_sha256"),
        "raw-annotation lock": v1.get("raw_annotation_lock_sha256"),
        "X_W (annotated cases)": v2.get("xw_annotated_sha256") or v1.get("xw_sha256"),
        "X_W (full cohort)": v2.get("xw_sha256"),
        "sampling record": v2.get("sampling_record_sha256"),
        "reliability report": v1.get("reliability_sha256"),
        "reference-SQL features": v2.get("reference_features_sha256"),
        "results.json": v2.get("results_json_sha256"),
        "evidence-availability audit": sha(avail) if av else None,
    }
    for k, h in prov.items():
        w(f"| {k} | `{h}` |" if h else f"| {k} | n/a |")
    w("")

    # 9.3.1
    w("## 9.3.1 Annotation and reliability")
    w("")
    w(f"Both raters completed {f(v1.get('case_count'))} cases; both exports passed validation "
      f"(A: {v1.get('validation', {}).get('A', {}).get('status')}, B: {v1.get('validation', {}).get('B', {}).get('status')}).")
    w("")
    for title, key in (("Applicability (YES / NO / UNCLEAR)", "applicability"),
                       ("Witness, where both raters judged the dimension applicable", "witness_where_both_applicable")):
        w(f"**{title}.** Agreement, Cohen's κ and Gwet's AC1 with 95% case-bootstrap intervals. Descriptive only.")
        w("")
        w("| Dim | n | Agreement | κ [95% CI] | AC1 [95% CI] |")
        w("|---|---|---|---|---|")
        for d in DIMS:
            r = rel.get(key, {}).get(d, {})
            w(f"| {d} | {f(r.get('n'))} | {f(r.get('agreement'), 3)} | {f(r.get('cohen_kappa'), 3)} "
              f"{iv(r.get('cohen_kappa_ci95_case_bootstrap'), 3)} | {f(r.get('gwet_ac1'), 3)} "
              f"{iv(r.get('gwet_ac1_ci95_case_bootstrap'), 3)} |")
        w("")
    unc = {}
    for d in DIMS:
        r = rel.get("applicability", {}).get(d, {})
        n = r.get("n") or 0
        unc[d] = {k: round(r.get(f"marginals_{k}", {}).get("UNCLEAR", 0) * n) for k in ("A", "B")}
    w("**UNCLEAR applicability labels** (per rater): " + "; ".join(f"{d} A {unc[d]['A']}, B {unc[d]['B']}" for d in DIMS) + ".")
    w("")
    xb, xm = rel.get("x_w_between_raters", {}), rel.get("x_w_missing", {})
    w(f"**Between-rater X_W:** Pearson r {f(xb.get('pearson_r'), 3)}, mean absolute difference "
      f"{f(xb.get('mean_abs_diff'), 3)}, exactly equal {f(xb.get('exact_equal_fraction'), 3)} "
      f"(n both defined {f(xb.get('n_both_defined'))}).")
    w(f"**Undefined combined X_W:** {f(xm.get('empty_denominator_or_undefined_combined'))}; one rater undefined "
      f"{f(xm.get('one_rater_undefined'))}; NO_USABLE_EVIDENCE among annotated cases {f(xm.get('no_usable_evidence'))}.")
    w("")

    # 9.3.2
    w("## 9.3.2 Cohort flow, primary population and outcome prevalence")
    w("")
    cf = res.get("cohort_flow", {})
    w("| Step | n |")
    w("|---|---|")
    w(f"| Frozen decisions | {f(cf.get('n_records'))} |")
    for k, n in sorted(cf.get("status_counts", {}).items()):
        w(f"| {k} | {f(n)} |")
    if av:
        w(f"| All decisions with NO_USABLE_EVIDENCE (evidence-availability audit) | {f(av['counts']['NO_USABLE_EVIDENCE'])} |")
    if rec:
        w(f"| Eligible primary decisions (EVALUABLE, usable evidence, Y_H defined) | {f(rec.get('n_eligible_primary'))} |")
        w(f"| Randomly sampled for annotation (seed {rec.get('seed')}) | {f(rec.get('n_sampled_primary'))} |")
        w(f"| Eligible but not sampled (X_W missing by design, MCAR) | {f(rec['n_eligible_primary'] - rec['n_sampled_primary'])} |")
        w(f"| E3/E4 with usable evidence added for S1/S2 | {f(rec.get('n_e3e4_added'))} |")
    w(f"| EVALUABLE with X_W missing (all reasons) | {f(cf.get('evaluable_xw_missing'))} |")
    w(f"| EVALUABLE with Y_H missing | {f(cf.get('evaluable_y_h_missing'))} |")
    p = pc.get("primary", {})
    w(f"| **Primary analysis population** | **{f(p.get('n'))}** |")
    if rec and p.get("n") is not None:
        w(f"| Sampled but X_W undefined (combined) | {f(rec['n_sampled_primary'] - p['n'])} |")
    w("")
    w(f"Primary population: {f(p.get('n'))} decisions in {f(p.get('n_groups'))} (database, question) groups; "
      f"harmful replacements Y_H = {f(p.get('events'))}, prevalence {f(p.get('prevalence'), 3)}.")
    rl = res.get("riley_2020", {})
    w(f"Riley et al. (2020) at the frozen planning values: criterion (i) needs n ≥ {f(rl.get('criterion_i_min_n'))} "
      f"(met: {rl.get('criterion_i_met')}); criterion (iii) needs n ≥ {f(rl.get('criterion_iii_min_n'))} "
      f"(met: {rl.get('criterion_iii_met')}); verdict `{rl.get('verdict')}`.")
    w("")

    completed = primary_v == "ANALYSIS_COMPLETED"
    # 9.3.3
    w("## 9.3.3 Primary estimand")
    w("")
    a0 = an.get("primary", {})
    if completed and a0:
        lo, hi = (a0.get("delta_logloss_repeat_percentile_interval_95") or [None, None])
        w(f"Δlog-loss (M0 − M1) = **{f(a0.get('delta_logloss'), 5)}**, 95% percentile interval over "
          f"{f(res.get('frozen_parameters', {}).get('n_repeats_used'))} repeats {iv([lo, hi], 5)}; "
          f"{f(a0.get('n_outer_predictions'))} outer predictions; convergence warnings {f(a0.get('convergence_warnings'))}.")
        w("")
        w(f"Positive values favour M1 (baseline + X_W). The repeat-level interval is {side(lo, hi)}. "
          f"It quantifies resampling instability across the {f(res.get('frozen_parameters', {}).get('n_repeats_used'))} repeated cross-validation splits, not a population "
          "confidence interval, and no significance threshold is frozen (protocol section 12).")
    else:
        w(f"Not estimated. Primary verdict `{primary_v}`: under the frozen hard stop no model is fitted and only "
          "descriptive results are reported.")
    w("")

    # 9.3.4
    w("## 9.3.4 Secondary measures (mean over repeats [2.5th, 97.5th percentile])")
    w("")
    if completed and a0:
        w("| Measure | M0 (baseline) | M1 (baseline + X_W) |")
        w("|---|---|---|")
        m0, m1 = a0.get("models", {}).get("M0", {}), a0.get("models", {}).get("M1", {})
        for label, k in (("Log loss", "logloss"), ("Brier score", "brier"), ("AUROC", "auroc"), ("AUPRC", "auprc"),
                         ("Calibration intercept", "calibration_intercept"), ("Calibration slope", "calibration_slope")):
            w(f"| {label} | {metric(m0.get(k))} | {metric(m1.get(k))} |")
        note = m1.get("calibration_sparse_event_note") or m0.get("calibration_sparse_event_note")
        if note:
            w("")
            w(f"Note: {note}")
    else:
        w("Not estimated (see 9.3.3).")
    w("")

    # 9.3.5
    w("## 9.3.5 Sensitivity analyses")
    w("")
    w("| Analysis | n | Events | Δlog-loss | 95% repeat interval | Status |")
    w("|---|---|---|---|---|---|")
    for k in ("primary",) + SENS:
        a, pp = an.get(k, {}), pc.get(k, {})
        w(f"| {k} | {f(pp.get('n'))} | {f(pp.get('events'))} | {f(a.get('delta_logloss'), 5)} | "
          f"{iv(a.get('delta_logloss_repeat_percentile_interval_95'), 5)} | {a.get('status', 'not run')} |")
    w("")
    if rob.get("rule"):
        w(f"Robustness flag `{rob.get('flag')}`: {rob['rule']}. Sign agreement can occur for a negligible "
          "effect, so the intervals are always read alongside it.")
    else:
        w(f"Robustness flag `{rob.get('flag', 'n/a')}`: the analyses were not run, so robustness cannot be assessed.")
    w("")

    # 9.3.6
    w("## 9.3.6 Systematic missingness (descriptive; no hypothesis test)")
    w("")
    ma = res.get("missingness_audit", {})
    w(f"Groups compared: {', '.join(ma.get('groups_compared', []))}; group sizes "
      + ", ".join(f"{k} {f(v)}" for k, v in ma.get("group_sizes", {}).items()) + ".")
    ql = ma.get("question_length_chars", {})
    if ql:
        w("")
        w("| Group | Question length median [q25, q75] |")
        w("|---|---|")
        for g, s in ql.items():
            w(f"| {g} | {f(s.get('median'), 1)} [{f(s.get('q25'), 1)}, {f(s.get('q75'), 1)}] |")
    for feat in ("reference_sql_hardness", "reference_sql_nesting_depth"):
        val = ma.get(feat)
        w("")
        if isinstance(val, dict):
            w(f"**{feat}** (proportions within group): " + json.dumps(val, sort_keys=True))
        else:
            w(f"**{feat}:** {val}")
    w("")
    if av:
        w("**Evidence availability (outcome-blind, not prespecified).** "
          f"{f(av['counts']['NO_USABLE_EVIDENCE'])} of {f(av['n_decisions'])} decisions "
          f"({100 * av['no_usable_evidence_fraction']:.1f}%) have no usable decision-time evidence and are "
          "outside the primary population by the frozen protocol (section 13).")
        h = av.get("reference_sql_hardness", {})
        if h:
            w("")
            w("| Reference-SQL hardness | Usable evidence | NO_USABLE_EVIDENCE |")
            w("|---|---|---|")
            for lvl in ("easy", "medium", "hard", "extra"):
                w(f"| {lvl} | {f(h['SUCCESS']['proportions'].get(lvl), 3)} | {f(h['NO_USABLE_EVIDENCE']['proportions'].get(lvl), 3)} |")
        w("")

    if av_note:
        w(av_note)
        w("")
    w("## Claim boundary")
    w("")
    w(CLAIM_BOUNDARY)
    w("")
    summary = {
        "test_or_synthetic": test,
        "primary_verdict": primary_v,
        "riley_verdict": verdicts.get("riley"),
        "robustness_flag": rob.get("flag"),
        "n_cases_annotated": v1.get("case_count"),
        "primary_population": p,
        "delta_logloss": {k: an.get(k, {}).get("delta_logloss") for k in ("primary",) + SENS},
        "delta_logloss_interval_95": {k: an.get(k, {}).get("delta_logloss_repeat_percentile_interval_95") for k in ("primary",) + SENS},
        "inputs_sha256": prov,
    }
    return "\n".join(L) + "\n", summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage1", type=Path, required=True)
    ap.add_argument("--stage2", type=Path, required=True)
    ap.add_argument("--evidence-availability", type=Path, default=None)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    md, summary = build(a.stage1, a.stage2, a.evidence_availability)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "P2_C1_4_FINDINGS.md").write_text(md, encoding="utf-8")
    (a.out / "P2_C1_4_FINDINGS.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("test_or_synthetic", "primary_verdict", "robustness_flag")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
