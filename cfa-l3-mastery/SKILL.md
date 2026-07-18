---
name: cfa-l3-mastery
description: This skill provides deep, exam-ready knowledge of the CFA Level 3 curriculum (portfolio management, asset allocation, IPS, behavioral finance, derivatives/equity/FI/alternatives PM, GIPS/ethics) plus a mapped inventory of the user's Baidu Netdisk CFA study materials with a "most-recent-year-wins" rule for overlapping content. Use it when the user asks CFA L3 questions, requests L3 concept explanations, calculations, IPS/essay drafting, or wants to locate/study their netdisk L3 materials. Trigger keywords: CFA、CFA三级、L3、CFA Level 3、资产配置、IPS、组合管理、道德GIPS、CFA备考.
agent_created: true
---

# CFA Level 3 Mastery

A specialized study and research assistant for CFA Level 3. It combines (1) an authoritative L3
curriculum knowledge base and (2) a mapped inventory of the user's actual Baidu Netdisk CFA materials,
so answers are both conceptually correct and tied to the resources the user already owns.

## When to use

- The user asks any CFA Level 3 question: concepts, formulas, calculations, essay/constructed-response drafting.
- The user wants to locate, organize, or study their netdisk CFA materials (especially L3).
- The user references CFA topics like asset allocation, IPS, behavioral finance, GIPS/ethics, equity/FI/derivatives/alternatives portfolio management.
- Cross-level CFA questions where L3 perspective (portfolio management + argumentation) applies.

## Core principles

1. **Most-recent-year-wins for overlaps.** The user's netdisk holds multiple annual editions of the
   same topic. When content overlaps, always prefer the newest year's material. The current latest
   complete L3 system is the **2024 L3 program (Volumes V1–V5: CME/AA, Equity, Fixed Income, IPS &
   Behavioral, Trading/Case)**; Ethics has a newer **2025/2026 考纲** file. Always point the user to
   the ★-recommended (latest) items in `references/l3_materials.md` and note older versions only as reference.
2. **L3 is about argumentation, not selection.** Lead with the command word, show the reasoning chain,
   and present calculations step-by-step. See `references/l3_curriculum.md` §一 for essay technique.
3. **Tie answers to the user's materials.** After explaining a concept, reference the matching netdisk
   file(s) so the user can open the exact lecture note / framework map / video.

## Workflow

1. **Classify the question** into one of the curriculum modules (3.1–3.14 in the knowledge base):
   Asset Allocation, CME, Currency Mgmt, Fixed-Income PM, Equity PM, Derivatives PM, Alternatives,
   Risk Mgmt, Execution, Performance Eval, Private Wealth IPS, Institutional IPS, Behavioral Finance, Ethics/GIPS.
2. **Retrieve knowledge** from `references/l3_curriculum.md` (authoritative concepts, formulas, exam tips).
   Use the latest curriculum phrasing; flag any 2025/2026 考纲 updates for Ethics.
3. **Map to materials** via `references/l3_materials.md` — pick the ★ latest-year file(s) for the topic
   and give the exact netdisk path so the user can open it.
4. **Compose the answer** by type:
   - *Concept*: definition → mechanism → link to other modules → example.
   - *Calculation*: formula → substitution → result → economic interpretation.
   - *IPS*: constraints list → objectives → allocation recommendation → rationale (tax/behavior/liquidity).
   - *Essay/Constructed Response*: answer the command word first, then bullet points (each = conclusion + reason), show all calc steps.
5. **De-overlap reminder**: if the user cites an older edition, remind them the newest year is the standard.

## Bundled resources

- `references/l3_curriculum.md` — Deep L3 curriculum knowledge base (exam structure, all modules, essay technique, workflow). **Primary knowledge source.**
- `references/l3_materials.md` — Netdisk L3 materials grouped by topic with the most-recent-year-wins resolution (★ = recommended latest, others = historical reference).
- `assets/cfa_l3_inventory.csv` — Full L3 file inventory (290 items: name, path, type, year, size).
- `assets/cfa_inventory.csv` — Full CFA inventory across all levels (734 items) for cross-level lookup.

## Coverage note

The material inventory was built from a full filename/semantic search of the three CFA roots on the
user's netdisk (`/cfa三级/`, `/CFA2026/`, `/我的资源/`), which together constitute the complete CFA
collection (their paths contain "cfa"/"CFA", so path-based matching captures all descendant files).
734 unique items were identified (L1: 197, L2: 230, L3: 290, unlabeled: 17). L3 deep-learning targets
the 290 L3 items with the recency rule applied.

> Note: The connector exposes listing/search but not file download, so the knowledge base encodes the
> canonical CFA L3 curriculum (stable, exam-authoritative) mapped onto the user's material inventory.
> If a download capability is later enabled, literal PDF text can be embedded to extend coverage.
