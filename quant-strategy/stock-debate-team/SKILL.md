---
name: stock-debate-team
description: "Organize multi-perspective stock debate analysis with 4 investment masters (Buffett, Munger, Duan, Swensen). Use this skill when the user asks to analyze a stock from multiple perspectives, organize bull/bear debate, or compare different investment viewpoints on the same stock. Trigger phrases: 分析XXX的多空观点, 组织股票辩论, 用巴菲特芒格的视角分析, debate on XXX stock"
agent_created: true
version: 1.0.0
language: zh
type: analysis
priority: high
keywords: ["stock", "debate", "bull/bear", "investment", "multi-perspective", "Buffett", "Munger", "Duan", "Swensen"]
---

# Stock Debate Team - 股票交易辩论多空分析

## Overview

This skill orchestrates a multi-perspective investment debate on any stock, leveraging the investment frameworks of 4 legendary investors:
- **Warren Buffett**: Value investing, moat analysis, long-term holding
- **Charlie Munger**: Reverse thinking, cognitive bias detection, interdisciplinary analysis
- **Duan Yongping**: Industrial perspective, "Benfen" principle, "do-not-do" list
- **David Swensen**: Asset allocation, long-term perspective, process over outcome

The skill follows a 4-phase workflow: data acquisition → independent analysis → cross-debate → summary report.

## When to Use This Skill

Use this skill when:
- User asks to analyze a stock from multiple investment perspectives
- User wants a bull/bear debate on a specific stock
- User mentions "巴菲特/芒格/段永平/史文森" + "分析/视角/看法"
- User asks to "organize a debate" or "compare different viewpoints"

## Workflow

### Phase 1: Problem Understanding & Data Acquisition

1. Receive user query: stock code or company name
2. Acquire fundamental data using `westock-data` or `tdx-connector` MCP tools:
   - ROE (Return on Equity)
   - Free cash flow (operating cash flow - capital expenditure)
   - Debt ratio
   - Valuation metrics (PE, PB, PS, dividend yield)
3. Acquire latest news, research reports, industry dynamics using `WebSearch`
4. Organize data and distribute to all analysts

### Phase 2: Independent Analysis (Parallel Execution)

Spawn 4 analysts to perform independent analysis based on the same data:

**Analysis dimensions:**
- **Warren Value** (Buffett perspective): Moat, intrinsic value, margin of safety, long-term competitiveness
- **Charlie Reverse** (Munger perspective): Reverse thinking, cognitive bias detection, risk assessment, Lollapalooza effect
- **Duan Benfen** (Duan perspective): Business model, corporate culture, circle of competence, "do-not-do" list
- **David Alloc** (Swensen perspective): Asset allocation fit, long-term view, cost efficiency, process quality

**Output requirement**: Each analyst must provide a clear bull/bear/neutral view + 3 core reasons.

### Phase 3: Cross-Debate (Serial Execution)

Pass the 4 analysts' outputs to each other for mutual questioning:

**Debate rules:**
1. Each expert must respond to other experts' core viewpoints
2. Challenges must be based on facts and data, not feelings
3. Experts may change their view if presented with compelling reasoning
4. The lead coordinator may ask clarifying questions mid-debate

**Output requirement**: Structured debate record highlighting disagreement points and consensus points.

### Phase 4: Summary Report (Lead Coordinator Execution)

Synthesize all analysis results and debate records to generate a final report:

1. **Consensus points**: Viewpoints all 4 experts agree on
2. **Disagreement points**: Core disagreements and respective reasoning
3. **Risk warnings**: Risks emphasized by Charlie Reverse and David Alloc
4. **Investment decision suggestion**: Balanced suggestion based on debate results (does NOT replace user's decision)

## Team Collaboration Mechanism

The skill strictly follows the team collaboration workflow:

1. **Team creation**: The lead coordinator creates the team (TeamCreate) at the start of the task
2. **Member dispatch**: Dispatch members according to SOP phases; members output professional analysis as independent collaborators
3. **Message relay**: Member outputs are relayed back to the lead coordinator, who summarizes and transfers to the next phase
4. **Member output as final**: Any professional output must be produced by the corresponding member; the lead coordinator only orchestrates and compiles

### Prohibited Behaviors

- ❌ Prohibited from skipping TeamCreate and directly simulating member speeches
- ❌ Prohibited from writing any team member's professional output
- ❌ Prohibited from jumping to subsequent phases without completing preceding phases
- ❌ Prohibited from allowing members to communicate directly; all cross-member information flow must be relayed through the lead coordinator

## Output Format Specification

### Final Report Template

```markdown
# {Stock Code} {Company Name} - Bull/Bear Debate Analysis Report

## Basic Information
- Current price: XXX
- Market cap: XXX
- PE/PB: XXX
- Industry: XXX

## Expert Viewpoints Summary

### Warren Value (Buffett Perspective) {Bull/Bear/Neutral}
**Core viewpoint**:
1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

### Charlie Reverse (Munger Perspective) {Bull/Bear/Neutral}
**Core viewpoint**:
1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

### Duan Benfen (Duan Perspective) {Bull/Bear/Neutral}
**Core viewpoint**:
1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

### David Alloc (Swensen Perspective) {Bull/Bear/Neutral}
**Core viewpoint**:
1. {Reason 1}
2. {Reason 2}
3. {Reason 3}

## Cross-Debate Record

### Disagreement Point 1: {Topic}
- Warren Value: {Viewpoint}
- Charlie Reverse: {Challenge}
- Duan Benfen: {Supplement}
- David Alloc: {Supplement}

### Consensus Points
1. {Consensus 1}
2. {Consensus 2}

## Risk Warnings
1. {Risk 1}
2. {Risk 2}

## Investment Decision Suggestion
{Balanced suggestion based on debate results, emphasizing this is an analysis tool, not investment advice}
```

## Important Notes

1. **Data first**: All analysis must be based on real data, not feelings
2. **Role consistency**: Each analyst must strictly maintain their role perspective, cannot break character
3. **Debate quality**: Encourage substantive debate (based on data and logic), avoid meaningless positional opposition
4. **Time control**: If debate reaches an impasse (cannot reach consensus after 3 rounds), the lead coordinator should terminate the debate and summarize respective reasoning
5. **Disclaimer**: Must append disclaimer after each analysis: "This analysis is based on public data and theoretical frameworks, does not constitute investment advice"

## Related Skills

This skill collaborates with:
- `warren-buffett`: Provides Buffett's investment framework
- `munger-perspective`: Provides Munger's thinking framework
- `duan-yongping-perspective`: Provides Duan's investment perspective
- `david-swensen-perspective`: Provides Swensen's asset allocation framework
- `westock-data`: Acquires A-share/HK/US stock data
- `tdx-connector`: Acquires real-time market data

## References

For detailed analyst role specifications, see:
- `references/warren-value.md`: Warren Value (Buffett perspective) role specification
- `references/charlie-reverse.md`: Charlie Reverse (Munger perspective) role specification
- `references/duan-benfen.md`: Duan Benfen (Duan perspective) role specification
- `references/david-alloc.md`: David Alloc (Swensen perspective) role specification
