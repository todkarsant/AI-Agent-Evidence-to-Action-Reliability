# Research Reference Register

Last updated: 2026-10-08. Entries 1–16 were checked against their primary pages on 2026-10-08; see the verification note at the end of section B.

This register is the working literature/evidence index for Project 2. It is intentionally separated into (A) scholarly research, (B) methodological/measurement sources, (C) industry/corporate evidence, and (D) journal targets/watchlist.

## A. Core scholarly literature

### A1. Agent reliability, consistency, robustness
1. Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). **Towards a Science of AI Agent Reliability.** arXiv:2602.16666. https://arxiv.org/abs/2602.16666
   - Relevance: establishes reliability as multidimensional (consistency, robustness, predictability, safety) and motivates evaluation beyond single-run success.

2. Gupta, A. (2026). **ReliabilityBench: Evaluating LLM Agent Reliability Under Production-Like Stress Conditions.** arXiv:2601.06112. https://arxiv.org/abs/2601.06112
   - Relevance: repeated execution, semantic-equivalent perturbations, tool/API faults, and end-state equivalence.
   - Novelty implication: generic perturbation robustness/repeatability is already occupied and must not be claimed as Project 2's novel contribution.

3. Raj, H., Orkat, N., Mukherjee, S., Guha, A., Flynn, C., & Majumdar, S. (2026). **Consistency as a Testable Property: Statistical Methods to Evaluate AI Agent Reliability.** arXiv:2605.10516. https://arxiv.org/abs/2605.10516
   - Relevance: formal treatment of consistency under semantically preserving perturbations; reinforces the need for explicit reliability measurement.

4. de Zarzà, I., de Curtò, J., Cabot, J., Manzoni, P., & Calafate, C. T. (2026). **Semantic Invariance in Agentic AI.** arXiv:2603.13173. https://arxiv.org/abs/2603.13173
   - Relevance: metamorphic/semantic-preserving transformations for agent robustness.
   - Novelty implication: semantic invariance itself is not an available novelty seam.

### A2. Evidence sufficiency / grounding / action linkage
5. Qiu, J., Han, Z., & Huang, C. (2026). **SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation.** arXiv:2605.03534. https://arxiv.org/abs/2605.03534
   - Relevance: evidence sufficiency as a set-level verification problem using coverage, relation strength, disagreement, conflict, and uncertainty.
   - Novelty implication: generic evidence sufficiency/coverage is already occupied.

6. Zhang, H., & Wu, W. (2026). **Do LLMs Know When Evidence is Insufficient? An Evidence Sufficiency Benchmark for Answer-Abstention Calibration in Retrieval-Augmented Generation.** Computers, Materials & Continua, 89(1), 69. DOI:10.32604/cmc.2026.086343.
   - Relevance: controlled evidence-sufficiency levels and abstention behavior.
   - Novelty implication: evidence-sufficiency calibration is an existing research area.

7. Sato, H., Tanaka, Y., Nakamura, R., Kobayashi, A., & Ito, M. (2026). **Learning Evidence Sufficiency Boundaries for Selective Answering in Grounded Multi-Hop QA.** arXiv:2609.01687. https://arxiv.org/abs/2609.01687
   - Relevance: evidence sufficiency boundaries, abstain-to-answer transitions, and stability after sufficient evidence.
   - Novelty implication: another direct collision for standalone evidence-sufficiency novelty.

8. Wu, J. (2026). **From Evidence to Action: A Systematic Study of External Knowledge Grounding in LLM-based Agents.** SSRN 7335618. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7335618
   - **UNVERIFIED (2026-10-08):** the SSRN page and Crossref record could not be read (rate-limited) and an exact-title search returned no match. Do not cite until verified.
   - Relevance: explicitly studies the gap between consulting evidence and having that evidence govern reasoning/planning/action; emphasizes runtime verification, provenance, uncertainty, and verifiable state change.
   - Status: preprint/working paper; do not treat as peer-reviewed journal evidence unless independently verified.

9. Liao, J. (2026). **Auditing Provenance Sensitivity in LLM Agent Action Selection.** arXiv:2607.20827. https://arxiv.org/abs/2607.20827
   - Relevance: source authority, evidence weakening, and action-selection sensitivity.
   - Novelty implication: provenance sensitivity/action-selection auditing is already occupied.

10. Guo, X., Xu, Z., Huo, D., Zhang, Y., Wang, W., Yang, Q., Yu, D., & Wang, Y. (2026). **When Tool Outputs Become Commands: Separating Action Induction from Runtime Authorization in Tool-Augmented LLM Agents.** arXiv:2608.27146. https://arxiv.org/abs/2608.27146
    - Relevance: separates action induction from runtime authorization and ties execution authority to audited evidence.
    - Novelty implication: action authorization/provenance separation is adjacent but distinct from Project 2's intended incremental-validity question.

11. Zheng, Y., Zhou, J., Hu, R., & Fang, R. (2026). **Evidence-Verified LLM Agents for Safe Backend Incident Remediation.** Preprint/ResearchGate record; DOI:10.13140/RG.2.2.24026.91840.
    - Relevance: evidence gate between hypothesis generation and remediation execution.
    - Status: preprint/grey literature; use as contextual evidence, not as a peer-reviewed anchor unless publication status is verified.

12. Wu, J., & Gong, M. (2026). **Policy-Invisible Violations in LLM-Based Agents.** arXiv:2604.12177. https://arxiv.org/abs/2604.12177
    - Relevance: shows how consequential policy failures can occur when facts required for correct judgment are hidden at decision time; trace-level human review is relevant to our measurement protocol.

13. Tang, Z., et al. (2026). **Safe, or Simply Incapable? Rethinking Safety Evaluation for Phone-Use Agents.** arXiv:2605.07630. https://arxiv.org/abs/2605.07630
    - Relevance: distinguishes harmless outcomes caused by safe judgment from harmless outcomes caused by inability to act; useful precedent for separating outcome class from mechanism.

14. Theodorakopoulos, L., & Theodoropoulou, A. (2026). **Auditable LLM Autonomy for Operational Decision-Making: Big Data Evidence and Decision Traces.** Computers, Materials & Continua, 88(2), Article 10. DOI:10.32604/cmc.2026.082270.
    - Relevance: evidence plane, decision-trace plane, outcomes plane; verification, action gating, trace completeness, evidence fidelity, action validity, and longitudinal stability.

15. Uluırmak, B. A., & Kurban, R. (2026). **EvalSafetyGap: A Hybrid Survey and Conceptual Framework for LLM Evaluation-Safety Failures.** arXiv:2606.30219. https://arxiv.org/abs/2606.30219
    - Relevance: benchmark validity, dynamic evaluation, judge reliability, safety measurement, governance/auditability, and proxy-target divergence.
    - Novelty implication: supports our insistence on measurement validity and separation of observable proxies from target properties.

16. Adeli, S. (2026). **Strategic Verification for Long-Running LLM Agents.** Preprints.org, posted 28 August 2026. https://doi.org/10.20944/preprints202608.2057.v1
    - Relevance: verification as a resource-constrained decision problem; verifier reliability and verification cost.
    - Status: explicitly marked non-peer-reviewed preprint; contextual only.

## B. Methodological / measurement foundations

17. Inter-rater reliability literature used for C.4.2.2:
    - Cohen's kappa remains a standard chance-corrected agreement statistic, but prevalence/marginal effects motivate sensitivity analyses.
    - Gwet AC1 is retained as a sensitivity statistic rather than a replacement for kappa.
    - Project 2 will report contingency tables and raw agreement in addition to chance-corrected coefficients.
    - These are methodological foundations, not evidence that our proposed witness construct is valid.

18. Project-specific methodological records:
    - C.4.2.3-C: fresh P0 runtime qualification.
    - C.4.2.3-D: observational evidence capture.
    - C.4.2.4-A.1: observability/identifiability attack.
    - C.4.2.4-A.2: witness redesign and novelty collision.
    - C.4.2.4-A.2B: mechanical redundancy attack.
    - C.4.2.4-A.3: witness codebook/baseline-independence attack.

19. Verified methodological references (checked 2026-10-08 against publisher, DOI or official pages; used in `paper/submission/MANUSCRIPT.md`):
    - Riley, R. D., et al. (2020). Calculating the sample size required for developing a clinical prediction model. *BMJ, 368*, m441. https://doi.org/10.1136/bmj.m441
    - Riley, R. D., et al. (2019). Minimum sample size for developing a multivariable prediction model: Part II—Binary and time-to-event outcomes. *Statistics in Medicine, 38*(7), 1276–1296. https://doi.org/10.1002/sim.7992 (correction: https://doi.org/10.1002/sim.8409, concerns the time-to-event criterion only)
    - Yu, T., et al. (2018). Spider. *EMNLP 2018*, 3911–3921. https://doi.org/10.18653/v1/D18-1425
    - Cohen, J. (1960). *Educational and Psychological Measurement, 20*(1), 37–46. https://doi.org/10.1177/001316446002000104
    - Gwet, K. L. (2008). *British Journal of Mathematical and Statistical Psychology, 61*, 29–48. https://doi.org/10.1348/000711006X126600 (issue number not confirmed)
    - Pedregosa, F., et al. (2011). Scikit-learn. *JMLR, 12*, 2825–2830. https://jmlr.org/papers/v12/pedregosa11a.html
    - Gneiting, T., & Raftery, A. E. (2007). *JASA*. https://doi.org/10.1198/016214506000001437 (volume/issue/pages not confirmed from a primary page)
    - Varma, S., & Simon, R. (2006). *BMC Bioinformatics, 7*, 91. https://doi.org/10.1186/1471-2105-7-91
    - Van Calster, B., et al. (2019). Calibration: The Achilles heel of predictive analytics. *BMC Medicine, 17*, 230. https://doi.org/10.1186/s12916-019-1466-7
    - Collins, G. S., et al. (2024). TRIPOD+AI statement. *BMJ, 385*, e078378. https://doi.org/10.1136/bmj-2023-078378
    - Rubin, D. B. (1976). Inference and missing data. *Biometrika, 63*(3), 581–592. https://doi.org/10.1093/biomet/63.3.581
    - Meta. (2024). Llama-3.2-1B model card. https://huggingface.co/meta-llama/Llama-3.2-1B (release 25 Sep 2024; Llama 3.2 Community License)

**Verification note (2026-10-08).** Entries 1–7, 9, 10 and 12–16 were verified, with these notes:
- entry 1 is accepted at ICML 2026;
- entry 4 is accepted at AMSTA 2026;
- entries 6 and 14 are peer-reviewed, and entry 14 is a review article;
- entry 11 has exactly four authors;
- entry 2's first author is Aayush Gupta and entry 9's is Junchi Liao.

Entry 8 could not be verified.

## C. Corporate / industry evidence — deliberately not treated as peer-reviewed science

### C1. Gartner (checked 2026-10-08 against Gartner's own press releases)
**Correction.** The earlier entry said that "hyperautomation total software market opportunity was projected to exceed $1 trillion by 2026", attributed to Gartner via an SEC filing (iLearningEngines 424B3, 9 Aug 2024). The filing contains **no** Gartner citation; "hyperautomation" appears there only once, in a risk factor. Gartner's own release gives a different figure. **Do not use the $1 trillion figure.**

Verified Gartner primary releases:
- Gartner (2021, April 28). Hyperautomation-enabling software market forecast to reach $596.6B in 2022 (from $481.6B in 2020). https://www.gartner.com/en/newsroom/press-releases/2021-04-28-gartner-forecasts-worldwide-hyperautomation-enabling-software-market-to-reach-nearly-600-billion-by-2022
- Gartner (2022, August 1). RPA software spending of $2.9B in 2022 (+19.5%), forecast at $3.35B in 2023 (+17.5%). Growth is described as slower than in previous years, but the market is still called "high-growth". The release does **not** say RPA stalled because it is unreliable or costly; that wording remains unverified and must not be used. https://www.gartner.com/en/newsroom/press-releases/2022-08-1-rpa-forecast-2022-2q22-press-release
- Gartner (2025, June 25). Over 40% of agentic AI projects will be canceled by end of 2027, citing escalating costs, unclear business value and inadequate risk controls. **Cited in the manuscript.** https://www.gartner.com/en/newsroom/press-releases/2025-06-25-gartner-predicts-over-40-percent-of-agentic-ai-projects-will-be-canceled-by-end-of-2027

All three are analyst forecasts, not peer-reviewed evidence.

### C1b. NVIDIA (checked 2026-10-08)
NVIDIA (2026, September 28). *NVIDIA Launches Open Agent Safety Platform to Secure Agents From Testing to Deployment.* https://nvidianews.nvidia.com/news/open-agent-safety-platform
- **OpenShell:** an open-source runtime boundary that traces agent actions and enforces policy.
- **Sentry:** an out-of-band watchdog on BlueField-4 DPUs, intended to detect agents acting outside their boundaries and quarantine them.
- **Partners:** more than 100 organisations are named as partners.

This is a vendor announcement and is cited in the manuscript as industry context only.

### C1c. Social-media posts supplied 2026-10-08 (not cited)
Three X posts were supplied:
- x.com/shivam74689/status/2106406422573449583
- x.com/nikks_techie/status/2106366160694616537
- x.com/nikks_techie/status/2106361698223640714

They could not be read automatically because X blocks it, and their content is unverified. Social-media posts are not appropriate references for a journal article. Their idea is that a 95%-accurate agent still causes loss on the remaining 5%, and that guardrails are the response. That idea is expressed in the manuscript as the authors' own hypothetical illustration, without citation.

### C2. Kognitos (re-checked 2026-10-08: the homepage title is "Kognitos: The Deterministic Agentic AI Platform for the Enterprise"; the tagline "Deterministic Agents, Hallucination-Free AI" and "English-as-Code" are both present; the platform page describes a "deterministic Symbolic Executor")
Kognitos markets an enterprise automation platform using the terms **“Deterministic Agents,” “Hallucination-Free AI,”** and **“English as Code.”** Its website describes a symbolic executor, auditable decisions, and a deterministic execution architecture:
- Kognitos corporate site: https://www.kognitos.com/
- Platform: https://www.kognitos.com/platform/
- Kognitos/qBotica announcement: https://www.kognitos.com/news/kognitos-and-qbotica-partner-to-bring-english-as-code-to-the-enterprise-for-key-operational-needs/

These statements are **vendor claims**, not independent evidence. We will use them only to establish industry motivation/positioning, not to substantiate the scientific claim that agents are reliable, hallucination-free, or deterministic.

### C3. Why industry evidence belongs in the research
Corporate evidence can establish:
- deployment motivation;
- enterprise pain-point framing;
- market expectations;
- claimed reliability/determinism requirements;
- terminology used by practitioners.

It cannot by itself establish:
- causal reliability effects;
- predictive validity;
- measurement validity;
- generalization;
- scientific novelty.

## D. Current journal / venue watchlist

The following venues supplied by the researcher are retained as the literature-search and submission-target watchlist. They are **not ranked** here.

| Venue | Verified identity / relevance |
|---|---|
| arXiv | Preprint repository; useful for current 2026 work, not peer review by itself. |
| Nature Machine Intelligence | AI/ML/robotics; explicitly covers multi-agent systems, NLP, symbolic reasoning, and societal/industrial impact. |
| Journal of Automation and Intelligence | ISSN 2949-8554; automation/AI/ML, decision-making, LLMs, multi-agent systems and autonomous systems are within scope. |
| IEEE Transactions on Artificial Intelligence | AI research venue; retain for later scope/fit verification. **Note: the IEEE URL supplied in the request (`punumber=10207`) actually corresponds to IEEE Computational Intelligence Magazine, not IEEE Transactions on Artificial Intelligence.** |
| Engineering Applications of Artificial Intelligence | Real-world engineering AI applications; explicitly includes decision support, verification/validation, safety/reliability and intelligent automation. |
| Artificial Intelligence (Elsevier) | Broad AI; includes planning/action, reasoning under uncertainty, multi-agent systems and related AI advances. |
| Applied Intelligence | Real-life complex AI problems and intelligent systems. |
| Progress in Artificial Intelligence | Broad AI research including natural language and intelligent systems. |
| Journal of Intelligent Manufacturing | Relevant mainly where the work is framed around intelligent manufacturing/industrial systems; not a default fit for the current analytical-agent study. |
| AI & SOCIETY | Relevant for AI's social, organizational, governance and societal dimensions. |
| Machine Intelligence Research | Broad machine-intelligence venue; scope should be checked against the final methodological contribution. |
| IEEE Computational Intelligence Magazine | **This is the journal behind the supplied IEEE `punumber=10207` URL.** Computational-intelligence design/applications, surveys/tutorials; useful for methodological positioning but not necessarily the primary target for an empirical agent-reliability paper. |
| ACM Transactions on Intelligent Systems and Technology | Intelligent systems/AI venue; retain for scope and recent-paper collision searches. |
| Journal of Knowledge Management | Potentially relevant only if the final paper emphasizes organizational knowledge/evidence governance; not the default technical target. |

### Scope verification notes
- Nature Machine Intelligence explicitly covers AI, machine learning, robotics, NLP, symbolic reasoning, and multi-agent systems. It also supports original Articles and Analyses and emphasizes rigorous peer review. https://www.nature.com/natmachintell/aims
- Engineering Applications of Artificial Intelligence explicitly asks for novel AI used in real-world engineering applications and validated with public datasets; its scope includes decision support, verification/validation, safety/reliability and intelligent automation.
- Applied Intelligence covers real-life complex AI problems and original AI research.
- Journal of Automation and Intelligence explicitly includes decision-making, machine learning, LLMs and multi-agent systems.

## E. Reference-use rule for Project 2

Every major manuscript claim must be assigned one of:
1. **Scholarly evidence** — peer-reviewed article or clearly identified preprint.
2. **Methodological evidence** — statistical/measurement source.
3. **Industry evidence** — vendor, analyst or corporate source, explicitly labelled.
4. **Project evidence** — our own preregistered/recorded experiment.
5. **Inference** — clearly labelled interpretation.

Industry sources must never be silently converted into scholarly evidence.

For novelty claims, current literature searches must be rerun immediately before manuscript freeze because the 2026 agent-reliability literature is moving rapidly.


### Supplied ScienceDirect ISSN links resolved
The three ISSNs in the supplied ScienceDirect comparison URL resolve to:
- **2949-8554 — Journal of Automation and Intelligence**.
- **0965-9978 — Advances in Engineering Software**.
- **0957-4174 — Expert Systems with Applications**.

For Project 2, *Expert Systems with Applications* and *Journal of Automation and Intelligence* are directly relevant venue/watchlist candidates; *Advances in Engineering Software* is relevant mainly if the manuscript is framed around engineering-software methodology or validation.
