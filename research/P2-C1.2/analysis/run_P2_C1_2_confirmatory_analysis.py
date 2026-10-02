#!/usr/bin/env python3
"""P2-C1.2 / P2-C1.4 confirmatory incremental-validity analysis (M0 vs M1).

Implements, without modification, the frozen protocol
  research/methodological_gates/P2_C1_4_CONFIRMATORY_PROTOCOL_FREEZE_V1_2026-09-21.md (sections 4-13)
and the analysis sections of
  research/methodological_gates/P2_C1_4_MISSINGNESS_AND_ELIGIBILITY_AMENDMENT_2026-10-01.md
  (section 4: primary, S1, S2 bounds; section 5: systematic-missingness audit).

M0 = logistic(B), M1 = logistic(B + X_W); B = execution_ok, log1p(row_count), log1p(column_count).
Primary estimand: Delta_logloss = mean_i [LogLoss(y_i, p0_i) - LogLoss(y_i, p1_i)] over every outer
prediction of 20 repeats of 5-fold StratifiedGroupKFold (seeds 20261001..20261020), with C tuned by
inner 5-fold StratifiedGroupKFold inside each outer training fold. Positive = M1 better.

Every implementation choice not stated verbatim by the protocol is listed in IMPLEMENTATION_CHOICES
and copied into the results JSON; these require author approval before unblinding.

The script fails closed (exit code 2, no results written) on any input-integrity problem.
A mechanical fold-feasibility failure (FEASIBILITY_STOP) or a primary-population shortfall against
Riley et al. 2020 criteria (i)/(iii) (FEASIBILITY_STOP_RILEY) writes the verdict (exit code 3) and fits nothing.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import math
import os
import platform
import sys
import warnings
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import scipy
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

try:  # optional; used for calibration intercept/slope when present
    import statsmodels
    import statsmodels.api as sm

    HAVE_STATSMODELS = True
except Exception:  # pragma: no cover - depends on environment
    statsmodels = None
    sm = None
    HAVE_STATSMODELS = False

ANALYSIS_ID = "P2-C1.2-CONFIRMATORY-ANALYSIS-IMPL-V1"
PROTOCOL_ID = "P2-C1.4-CONFIRMATORY-V1-2026-09-21"
AMENDMENT_ID = "P2-C1.4-MISSINGNESS-AND-ELIGIBILITY-AMENDMENT-2026-10-01"
COHORT_PROTOCOL_VERSION = "P2-C1.4-ALIGNED-V2"

# ----------------------------------------------------------------------------------------------
# Frozen parameters (protocol sections 4, 8, 9, 10, 12). Do not edit.
# ----------------------------------------------------------------------------------------------
C_GRID: Tuple[float, ...] = (0.01, 0.1, 1.0, 10.0, 100.0)
OUTER_SPLITS = 5
INNER_SPLITS = 5
N_REPEATS_FROZEN = 20
OUTER_SEED_START = 20261001  # repeats use 20261001 .. 20261020
MAX_ITER = 2000
TOL = 1e-8
PROB_CLIP = 1e-15
INTERVAL_PERCENTILES = (2.5, 97.5)
# Riley et al. 2020 planning values (protocol section 4)
RILEY_N_PARAMETERS = 4
RILEY_SHRINKAGE = 0.90
RILEY_R2_FRACTION_OF_MAX = 0.15
RILEY_INTERCEPT_MARGIN = 0.05  # Riley criterion (iii): absolute margin of error delta = 0.05
RILEY_Z = 1.96

STATUS_EVALUABLE = "EVALUABLE"
STATUS_E1 = "EXCLUDED_E1_REFERENCE_NOT_SCOREABLE"
STATUS_E2 = "NON_EVALUABLE_E2_RUNTIME_FAILURE_PRE_EVIDENCE"
STATUS_E3E4 = "NON_EVALUABLE_E3E4_RUNTIME_FAILURE_POST_EVIDENCE"
ALL_STATUSES = (STATUS_EVALUABLE, STATUS_E1, STATUS_E2, STATUS_E3E4)

PROB_QUANTILES = (0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0)

EXIT_OK = 0
EXIT_INPUT_INVALID = 2
EXIT_FEASIBILITY_STOP = 3

IMPLEMENTATION_CHOICES: List[str] = [
    "IC01 Inner-CV seed: inner StratifiedGroupKFold(5, shuffle=True, random_state=outer_seed*10+outer_fold_index), outer_fold_index in 0..4.",
    "IC02 Tuning criterion (M0 and M1 identical): unweighted mean over the 5 inner validation folds of the per-fold mean per-case log loss (probabilities clipped to [1e-15, 1-1e-15]); the minimum wins; exact float ties go to the smaller C (grid scanned ascending, replace only on strictly smaller loss).",
    "IC03 After C selection the model is refit on the full outer training fold (log1p standardization re-fitted on that fold) and predicts the outer validation fold.",
    "IC04 Standardization of log1p(row_count) and log1p(column_count): mean and population SD (ddof=0) of the training fold; an SD of 0 is replaced by 1 (centering only). Fitted separately on every inner and outer training fold.",
    "IC05 X_W enters M1 raw (no transform, no standardization); the protocol specifies transforms only for row/column counts.",
    "IC06 Structurally missing row_count/column_count (null) are allowed only when execution_ok is false and are coded as 0 before log1p (log1p(0)=0), then standardized with the other training rows; execution_ok absorbs the structural-missingness level. Null counts with execution_ok true fail closed.",
    "IC07 L2 logistic regression via scikit-learn LogisticRegression(solver='lbfgs', C=C, l1_ratio=0.0 [== penalty='l2'; 'penalty' is deprecated in sklearn>=1.8], fit_intercept=True, max_iter=2000, tol=1e-8, class_weight=None). The lbfgs objective penalizes only the coefficient vector; the intercept is not penalized (sklearn LinearModelLoss.l2_penalty is applied to weights excluding the intercept).",
    "IC08 Feasibility (mechanical, protocol sections 4/9): before any fit, all 20x5 outer and 20x5x5 inner partitions are generated; FEASIBILITY_STOP if StratifiedGroupKFold raises, or any outer or inner training or validation fold contains zero events or zero non-events. Nothing is fitted after a primary FEASIBILITY_STOP.",
    "IC09 Riley et al. 2020 criteria (i) and (iii) are computed at the observed primary-population prevalence with 4 parameters, shrinkage 0.90, R2_CS = 0.15 * max R2_CS, intercept margin 0.05; HARD STOP (author decision 2026-10-02, amendment A4): if the primary population fails criterion (i) or (iii), or the criteria are not computable (prevalence 0 or 1), the verdict is FEASIBILITY_STOP_RILEY and no model is fitted for any population. The Riley check is applied to the primary population only.",
    "IC10 Delta_logloss = mean of all 20 x N paired per-case differences (equal to the mean of the 20 repeat-level means because every repeat predicts every case once). Interval = numpy.percentile(repeat_deltas, [2.5, 97.5], method='linear').",
    "IC11 Secondary metrics are computed per repeat on the pooled outer predictions of that repeat (N cases) and summarized as the mean and the 2.5/97.5 percentiles over repeats. AUROC/AUPRC (sklearn roc_auc_score / average_precision_score) are null if a repeat has only one class.",
    "IC12 Calibration per repeat on pooled outer predictions: slope = coefficient of logit(p) in an unpenalized logistic regression of y on [1, logit(p)]; intercept = calibration-in-the-large, the intercept of an unpenalized logistic regression of y on a constant with logit(p) as offset. statsmodels GLM(Binomial) is used when installed; otherwise slope via sklearn LogisticRegression(C=inf) and intercept via 1-D Newton-Raphson. The method used is recorded. Fit failures (e.g. separation) are recorded as null with the reason.",
    "IC13 Predicted-probability distribution: quantiles 0,1,5,10,25,50,75,90,95,99,100% and mean of all 20 x N outer predictions per model.",
    "IC14 Groups = (database_id, question) taken from decision_time_evidence, encoded as a JSON string; exact string identity.",
    "IC15 Sensitivity populations: S1 = primary + E3E4 records with x_w non-null and y_h_implied_by_definition == 0 (y=0); S2_low/S2_high = S1 + E3E4 records with p0_correct is true and x_w non-null, y=0 / y=1. Each population re-runs the identical procedure (same seeds, grid, derivation), with its own partitions; an infeasible sensitivity population is reported FEASIBILITY_STOP and robustness becomes NOT_ASSESSABLE.",
    "IC16 Robustness flag: ROBUST if Delta is strictly positive in all four analyses or strictly negative in all four; NOT_ROBUST otherwise; NOT_ASSESSABLE if any analysis could not be run. No significance threshold or decision rule on Delta is applied (none is frozen).",
    "IC17 Missingness audit compares status groups E2, E3E4 (combined) and EVALUABLE; E3 vs E4 are NOT separated because that requires p0_correct (an outcome field). Audit uses only record_status, decision_time_evidence.database_id, decision_time_evidence.question (character length, Python len) and the optional --reference-features CSV; descriptive only, no hypothesis test (none is frozen).",
    "IC18 Input integrity (fail closed): cohort protocol_version must be P2-C1.4-ALIGNED-V2; unique decision_ids; X_W decision_id set identical to the cohort's; x_w finite numeric in [0,1] or null; E1/E2 records must have null x_w; y_h in {0,1,null}; E3E4 records must have null y_h, y_h_implied_by_definition 0 iff p0_correct is false.",
    "IC19 Convergence warnings from lbfgs are counted and reported per analysis, not treated as failures.",
    "IC20 --sha-check COHORT_SHA256 XW_SHA256 (optional): fail closed if the inputs do not match the expected hashes. SHA-256 of every input file is always recorded.",
    "IC21 Exit codes: 0 analysis completed; 2 input invalid (no results written); 3 FEASIBILITY_STOP or FEASIBILITY_STOP_RILEY (verdict written, nothing fitted).",
]


class InputError(Exception):
    """Raised for any input-integrity failure (fail closed)."""


# ----------------------------------------------------------------------------------------------
# Hashing / IO helpers
# ----------------------------------------------------------------------------------------------
def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read JSON {path}: {exc}") from exc


def _fnum(x: Optional[float]) -> Optional[float]:
    if x is None:
        return None
    x = float(x)
    if not math.isfinite(x):
        return None
    return x


# ----------------------------------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------------------------------
def validate_inputs(cohort: Any, xw: Any) -> Tuple[List[dict], Dict[str, Optional[float]]]:
    if not isinstance(cohort, dict) or "records" not in cohort:
        raise InputError("cohort must be an object with 'records'")
    if cohort.get("protocol_version") != COHORT_PROTOCOL_VERSION:
        raise InputError(f"cohort protocol_version must be {COHORT_PROTOCOL_VERSION}")
    records = cohort["records"]
    if not isinstance(records, list) or not records:
        raise InputError("cohort records must be a non-empty list")
    if not isinstance(xw, dict) or "records" not in xw or "xw_construction_version" not in xw:
        raise InputError("xw must be an object with 'xw_construction_version' and 'records'")
    if not isinstance(xw["xw_construction_version"], str) or not xw["xw_construction_version"]:
        raise InputError("xw_construction_version must be a non-empty string")

    ids: List[str] = []
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            raise InputError(f"cohort record {i} is not an object")
        did = r.get("decision_id")
        if not isinstance(did, str) or not did:
            raise InputError(f"cohort record {i} has invalid decision_id")
        st = r.get("record_status")
        if st not in ALL_STATUSES:
            raise InputError(f"{did}: invalid record_status {st!r}")
        for key in ("baseline", "decision_time_evidence", "intervention_outcome"):
            if not isinstance(r.get(key), dict):
                raise InputError(f"{did}: missing object {key}")
        ev = r["decision_time_evidence"]
        if not isinstance(ev.get("question"), str) or not ev["question"]:
            raise InputError(f"{did}: decision_time_evidence.question missing")
        if not isinstance(ev.get("database_id"), str) or not ev["database_id"]:
            raise InputError(f"{did}: decision_time_evidence.database_id missing")
        ids.append(did)
    if len(set(ids)) != len(ids):
        raise InputError("duplicate decision_id in cohort")

    xw_map: Dict[str, Optional[float]] = {}
    xrecs = xw["records"]
    if not isinstance(xrecs, list):
        raise InputError("xw records must be a list")
    for j, e in enumerate(xrecs):
        if not isinstance(e, dict) or not isinstance(e.get("decision_id"), str):
            raise InputError(f"xw record {j} invalid")
        did = e["decision_id"]
        if did in xw_map:
            raise InputError(f"duplicate decision_id in xw: {did}")
        if "x_w" not in e:
            raise InputError(f"xw record {did} lacks x_w")
        v = e["x_w"]
        if v is None:
            xw_map[did] = None
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise InputError(f"x_w for {did} is not numeric: {v!r}")
        v = float(v)
        if not math.isfinite(v) or v < 0.0 or v > 1.0:
            raise InputError(f"x_w for {did} out of range [0,1]: {v!r}")
        xw_map[did] = v
    if set(xw_map) != set(ids):
        missing = sorted(set(ids) - set(xw_map))[:5]
        extra = sorted(set(xw_map) - set(ids))[:5]
        raise InputError(f"decision_id sets differ between cohort and xw (missing in xw e.g. {missing}; extra in xw e.g. {extra})")

    for r in records:
        did, st = r["decision_id"], r["record_status"]
        b, io = r["baseline"], r["intervention_outcome"]
        if st in (STATUS_E1, STATUS_E2) and xw_map[did] is not None:
            raise InputError(f"{did}: {st} record must have null x_w (no usable evidence)")
        yh = io.get("y_h")
        if yh is not None and (isinstance(yh, bool) or yh not in (0, 1)):
            raise InputError(f"{did}: y_h must be 0, 1 or null")
        imp = io.get("y_h_implied_by_definition")
        if imp is not None and (isinstance(imp, bool) or imp != 0):
            raise InputError(f"{did}: y_h_implied_by_definition must be 0 or null")
        if st == STATUS_E3E4:
            if yh is not None:
                raise InputError(f"{did}: E3E4 record must have null y_h")
            p0 = io.get("p0_correct")
            if not isinstance(p0, bool):
                raise InputError(f"{did}: E3E4 record must have boolean p0_correct")
            if (p0 is False) != (imp == 0):
                raise InputError(f"{did}: y_h_implied_by_definition inconsistent with p0_correct")
        elif imp is not None:
            raise InputError(f"{did}: y_h_implied_by_definition set on non-E3E4 record")
        if st == STATUS_EVALUABLE:
            eo = b.get("execution_ok")
            if not isinstance(eo, bool):
                raise InputError(f"{did}: baseline.execution_ok must be boolean")
            for k in ("row_count", "column_count"):
                v = b.get(k)
                if v is None:
                    if eo:
                        raise InputError(f"{did}: baseline.{k} null with execution_ok true")
                elif isinstance(v, bool) or not isinstance(v, int) or v < 0:
                    raise InputError(f"{did}: baseline.{k} must be a non-negative integer or null")
    return records, xw_map


def _baseline_row(r: dict) -> Tuple[float, float, float]:
    b = r["baseline"]
    eo = b.get("execution_ok")
    if not isinstance(eo, bool):
        raise InputError(f"{r['decision_id']}: baseline.execution_ok must be boolean")
    vals = []
    for k in ("row_count", "column_count"):
        v = b.get(k)
        if v is None:
            if eo:
                raise InputError(f"{r['decision_id']}: baseline.{k} null with execution_ok true")
            v = 0  # IC06 structural missingness
        elif isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise InputError(f"{r['decision_id']}: baseline.{k} invalid")
        vals.append(math.log1p(v))
    return (1.0 if eo else 0.0, vals[0], vals[1])


def group_key(r: dict) -> str:
    ev = r["decision_time_evidence"]
    return json.dumps([ev["database_id"], ev["question"]], ensure_ascii=False)


# ----------------------------------------------------------------------------------------------
# Populations
# ----------------------------------------------------------------------------------------------
class Population:
    def __init__(self, name: str, ids: List[str], X_base: np.ndarray, xw: np.ndarray, y: np.ndarray, groups: np.ndarray):
        self.name = name
        self.ids = ids
        self.X_base = X_base  # columns: execution_ok, log1p(row_count), log1p(column_count)
        self.xw = xw
        self.y = y.astype(int)
        self.groups = groups

    @property
    def n(self) -> int:
        return len(self.ids)

    def counts(self) -> dict:
        ev = int(self.y.sum())
        gw_event = len(set(self.groups[self.y == 1].tolist()))
        return {
            "n": self.n,
            "events": ev,
            "non_events": int(self.n - ev),
            "prevalence": _fnum(ev / self.n) if self.n else None,
            "n_groups": int(len(set(self.groups.tolist()))),
            "n_groups_with_event": int(gw_event),
        }


def _make_population(name: str, items: List[Tuple[dict, int]], xw_map: Dict[str, Optional[float]]) -> Population:
    ids, Xb, xv, ys, gs = [], [], [], [], []
    for r, y in items:
        ids.append(r["decision_id"])
        Xb.append(_baseline_row(r))
        xv.append(xw_map[r["decision_id"]])
        ys.append(int(y))
        gs.append(group_key(r))
    return Population(
        name,
        ids,
        np.asarray(Xb, dtype=float).reshape(-1, 3),
        np.asarray(xv, dtype=float),
        np.asarray(ys, dtype=int),
        np.asarray(gs, dtype=object),
    )


def build_populations(records: List[dict], xw_map: Dict[str, Optional[float]]) -> Tuple[Dict[str, Population], dict]:
    primary: List[Tuple[dict, int]] = []
    e3: List[Tuple[dict, int]] = []
    e4: List[dict] = []
    flow = {
        "evaluable_xw_missing": 0,
        "evaluable_y_h_missing": 0,
        "e3e4_xw_missing": 0,
        "e3_with_xw": 0,
        "e4_with_xw": 0,
    }
    for r in records:  # frozen cohort order is preserved
        st = r["record_status"]
        io = r["intervention_outcome"]
        x = xw_map[r["decision_id"]]
        if st == STATUS_EVALUABLE:
            if x is None:
                flow["evaluable_xw_missing"] += 1
                continue
            if io.get("y_h") is None:
                flow["evaluable_y_h_missing"] += 1
                continue
            primary.append((r, int(io["y_h"])))
        elif st == STATUS_E3E4:
            if x is None:
                flow["e3e4_xw_missing"] += 1
                continue
            if io.get("y_h_implied_by_definition") == 0:
                e3.append((r, 0))
                flow["e3_with_xw"] += 1
            elif io.get("p0_correct") is True:
                e4.append(r)
                flow["e4_with_xw"] += 1
    s1 = primary + e3
    pops = {
        "primary": _make_population("primary", primary, xw_map),
        "S1": _make_population("S1", s1, xw_map),
        "S2_low": _make_population("S2_low", s1 + [(r, 0) for r in e4], xw_map),
        "S2_high": _make_population("S2_high", s1 + [(r, 1) for r in e4], xw_map),
    }
    return pops, flow


def status_counts(records: List[dict]) -> Dict[str, int]:
    out = {s: 0 for s in ALL_STATUSES}
    for r in records:
        out[r["record_status"]] += 1
    return out


# ----------------------------------------------------------------------------------------------
# Partitions and feasibility gate
# ----------------------------------------------------------------------------------------------
def outer_seeds(n_repeats: int) -> List[int]:
    return [OUTER_SEED_START + k for k in range(n_repeats)]


def inner_seed(outer_seed: int, fold_index: int) -> int:
    return outer_seed * 10 + fold_index  # IC01


def _sgkf_split(n_splits: int, seed: int, y: np.ndarray, groups: np.ndarray) -> List[Tuple[np.ndarray, np.ndarray]]:
    cv = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    dummy = np.zeros((len(y), 1))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # class-count warnings; feasibility is checked explicitly
        return [(np.asarray(tr), np.asarray(te)) for tr, te in cv.split(dummy, y, groups)]


def _both_classes(y: np.ndarray) -> bool:
    return bool(y.size) and 0 < int(y.sum()) < y.size


def build_partitions(pop: Population, n_repeats: int) -> Tuple[Optional[list], Optional[str]]:
    """Generate all outer/inner partitions; return (plan, None) or (None, reason) without fitting anything."""
    plan = []
    y, g = pop.y, pop.groups
    if pop.n == 0:
        return None, "empty population"
    for r_i, seed in enumerate(outer_seeds(n_repeats)):
        try:
            outer = _sgkf_split(OUTER_SPLITS, seed, y, g)
        except ValueError as exc:
            return None, f"repeat {r_i} (seed {seed}): outer StratifiedGroupKFold raised: {exc}"
        rep = []
        for f_i, (tr, te) in enumerate(outer):
            if not _both_classes(y[tr]):
                return None, f"repeat {r_i} (seed {seed}) outer fold {f_i}: training fold lacks events or non-events"
            if not _both_classes(y[te]):
                return None, f"repeat {r_i} (seed {seed}) outer fold {f_i}: validation fold lacks events or non-events"
            iseed = inner_seed(seed, f_i)
            try:
                inner = _sgkf_split(INNER_SPLITS, iseed, y[tr], g[tr])
            except ValueError as exc:
                return None, f"repeat {r_i} outer fold {f_i} (inner seed {iseed}): inner StratifiedGroupKFold raised: {exc}"
            inner_abs = []
            for k_i, (itr, ite) in enumerate(inner):
                if not _both_classes(y[tr][itr]) or not _both_classes(y[tr][ite]):
                    return None, f"repeat {r_i} outer fold {f_i} inner fold {k_i}: training or validation fold lacks events or non-events"
                inner_abs.append((tr[itr], tr[ite]))
            rep.append({"train": tr, "test": te, "inner": inner_abs, "inner_seed": iseed})
        plan.append({"seed": seed, "folds": rep})
    return plan, None


# ----------------------------------------------------------------------------------------------
# Riley et al. 2020
# ----------------------------------------------------------------------------------------------
def riley_quantities(n: int, events: int) -> dict:
    out: Dict[str, Any] = {
        "n_parameters": RILEY_N_PARAMETERS,
        "shrinkage_target": RILEY_SHRINKAGE,
        "r2cs_fraction_of_max": RILEY_R2_FRACTION_OF_MAX,
        "intercept_margin_delta": RILEY_INTERCEPT_MARGIN,
        "realized_n": n,
        "realized_events": events,
    }
    if n == 0 or events == 0 or events == n:
        out.update({"computable": False, "reason": "prevalence is 0 or 1", "verdict": "RILEY_CRITERIA_NOT_MET"})
        return out
    phi = events / n
    ln_lnull_per_n = phi * math.log(phi) + (1 - phi) * math.log(1 - phi)
    max_r2 = 1.0 - math.exp(2.0 * ln_lnull_per_n)
    r2cs = RILEY_R2_FRACTION_OF_MAX * max_r2
    n_i = RILEY_N_PARAMETERS / ((RILEY_SHRINKAGE - 1.0) * math.log(1.0 - r2cs / RILEY_SHRINKAGE))
    n_iii = (RILEY_Z / RILEY_INTERCEPT_MARGIN) ** 2 * phi * (1 - phi)
    n_i_c, n_iii_c = int(math.ceil(n_i)), int(math.ceil(n_iii))
    meets_i, meets_iii = n >= n_i_c, n >= n_iii_c
    out.update(
        {
            "computable": True,
            "observed_prevalence": phi,
            "max_r2cs": max_r2,
            "anticipated_r2cs": r2cs,
            "criterion_i_min_n": n_i_c,
            "criterion_i_min_n_unrounded": n_i,
            "criterion_i_min_events": int(math.ceil(n_i_c * phi)),
            "criterion_i_met": bool(meets_i),
            "criterion_iii_min_n": n_iii_c,
            "criterion_iii_min_n_unrounded": n_iii,
            "criterion_iii_met": bool(meets_iii),
            "verdict": "RILEY_CRITERIA_MET" if (meets_i and meets_iii) else "RILEY_CRITERIA_NOT_MET",
        }
    )
    return out


# ----------------------------------------------------------------------------------------------
# Modeling
# ----------------------------------------------------------------------------------------------
def _sklearn_ge_18() -> bool:
    parts = sklearn.__version__.split(".")
    try:
        return (int(parts[0]), int(parts[1])) >= (1, 8)
    except ValueError:  # pragma: no cover
        return True


def make_logreg(C: float) -> LogisticRegression:
    kw = dict(C=C, solver="lbfgs", max_iter=MAX_ITER, tol=TOL, fit_intercept=True, class_weight=None)
    if _sklearn_ge_18():
        return LogisticRegression(l1_ratio=0.0, **kw)  # == L2 penalty (IC07)
    return LogisticRegression(penalty="l2", **kw)  # pragma: no cover


def _design(pop: Population, idx: np.ndarray, mean: np.ndarray, sd: np.ndarray, with_xw: bool) -> np.ndarray:
    Xb = pop.X_base[idx]
    cols = [Xb[:, 0:1], (Xb[:, 1:3] - mean) / sd]
    if with_xw:
        cols.append(pop.xw[idx].reshape(-1, 1))
    return np.hstack(cols)


def _scaler(pop: Population, train_idx: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    Z = pop.X_base[train_idx, 1:3]
    mean = Z.mean(axis=0)
    sd = Z.std(axis=0, ddof=0)
    sd = np.where(sd > 0, sd, 1.0)  # IC04
    return mean, sd


def fit_predict(pop: Population, train_idx: np.ndarray, test_idx: np.ndarray, C: float, with_xw: bool, warn_counter: List[int]) -> np.ndarray:
    mean, sd = _scaler(pop, train_idx)
    Xtr = _design(pop, train_idx, mean, sd, with_xw)
    Xte = _design(pop, test_idx, mean, sd, with_xw)
    model = make_logreg(C)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(Xtr, pop.y[train_idx])
    warn_counter[0] += sum(1 for w in caught if issubclass(w.category, ConvergenceWarning))
    return model.predict_proba(Xte)[:, 1]


def per_case_logloss(y: np.ndarray, p: np.ndarray) -> np.ndarray:
    pc = np.clip(p, PROB_CLIP, 1.0 - PROB_CLIP)
    return -(y * np.log(pc) + (1 - y) * np.log(1.0 - pc))


def select_C(pop: Population, inner: list, with_xw: bool, warn_counter: List[int]) -> Tuple[float, List[float]]:
    losses = []
    for C in C_GRID:
        fold_means = []
        for itr, ite in inner:
            p = fit_predict(pop, itr, ite, C, with_xw, warn_counter)
            fold_means.append(float(np.mean(per_case_logloss(pop.y[ite], p))))
        losses.append(float(np.mean(fold_means)))
    best_i = 0
    for i in range(1, len(C_GRID)):  # IC02: ascending scan, strict improvement only
        if losses[i] < losses[best_i]:
            best_i = i
    return C_GRID[best_i], losses


# ----------------------------------------------------------------------------------------------
# Secondary metrics
# ----------------------------------------------------------------------------------------------
def _logit(p: np.ndarray) -> np.ndarray:
    pc = np.clip(p, PROB_CLIP, 1.0 - PROB_CLIP)
    return np.log(pc) - np.log1p(-pc)


def calibration(y: np.ndarray, p: np.ndarray) -> dict:
    lp = _logit(p)
    out: Dict[str, Any] = {"method": "statsmodels_GLM_binomial" if HAVE_STATSMODELS else "sklearn_unpenalized_slope+newton_offset_intercept"}
    if not _both_classes(y):
        out.update({"slope": None, "intercept": None, "error": "single class"})
        return out
    try:
        if HAVE_STATSMODELS:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                r_s = sm.GLM(y, sm.add_constant(lp, has_constant="add"), family=sm.families.Binomial()).fit()
                r_i = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial(), offset=lp).fit()
            slope, intercept = float(r_s.params[1]), float(r_i.params[0])
        else:  # pragma: no cover - exercised only without statsmodels
            m = LogisticRegression(C=np.inf, solver="lbfgs", max_iter=MAX_ITER, tol=TOL).fit(lp.reshape(-1, 1), y)
            slope = float(m.coef_[0, 0])
            a = 0.0
            for _ in range(100):
                pi = 1.0 / (1.0 + np.exp(-(a + lp)))
                g = float(np.sum(y - pi))
                h = float(np.sum(pi * (1 - pi)))
                step = g / h
                a += step
                if abs(step) < 1e-12:
                    break
            intercept = a
        out.update({"slope": _fnum(slope), "intercept": _fnum(intercept), "error": None})
    except Exception as exc:  # separation, non-convergence, etc.
        out.update({"slope": None, "intercept": None, "error": f"{type(exc).__name__}: {exc}"})
    return out


def repeat_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    two = _both_classes(y)
    return {
        "logloss": float(np.mean(per_case_logloss(y, p))),
        "brier": float(np.mean((p - y) ** 2)),
        "auroc": float(roc_auc_score(y, p)) if two else None,
        "auprc": float(average_precision_score(y, p)) if two else None,
        "calibration": calibration(y, p),
    }


def _summ(values: Sequence[Optional[float]]) -> dict:
    v = np.asarray([x for x in values if x is not None], dtype=float)
    if v.size == 0:
        return {"mean": None, "p2_5": None, "p97_5": None, "n_repeats_defined": 0}
    lo, hi = np.percentile(v, INTERVAL_PERCENTILES, method="linear")
    return {"mean": float(v.mean()), "p2_5": float(lo), "p97_5": float(hi), "n_repeats_defined": int(v.size)}


# ----------------------------------------------------------------------------------------------
# Analysis of one population
# ----------------------------------------------------------------------------------------------
def analyze_population(pop: Population, plan: list) -> Tuple[dict, List[tuple]]:
    warn = [0]
    rows: List[tuple] = []
    repeat_deltas: List[float] = []
    all_d: List[np.ndarray] = []
    rep_metrics = {"M0": [], "M1": []}
    all_p = {"M0": [], "M1": []}
    selected = {"M0": [], "M1": []}
    for r_i, rep in enumerate(plan):
        p0_full = np.full(pop.n, np.nan)
        p1_full = np.full(pop.n, np.nan)
        for f_i, fold in enumerate(rep["folds"]):
            tr, te = fold["train"], fold["test"]
            C0, loss0 = select_C(pop, fold["inner"], False, warn)
            C1, loss1 = select_C(pop, fold["inner"], True, warn)
            selected["M0"].append({"repeat": r_i, "fold": f_i, "C": C0, "inner_mean_logloss": loss0})
            selected["M1"].append({"repeat": r_i, "fold": f_i, "C": C1, "inner_mean_logloss": loss1})
            p0 = fit_predict(pop, tr, te, C0, False, warn)
            p1 = fit_predict(pop, tr, te, C1, True, warn)
            p0_full[te], p1_full[te] = p0, p1
            yv = pop.y[te]
            d = per_case_logloss(yv, p0) - per_case_logloss(yv, p1)
            for j, idx in enumerate(te):
                rows.append((r_i, f_i, pop.ids[idx], int(yv[j]), float(p0[j]), float(p1[j]), float(d[j])))
        if np.isnan(p0_full).any() or np.isnan(p1_full).any():
            raise RuntimeError("outer folds did not cover every case exactly once")
        d_rep = per_case_logloss(pop.y, p0_full) - per_case_logloss(pop.y, p1_full)
        all_d.append(d_rep)
        repeat_deltas.append(float(np.mean(d_rep)))
        for m, p in (("M0", p0_full), ("M1", p1_full)):
            rep_metrics[m].append(repeat_metrics(pop.y, p))
            all_p[m].append(p)
    d_all = np.concatenate(all_d)
    lo, hi = np.percentile(np.asarray(repeat_deltas), INTERVAL_PERCENTILES, method="linear")
    models = {}
    for m in ("M0", "M1"):
        pm = np.concatenate(all_p[m])
        q = np.quantile(pm, PROB_QUANTILES, method="linear")
        cs = [x["C"] for x in selected[m]]
        models[m] = {
            "per_repeat": rep_metrics[m],
            "logloss": _summ([x["logloss"] for x in rep_metrics[m]]),
            "brier": _summ([x["brier"] for x in rep_metrics[m]]),
            "auroc": _summ([x["auroc"] for x in rep_metrics[m]]),
            "auprc": _summ([x["auprc"] for x in rep_metrics[m]]),
            "calibration_slope": _summ([x["calibration"]["slope"] for x in rep_metrics[m]]),
            "calibration_intercept": _summ([x["calibration"]["intercept"] for x in rep_metrics[m]]),
            "calibration_sparse_event_note": f"{int(pop.y.sum())} events per repeat; calibration estimates are unstable with few events and must not be over-interpreted.",
            "predicted_probability_distribution": {
                "quantiles": {f"q{qq:g}": float(v) for qq, v in zip(PROB_QUANTILES, q)},
                "mean": float(pm.mean()),
                "n_predictions": int(pm.size),
            },
            "selected_C": selected[m],
            "selected_C_counts": {repr(c): int(sum(1 for x in cs if x == c)) for c in C_GRID},
        }
    res = {
        "status": "COMPLETED",
        "delta_logloss": float(np.mean(d_all)),
        "delta_logloss_by_repeat": repeat_deltas,
        "delta_logloss_repeat_percentile_interval_95": [float(lo), float(hi)],
        "interval_note": "2.5th/97.5th percentile of the repeat-level estimates; quantifies resampling instability, not a population-level confidence interval (protocol section 12).",
        "n_outer_predictions": int(d_all.size),
        "models": models,
        "convergence_warnings": int(warn[0]),
        "partitions": [{"repeat": i, "outer_seed": rep["seed"], "inner_seeds": [f["inner_seed"] for f in rep["folds"]], "outer_validation_sizes": [int(len(f["test"])) for f in rep["folds"]], "outer_validation_events": [int(pop.y[f["test"]].sum()) for f in rep["folds"]]} for i, rep in enumerate(plan)],
    }
    return res, rows


# ----------------------------------------------------------------------------------------------
# Systematic-missingness audit (amendment section 5) -- pre-outcome fields only
# ----------------------------------------------------------------------------------------------
AUDIT_GROUPS = {STATUS_EVALUABLE: "EVALUABLE", STATUS_E2: "E2", STATUS_E3E4: "E3E4"}


def pre_outcome_projection(records: List[dict]) -> List[dict]:
    """The ONLY view of the cohort the audit receives: no intervention_outcome, no baseline."""
    out = []
    for r in records:
        ev = r["decision_time_evidence"]
        out.append({"decision_id": r["decision_id"], "record_status": r["record_status"], "database_id": ev["database_id"], "question": ev["question"]})
    return out


def load_reference_features(path: str) -> Dict[str, dict]:
    feats: Dict[str, dict] = {}
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            rd = csv.DictReader(fh)
            need = {"decision_id", "hardness", "nesting_depth"}
            if rd.fieldnames is None or not need.issubset(rd.fieldnames):
                raise InputError(f"reference-features CSV must have columns {sorted(need)}")
            for row in rd:
                did = row["decision_id"]
                if did in feats:
                    raise InputError(f"duplicate decision_id in reference-features: {did}")
                try:
                    nd = int(row["nesting_depth"])
                except ValueError as exc:
                    raise InputError(f"nesting_depth not an integer for {did}") from exc
                feats[did] = {"hardness": row["hardness"], "nesting_depth": nd}
    except OSError as exc:
        raise InputError(f"cannot read reference-features: {exc}") from exc
    return feats


def _num_summary(v: List[float]) -> dict:
    if not v:
        return {"n": 0}
    a = np.asarray(v, dtype=float)
    q = np.quantile(a, [0.0, 0.25, 0.5, 0.75, 1.0], method="linear")
    return {"n": int(a.size), "mean": float(a.mean()), "sd": float(a.std(ddof=1)) if a.size > 1 else None, "min": float(q[0]), "q25": float(q[1]), "median": float(q[2]), "q75": float(q[3]), "max": float(q[4])}


def missingness_audit(projection: List[dict], ref_feats: Optional[Dict[str, dict]]) -> dict:
    groups = {g: [p for p in projection if p["record_status"] == s] for s, g in AUDIT_GROUPS.items()}
    dbs = sorted({p["database_id"] for p in projection if p["record_status"] in AUDIT_GROUPS})
    db_table = {db: {g: sum(1 for p in groups[g] if p["database_id"] == db) for g in groups} for db in dbs}
    qlen = {g: _num_summary([float(len(p["question"])) for p in groups[g]]) for g in groups}
    audit: Dict[str, Any] = {
        "groups_compared": sorted(groups),
        "group_sizes": {g: len(v) for g, v in groups.items()},
        "fields_used": ["record_status", "decision_time_evidence.database_id", "decision_time_evidence.question", "reference_features.hardness", "reference_features.nesting_depth"],
        "outcome_fields_used": [],
        "e3_e4_split": "NOT_COMPUTED_REQUIRES_OUTCOME_FIELD_p0_correct",
        "database_counts": db_table,
        "question_length_chars": qlen,
        "test": "descriptive only; no hypothesis test is frozen",
    }
    if ref_feats is None:
        audit["reference_sql_hardness"] = "NOT_COMPUTED_INPUT_MISSING"
        audit["reference_sql_nesting_depth"] = "NOT_COMPUTED_INPUT_MISSING"
    else:
        levels = sorted({f["hardness"] for f in ref_feats.values()})
        hard, nest, missing = {}, {}, {}
        for g, items in groups.items():
            fs = [ref_feats.get(p["decision_id"]) for p in items]
            missing[g] = sum(1 for f in fs if f is None)
            hard[g] = {lv: sum(1 for f in fs if f is not None and f["hardness"] == lv) for lv in levels}
            nest[g] = _num_summary([float(f["nesting_depth"]) for f in fs if f is not None])
        audit["reference_sql_hardness"] = hard
        audit["reference_sql_nesting_depth"] = nest
        audit["reference_features_missing_per_group"] = missing
    return audit


# ----------------------------------------------------------------------------------------------
# Orchestration
# ----------------------------------------------------------------------------------------------
def package_versions() -> dict:
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scikit-learn": sklearn.__version__,
        "statsmodels": statsmodels.__version__ if HAVE_STATSMODELS else None,
    }


def robustness(analyses: Dict[str, dict]) -> dict:
    names = ["primary", "S1", "S2_low", "S2_high"]
    deltas = {n: analyses[n].get("delta_logloss") if analyses[n].get("status") == "COMPLETED" else None for n in names}
    if any(v is None for v in deltas.values()):
        flag = "NOT_ASSESSABLE"
    else:
        signs = {int(np.sign(v)) for v in deltas.values()}
        flag = "ROBUST" if (len(signs) == 1 and 0 not in signs) else "NOT_ROBUST"
    return {"flag": flag, "deltas": deltas, "rule": "sign of Delta_logloss agrees (strictly) across primary, S1, S2_low, S2_high (amendment section 4)"}


def run(cohort_path: str, xw_path: str, out_dir: str, n_repeats: int, test_mode: bool, ref_path: Optional[str] = None, sha_expected: Optional[Sequence[str]] = None) -> int:
    hashes = {"cohort_sha256": sha256_file(cohort_path), "xw_sha256": sha256_file(xw_path)}
    if ref_path:
        hashes["reference_features_sha256"] = sha256_file(ref_path)
    if sha_expected is not None:
        exp_c, exp_x = (s.lower() for s in sha_expected)
        if exp_c != hashes["cohort_sha256"] or exp_x != hashes["xw_sha256"]:
            raise InputError(f"--sha-check mismatch: got cohort={hashes['cohort_sha256']} xw={hashes['xw_sha256']}")
    cohort = _load_json(cohort_path)
    xw = _load_json(xw_path)
    records, xw_map = validate_inputs(cohort, xw)
    ref_feats = load_reference_features(ref_path) if ref_path else None
    pops, flow = build_populations(records, xw_map)

    results: Dict[str, Any] = {
        "analysis_id": ANALYSIS_ID,
        "protocol_id": PROTOCOL_ID,
        "amendment_id": AMENDMENT_ID,
        "test_mode": bool(test_mode),
        "input_marked_synthetic": bool(cohort.get("SYNTHETIC") is True or xw.get("SYNTHETIC") is True),
        "inputs": {"cohort_file": os.path.basename(cohort_path), "xw_file": os.path.basename(xw_path), "reference_features_file": os.path.basename(ref_path) if ref_path else None, "xw_construction_version": xw["xw_construction_version"], **hashes},
        "package_versions": package_versions(),
        "frozen_parameters": {
            "C_grid": list(C_GRID),
            "outer_splits": OUTER_SPLITS,
            "inner_splits": INNER_SPLITS,
            "n_repeats_frozen": N_REPEATS_FROZEN,
            "n_repeats_used": n_repeats,
            "outer_seeds": outer_seeds(n_repeats),
            "inner_seed_rule": "outer_seed*10 + outer_fold_index",
            "solver": "lbfgs",
            "penalty": "l2",
            "max_iter": MAX_ITER,
            "tol": TOL,
            "fit_intercept": True,
            "class_weight": None,
            "probability_clip": PROB_CLIP,
            "tuning_criterion": "mean inner-validation log loss; ties -> smaller C",
            "baseline_features": ["execution_ok", "z(log1p(row_count))", "z(log1p(column_count))"],
            "xw_transform": "none (raw)",
            "groups": "(database_id, question)",
        },
        "implementation_choices_requiring_author_approval": IMPLEMENTATION_CHOICES,
        "cohort_flow": {"n_records": len(records), "status_counts": status_counts(records), **flow},
        "population_counts": {k: p.counts() for k, p in pops.items()},
        "riley_2020": riley_quantities(pops["primary"].n, int(pops["primary"].y.sum())),
        "missingness_audit": missingness_audit(pre_outcome_projection(records), ref_feats),
    }

    plans: Dict[str, Optional[list]] = {}
    reasons: Dict[str, Optional[str]] = {}
    for name, pop in pops.items():
        plans[name], reasons[name] = build_partitions(pop, n_repeats)
    feas = {name: ("FEASIBLE" if plans[name] is not None else "FEASIBILITY_STOP") for name in pops}
    riley_ok = results["riley_2020"]["verdict"] == "RILEY_CRITERIA_MET"
    results["feasibility"] = {"per_population": feas, "reasons": reasons, "rule": IMPLEMENTATION_CHOICES[7], "riley_stop_rule": IMPLEMENTATION_CHOICES[8], "riley_primary_met": riley_ok}

    os.makedirs(out_dir, exist_ok=True)
    analyses: Dict[str, dict] = {}
    if plans["primary"] is None:
        for name in pops:
            analyses[name] = {"status": "NOT_RUN_PRIMARY_FEASIBILITY_STOP"}
        verdict_primary = "FEASIBILITY_STOP"
    elif not riley_ok:
        for name in pops:
            analyses[name] = {"status": "NOT_RUN_RILEY_STOP"}
        verdict_primary = "FEASIBILITY_STOP_RILEY"
    else:
        verdict_primary = "ANALYSIS_COMPLETED"
        for name, pop in pops.items():
            if plans[name] is None:
                analyses[name] = {"status": "FEASIBILITY_STOP", "reason": reasons[name]}
                continue
            res, rows = analyze_population(pop, plans[name])
            analyses[name] = res
            _write_csv(os.path.join(out_dir, f"per_case_logloss_differences_{name}.csv"), rows)
    results["analyses"] = analyses
    results["verdicts"] = {
        "primary": verdict_primary,
        "riley": results["riley_2020"]["verdict"],
        "robustness": robustness(analyses) if verdict_primary == "ANALYSIS_COMPLETED" else {"flag": "NOT_ASSESSABLE"},
        "inferential_decision_rule": "none frozen; Delta_logloss and its repeat-level interval are reported without a significance verdict",
    }

    blob = json.dumps(results, sort_keys=True, indent=2, allow_nan=False, ensure_ascii=True) + "\n"
    with open(os.path.join(out_dir, "results.json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(blob)
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_summary(results))
    meta = {
        "run_timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "argv": sys.argv,
        "results_json_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "cohort_path": os.path.abspath(cohort_path),
        "xw_path": os.path.abspath(xw_path),
        "reference_features_path": os.path.abspath(ref_path) if ref_path else None,
    }
    with open(os.path.join(out_dir, "run_metadata.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, sort_keys=True, indent=2)
        fh.write("\n")
    return EXIT_OK if verdict_primary == "ANALYSIS_COMPLETED" else EXIT_FEASIBILITY_STOP


def _write_csv(path: str, rows: List[tuple]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["repeat", "fold", "decision_id", "y", "p0", "p1", "d"])
        for r_i, f_i, did, y, p0, p1, d in rows:
            w.writerow([r_i, f_i, did, y, repr(p0), repr(p1), repr(d)])


def _f(x: Any, nd: int = 5) -> str:
    return "NA" if x is None else f"{x:.{nd}f}"


def render_summary(res: dict) -> str:
    L = [f"# P2-C1.2 confirmatory analysis summary", ""]
    if res["test_mode"]:
        L += ["**TEST MODE** - not a confirmatory run (repeats overridden to %d)." % res["frozen_parameters"]["n_repeats_used"], ""]
    if res["input_marked_synthetic"]:
        L += ["**SYNTHETIC INPUT** - numbers carry no scientific meaning.", ""]
    L += [f"- Protocol: {res['protocol_id']} + {res['amendment_id']}", f"- Cohort SHA-256: `{res['inputs']['cohort_sha256']}`", f"- X_W SHA-256: `{res['inputs']['xw_sha256']}`", f"- Primary verdict: **{res['verdicts']['primary']}**; Riley: {res['verdicts']['riley']}; robustness: {res['verdicts']['robustness']['flag']}", ""]
    L += ["## Cohort flow", "", "| status | n |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(res["cohort_flow"]["status_counts"].items())] + [""]
    L += ["## Analyses", "", "| population | n | events | groups | Delta_logloss | 95% repeat interval | M0 Brier | M1 Brier | M0 AUROC | M1 AUROC |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name in ("primary", "S1", "S2_low", "S2_high"):
        c = res["population_counts"][name]
        a = res["analyses"][name]
        if a.get("status") == "COMPLETED":
            iv = a["delta_logloss_repeat_percentile_interval_95"]
            m0, m1 = a["models"]["M0"], a["models"]["M1"]
            L.append(f"| {name} | {c['n']} | {c['events']} | {c['n_groups']} | {_f(a['delta_logloss'], 6)} | [{_f(iv[0], 6)}, {_f(iv[1], 6)}] | {_f(m0['brier']['mean'])} | {_f(m1['brier']['mean'])} | {_f(m0['auroc']['mean'])} | {_f(m1['auroc']['mean'])} |")
        else:
            L.append(f"| {name} | {c['n']} | {c['events']} | {c['n_groups']} | {a.get('status')} | | | | | |")
    L += ["", "Positive Delta_logloss = M1 (B + X_W) has lower out-of-sample log loss than M0 (B). The interval is over 20 repeat-level estimates (resampling instability), not a population confidence interval.", ""]
    r = res["riley_2020"]
    if r.get("computable"):
        L += ["## Riley et al. 2020 (primary population; hard stop if not met)", "", f"- criterion (i) min N = {r['criterion_i_min_n']} (met: {r['criterion_i_met']}); criterion (iii) min N = {r['criterion_iii_min_n']} (met: {r['criterion_iii_met']}); realized N = {r['realized_n']}, events = {r['realized_events']}", ""]
    if res["verdicts"]["primary"] == "FEASIBILITY_STOP_RILEY":
        L += ["## FEASIBILITY_STOP_RILEY", "", "The primary population does not meet Riley et al. 2020 criteria (i) and (iii) at the frozen planning values. No model was fitted; no parameter was changed.", ""]
    if res["feasibility"]["per_population"]["primary"] == "FEASIBILITY_STOP":
        L += ["## FEASIBILITY_STOP", "", f"Reason: {res['feasibility']['reasons']['primary']}", "Confirmatory fitting stopped; no fold count or parameter was changed.", ""]
    L += ["## Implementation choices requiring author approval", ""] + [f"- {c}" for c in res["implementation_choices_requiring_author_approval"]] + [""]
    return "\n".join(L)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cohort", required=True)
    ap.add_argument("--xw", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--reference-features", default=None, help="optional CSV decision_id,hardness,nesting_depth for the missingness audit")
    ap.add_argument("--sha-check", nargs=2, metavar=("COHORT_SHA256", "XW_SHA256"), default=None, help="fail closed unless the inputs have these SHA-256 hashes")
    ap.add_argument("--test-mode", action="store_true", help="TESTS ONLY: permits --repeats; recorded in outputs")
    ap.add_argument("--repeats", type=int, default=None, help="TESTS ONLY (requires --test-mode)")
    args = ap.parse_args(argv)
    if args.repeats is not None and not args.test_mode:
        print("ERROR: --repeats override is refused outside --test-mode (frozen: 20 repeats).", file=sys.stderr)
        return EXIT_INPUT_INVALID
    n_rep = N_REPEATS_FROZEN
    if args.repeats is not None:
        if args.repeats < 1 or args.repeats > N_REPEATS_FROZEN:
            print("ERROR: --repeats must be in 1..20", file=sys.stderr)
            return EXIT_INPUT_INVALID
        n_rep = args.repeats
    try:
        code = run(args.cohort, args.xw, args.out, n_rep, args.test_mode, args.reference_features, args.sha_check)
    except InputError as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return EXIT_INPUT_INVALID
    if code == EXIT_FEASIBILITY_STOP:
        print("FEASIBILITY_STOP (mechanical or Riley): see results.json", file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
