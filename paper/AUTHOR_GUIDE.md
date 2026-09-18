# IEEE Paper – Author Guide (Your Own Words, 0% Plagiarism)

This guide helps you write the paper **yourself** in IEEE format so that the text is **original** and **plagiarism-free**. The template (`IEEE_Paper_Template.tex`) gives the structure; you supply every sentence.

---

## Can We Achieve 0% AI / 0% Plagiarism? Yes.

- **0% plagiarism:** Write every paragraph in your own words. Cite other work with IEEE references [1], [2]. Do not copy-paste from README, papers, or websites.
- **0% AI-written:** Use this guide only as a *prompt* for what to cover. You type the actual sentences. Do not paste AI-generated paragraphs into the paper.
- **Practical tip:** For each section, read the “Points to cover” below, then close this file and write 2–3 sentences from memory. Then refine. That keeps the voice yours.

---

## IEEE Format Checklist

- **Sections:** I. Introduction, II. Related Work, … (already in the template).
- **References:** Numbered [1], [2] in text; full entry in `\begin{thebibliography}`.
- **Figures/Tables:** Numbered (Fig. 1, Table I); cite in text as “Fig. 1” or “see Table I.”
- **Length:** Typically 6–8 pages for a conference paper (adjust per your conference).
- **Abstract:** 80–150 words, no citations.
- **Keywords:** 5–8 comma-separated terms (already suggested in template).

---

## Section-by-Section: What to Write (In Your Own Words)

### Abstract (80–150 words)

**Points to cover:**

1. Problem: E-commerce flash sales cause sudden traffic spikes; reactive autoscaling reacts too late.
2. Approach: Predict traffic about one hour ahead using ML; scale Kubernetes infrastructure before the spike.
3. Method: Random Forest on synthetic hourly flash-sale data; REST API for predictions; rule-based replica count; Kubernetes HPA.
4. Result: Proactive scaling; mention your MAE/RMSE and that the system recommends 1–5 replicas.

Write one short paragraph. Do not copy from the README; paraphrase.

---

### I. Introduction

**Points to cover:**

- Why flash sales matter (e.g., high demand in short windows).
- How they cause unpredictable or sudden traffic spikes.
- Limitations of reactive autoscaling (delay, timeouts, poor UX, lost sales).
- Objective: proactive autoscaling by predicting traffic in advance.
- Short roadmap: “The rest of the paper is organized as follows: Section II … Section III …”

Write 3–4 short paragraphs. Use your own sentences.

---

### II. Related Work

**Points to cover:**

- Reactive vs predictive autoscaling in cloud/Kubernetes.
- Traffic or load forecasting (e.g., time series, ML).
- Use of ML for resource management or scaling.
- Kubernetes HPA and similar mechanisms.

**Plagiarism avoidance:** For each source, read it once, then write one sentence summarizing the idea **without** looking at the original. Cite as [1], [2], etc. Add 3–5 references to the `.tex` file.

---

### III. System Architecture

**Points to cover:**

- Flow: Flash sale event → REST API → ML model → scaling logic (traffic → replicas) → Kubernetes HPA → deployment.
- Optional: one figure (e.g., redraw the README architecture diagram in draw.io or LaTeX).
- Describe each block in one or two sentences.

Write in your own words; do not copy the README diagram text verbatim.

---

### IV. Data

**Points to cover:**

- Dataset: synthetic, 30 days, hourly (e.g., 722 rows), 7 columns.
- Schema: timestamp, hour, day_of_week, campaign, discount, past_traffic, traffic (target).
- Why synthetic: no real user data, reproducibility, controlled scenarios, privacy.
- How generated: script (`traffic_data_generator.py`), base pattern + campaign/discount effects.

Use your own wording; you can refer to `data/schema.md` for numbers but do not copy sentences.

---

### V. Methodology

**V-A. Feature engineering**

- 16 features: hour; campaign; discount; past_traffic; lag_1, lag_2, lag_3; rolling_mean_3, rolling_std_3; day_0…day_6 (one-hot).
- Briefly say what each group captures (time, business, recent history).

**V-B. Model and training**

- Random Forest Regressor (e.g., 200 trees, max depth 10).
- Train/test split (e.g., 80/20).
- Metrics: MAE, RMSE; optionally compare to a baseline (e.g., mean predictor).

**V-C. Scaling logic**

- Rule-based: predicted traffic → 1–5 replicas (use your actual thresholds from the project).
- How this connects to Kubernetes HPA (e.g., min/max replicas, metrics).

Write all in your own sentences.

---

### VI. Implementation

**Points to cover:**

- Flask API: `/health`, `/predict`; request (current_time, last_traffic, campaign, discount) and response (predicted_traffic, recommended_replicas).
- Kubernetes: deployment, HPA (min/max replicas, CPU/memory targets if you use them).
- Autoscale script/simulation (what it does in one sentence).
- Optional: dashboard for demo.

Describe what *you* built; avoid copying README or code comments verbatim.

---

### VII. Results

**Points to cover:**

- Your actual MAE and RMSE from training (from your run of `train_model.py`).
- Top 3–5 feature importances (e.g., rolling_mean_3, past_traffic, campaign).
- Scaling behavior: e.g., how replicas change in the 24-hour simulation or in a sample scenario.

Use real numbers from your project; write the interpretation yourself.

---

### VIII. Discussion and Limitations

**Points to cover:**

- Limitations: synthetic data only; single model; fixed replica thresholds; no real load testing.
- Future work: real traffic data, retraining pipeline, database, Prometheus/Grafana, load testing, CI/CD (as in your README).

One short paragraph each is enough. Use your own words.

---

### IX. Conclusion

**Points to cover:**

- One short paragraph: restate problem, approach (ML-based traffic prediction + proactive scaling), and main contribution.
- No new technical content; no new citations.

---

## References (IEEE Style)

- In text: “Previous work [1] showed that …” or “The system uses the Horizontal Pod Autoscaler [2].”
- In bibliography: number, authors, title, journal/conference, volume, number, pages, year. For URLs: author/organization, “Title,” URL, “accessed Month Year.”

Add real references (papers you read, Kubernetes docs, scikit-learn) and cite only what you actually use.

---

## Before Submission

- [ ] Every section has been written by you; no pasted AI or README text.
- [ ] All claims from others are cited [1], [2], …
- [ ] Abstract and conclusion are concise and in your voice.
- [ ] MAE/RMSE and feature importance match your actual runs.
- [ ] Spell-check and grammar pass.
- [ ] Run the LaTeX file to ensure it compiles (e.g., pdflatex or Overleaf).
- [ ] **When conference is decided:** Uncomment the `\thanks{...}` line under the title in the .tex file and fill in conference name, location, and dates.

---

## Compiling the LaTeX

- **Overleaf:** Upload `IEEE_Paper_Template.tex` and use “pdfLaTeX” to compile.
- **Local:** `pdflatex IEEE_Paper_Template`, then `bibtex` if you switch to BibTeX, then `pdflatex` twice.

You can rename the `.tex` file (e.g., to `Predictive_Autoscaling_FlashSales.tex`) once you are happy with it.

Good luck with your publication.
