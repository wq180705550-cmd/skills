---
name: cfa-l3-mastery
description: Unified CFA study & research assistant covering Level 1, Level 2, and Level 3. Combines (1) authoritative curriculum key-points for all 10 L1 subjects, 10 L2 subjects, and 14 L3 modules, and (2) a mapped inventory of the user's Baidu Netdisk CFA materials with a "most-recent-year-wins" rule for overlapping content. Use it when the user asks any CFA question (concept, formula, valuation, IPS/essay drafting) or wants to locate/study their netdisk CFA materials at any level. Trigger keywords: CFA、CFA一级、CFA二级、CFA三级、L1、L2、L3、CFA Level、资产配置、IPS、组合管理、道德GIPS、权益估值、固定收益、财报、CFA备考.
agent_created: true
---

# CFA Mastery（L1 / L2 / L3 统一备考助手）

A specialized study and research assistant for the entire CFA program. It combines
(1) an authoritative curriculum knowledge base covering **all three levels** with
(2) a mapped inventory of the user's actual Baidu Netdisk CFA materials, so answers
are both conceptually correct and tied to the exact resources the user already owns.

> Scope note: the skill directory is named `cfa-l3-mastery` for historical reasons;
> since this iteration it covers **L1 + L2 + L3** in full.

## When to use

- The user asks any CFA question at any level: concepts, formulas, calculations,
  valuation models, IPS / essay (constructed-response) drafting.
- The user wants to locate, organize, or study their netdisk CFA materials (L1/L2/L3).
- The user references CFA topics: asset allocation, IPS, behavioral finance, GIPS/ethics,
  equity/FCFF-FCFE valuation, fixed-income spreads/MBS, derivatives pricing, FSA, etc.
- Cross-level questions: explain how a topic progresses from L1 → L2 → L3.

## Core principles

1. **Most-recent-year-wins for overlaps.** The user's netdisk holds multiple annual
   editions of the same subject. When content overlaps, always prefer the newest year's
   material. Current latest anchors:
   - **L1/L2**: the **2026 二级 JC/GD 班** program (`/CFA2026/`) plus 2025 品职框架图.
   - **L3**: the **2024 L3 program (Volumes V1–V5)**; Ethics has a newer **2025/2026 考纲** file.
   Always point the user to the ★-recommended (latest) items in the `l*_materials.md`
   files and note older versions only as reference.
2. **Match the level's exam style.**
   - L1: concept discrimination + basic calculation (multiple choice).
   - L2: valuation / model application + heavy calculation (item set).
   - L3: argumentation + calculation (constructed response / essay).
   Lead with the command word, show the reasoning chain, present calculations step-by-step.
3. **Tie answers to the user's materials.** After explaining a concept, reference the
   matching netdisk file(s) so the user can open the exact lecture note / framework map / video.

## Workflow

1. **Classify the level and subject.** Map the question to L1/L2/L3 and the corresponding
   subject (subject lists in §一 of `cfa_all_subjects.md`).
2. **Retrieve knowledge** from the level key-points file:
   - L1 → `references/l1_keys.md` (10 subjects)
   - L2 → `references/l2_keys.md` (10 subjects, valuation-heavy)
   - L3 → `references/l3_curriculum.md` (14 modules, essay technique)
   Use the latest curriculum phrasing; flag any 2025/2026 考纲 updates for Ethics.
3. **Map to materials** via the matching `l*_materials.md` — pick the ★ latest-year
   file(s) for the subject and give the exact netdisk path so the user can open it.
4. **Compose the answer** by type:
   - *Concept*: definition → mechanism → link to other modules → example.
   - *Calculation*: formula → substitution → result → economic interpretation.
   - *Valuation (L2)*: state model (DDM/FCFF-FCFE/multiple) → inputs → compute → sanity-check.
   - *IPS (L3)*: constraints list → objectives → allocation recommendation → rationale.
   - *Essay/Constructed Response*: answer the command word first, then bullet points
     (each = conclusion + reason), show all calc steps.
5. **De-overlap reminder**: if the user cites an older edition, remind them the newest year is the standard.

## Bundled resources

- `references/cfa_all_subjects.md` — Cross-level index: all subjects per level, how each
  topic progresses L1→L2→L3, and pointers to the per-level key-points and material files. **Start here.**
- `references/l1_keys.md` — L1 key points (10 subjects: Ethics, Quant, Econ, FSA, Corp, Equity, FI, Derivatives, Alternatives, Portfolio).
- `references/l2_keys.md` — L2 key points (10 subjects, valuation-heavy: Quant, Econ, FSA, Corp, Equity Valuation, FI, Derivatives, Alternatives, Portfolio, Ethics).
- `references/l3_curriculum.md` — Deep L3 curriculum knowledge base (exam structure, 14 modules, essay technique).
- `references/l1_materials.md` / `l2_materials.md` / `l3_materials.md` — Netdisk materials grouped by subject with most-recent-year-wins (★ = recommended latest).
- `assets/cfa_inventory.csv` — Full CFA inventory across all levels (734 items: L1 197 / L2 230 / L3 290 / unlabeled 17).
- `assets/cfa_l1_inventory.csv` / `cfa_l2_inventory.csv` / `cfa_l3_inventory.csv` — Per-level inventories.

## Coverage note

The material inventory was built from a full filename/semantic search of the three CFA
roots on the user's netdisk (`/cfa三级/`, `/CFA2026/`, `/我的资源/`), which together
constitute the complete CFA collection (paths contain "cfa"/"CFA", so path-based matching
captures all descendant files). 734 unique items identified; the key-points for every
subject across L1/L2/L3 are written from the **authoritative CFA curriculum** (the same
source instructors teach from) and tied to the user's actual netdisk materials.

> **Important limitation**: The Baidu Netdisk connector exposes listing/search but **not
> file download**, so the knowledge base encodes the canonical CFA curriculum (stable,
> exam-authoritative) mapped onto the user's material inventory, rather than verbatim PDF
> text. If a download capability is later enabled, literal PDF extractions can replace the
> curriculum-derived key points without changing the file structure.
