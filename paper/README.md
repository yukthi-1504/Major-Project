# Paper – IEEE Format

This folder contains everything you need to write your project paper in **IEEE format**, in **your own words**, and keep it **plagiarism-free**.

## Files

| File | Purpose |
|------|--------|
| **IEEE_Paper_Template.tex** | IEEE two-column LaTeX template. Section headings and placeholders are provided; you write all body text. |
| **AUTHOR_GUIDE.md** | Section-by-section writing prompts, IEEE checklist, and tips for 0% plagiarism / original writing. |

## How to use

1. Open **AUTHOR_GUIDE.md** and read the “Points to cover” for each section.
2. Open **IEEE_Paper_Template.tex** and replace each “Replace this…” placeholder with your own paragraphs.
3. Do **not** copy-paste from README or from any AI output; write every sentence yourself.
4. Add real references (papers, K8s docs, scikit-learn) in the `\begin{thebibliography}` block and cite them as [1], [2] in the text.
5. Compile the LaTeX (Overleaf or `pdflatex`) to generate the PDF.

## Compiling

- **Overleaf:** Upload the `.tex` file, ensure `IEEEtran` class is available (it is on Overleaf), and compile with pdfLaTeX.
- **Local:** Install a TeX distribution (e.g., MiKTeX, TeX Live), then run:
  ```bash
  pdflatex IEEE_Paper_Template
  pdflatex IEEE_Paper_Template
  ```

## Conference not decided yet

The template is **conference-agnostic**. Finish writing the full paper first. When you choose a conference:

1. Open `IEEE_Paper_Template.tex`.
2. Find the commented line: `%\thanks{To appear in: ...}` under the title.
3. Uncomment it and fill in: **[Conference Full Name]**, **[City, Country]**, **[Dates]** (e.g. ``March 15--17, 2026'').
4. If the conference provides a specific .sty or template, you can switch to it; the section structure will stay the same.

Good luck with your publication.
