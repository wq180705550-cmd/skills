---
name: loop
description: "Execute iterative loop optimization tasks. Use when user input starts with '/loop' followed by a task description, convergence criteria, and max iterations. Implements autonomous execute→validate→fix→retry cycles until success criteria are met or iteration limit reached. Different from /goal which executes once without automatic retry."
agent_created: true
---

# Loop - Iterative Optimization Execution

## Overview

This skill replicates Claude Code's `/loop` command functionality. To execute iterative optimization tasks with automatic retry loops. Receive a task, convergence criteria, and iteration limit; then autonomously cycle through execution → validation → fix → retry until all success criteria are met or the maximum iteration count is reached.

## When To Use This Skill

Trigger this skill when:
- User input starts with `/loop` followed by task description
- Task requires multiple iterations to optimize (code, prompts, strategies, parameters)
- Success can be measured by quantifiable metrics (error rates, accuracy, performance)
- Automatic retry and self-correction would be more efficient than manual iteration

**Do NOT use this skill for:**
- Single-execution tasks (use `goal` skill instead)
- Tasks without clear success metrics
- One-time code generation or analysis

## Core Definition

The `/loop` skill executes iterative optimization cycles. Each cycle consists of: execute → collect results → validate against criteria → fix issues → retry. Continue looping until either:
1. **Convergence**: All success criteria are met
2. **Iteration limit**: Maximum iterations reached (force stop and output current best result)

### Two Loop Modes

1. **Condition loop**: Continue until validation metrics meet thresholds (zero errors, accuracy ≥ X%, etc.)
2. **Limited loop**: Restrict maximum iteration rounds, force stop at limit and output current optimal result

## Workflow

### Step 1: Parse Loop Task and Boundaries

To begin, explicitly restate:
- Complete loop task description
- Acceptance/validation criteria with numeric thresholds
- Maximum iteration count
- Constraint rules

Identify task type: code optimization, prompt tuning, parameter search, bug fixing, strategy backtest, etc.

Identify prerequisite dependencies: read project files, load datasets, initialize environment, install dependencies.

**Output**: 【Loop Plan Confirmation】task, criteria, max iterations, first-round execution plan. Wait for user confirmation before starting.

### Step 2: First-Round Baseline Execution

Execute the target logic by calling file read, terminal run, quantitative calculation, or other tools.

Collect full outputs: execution logs, error stacks, quantitative metrics, validation scores, text defects.

**Output format**: 【Round 0 Baseline Results】with clear list of unmet defect checklist.

### Step 3: Iteration Core Logic (automatic repeat until exit condition)

Each single iteration follows four fixed steps:

1. **Defect attribution**: Distinguish code bugs, unreasonable parameters, missing logic, data preprocessing errors, boundary scenario omissions
2. **Targeted fix**: Only modify files, parameters, or functions causing the failure; minimal-scope changes; do not break originally working logic
3. **Re-run validation**: Execute complete re-testing process; re-collect metrics and errors
4. **Compare before/after metrics**: Record optimization gain for this round

**Output format per round**: 【Round N Iteration】→ Defect List → Modifications → Retest Results → Currently Meets Criteria?

### Step 4: Loop Termination Judgment (one of two)

1. **Convergence termination**: All acceptance criteria fully satisfied → immediately stop loop
2. **Upper-limit termination**: Iteration count reaches user-specified maximum → force stop; output current best version; mark remaining unresolved issues

### Step 5: Loop Summary

After loop ends, uniformly output:
1. Complete iteration log for all rounds; metric changes compared per round
2. Final complete list of changed files and code diffs
3. Final validation metrics and complete runnable code
4. Remaining risks, further optimization directions (if not fully converged)

## Built-in Hard Constraints

1. **Do not arbitrarily expand requirements**: Only iterate around the given loop goal; do not add unrelated features
2. **Minimum modification principle**: Each iteration only fixes defect points; no global large-scale refactoring
3. **Complete traceability**: Each round of modifications must annotate file path, line number, and change reason
4. **Do not silently loop**: Each iteration actively synchronizes progress; inform current metrics and gaps
5. **Fault tolerance control**: Single round encounters fatal environment failure (tool timeout, missing files), automatically log and attempt compatible fix; after 3 consecutive failures, pause loop and ask user to confirm handling plan
6. **Metric quantization**: All validation results must output numerical values; reject vague descriptions like "some improvement"

## User Interaction Standards

### Input Format

User standard input format:
```
/loop 【iteration task】|【termination condition】|【maximum iteration rounds】
```

Example:
```
/loop optimize futures LLM analysis prompt | hallucination rate ≤5%, logic accuracy ≥65% | maximum 8 rounds
```

### Interaction Flow

1. After receiving command, first output loop plan confirmation: task, judgment criteria, iteration upper limit, first-round execution plan; wait for user confirmation before starting loop
2. After each round of iteration completes, actively push this round's report; do not wait for user to ask
3. When loop terminates, output complete iteration review document

## Differentiation from `/goal` Skill

| Aspect | `/goal` | `/loop` |
|--------|----------|----------|
| Execution | Single complete task, execute once and done | Multiple automatic iterations with retry |
| Retry | No automatic retry | Automatic fix → re-execute cycles |
| Goal | Deliver runnable output | Metric convergence through iteration |
| Use case | One-time development tasks | Tuning, prompt iteration, bug batch fix, strategy backtest optimization |

## Example Execution

**User input**:
```
/loop optimize CTA volatility calculation function | prediction error <3% | maximum 5 rounds
```

**Assistant response**:
```
【Loop Plan Confirmation】
Task: Optimize CTA volatility calculation function
Termination condition: Prediction error <3%
Maximum iterations: 5 rounds
First round: Run calculation to obtain baseline error, list all unmet defects

Confirm to start loop?
```

(After user confirms, execute iterations...)

**Final output after convergence**:
```
【Loop Complete Summary】
Total iterations: 3 rounds (max 5, early convergence exit)

Metric convergence record:
| Round | Prediction Error | Meets Criteria? |
|-------|-----------------|-----------------|
| 0     | 8.7%            | No              |
| 1     | 5.1%            | No              |
| 2     | 4.3%            | No              |
| 3     | 2.1%            | Yes             |

Final complete code: [attached]
All changed files: [list]
Remaining risks: None
```
