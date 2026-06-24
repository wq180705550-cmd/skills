---
name: loop
description: "Execute iterative loop optimization tasks. Use when user input starts with '/loop' followed by task description, convergence criteria, and max iterations. Implements autonomous execute→validate→fix→retry cycles until success criteria are met or iteration limit reached. Different from /goal which executes once without automatic retry."
agent_created: true
---

# Loop - Iterative Optimization Execution

## Overview

This skill replicates Claude Code's `/loop` command functionality to execute iterative optimization tasks with automatic retry loops. Receive a task, convergence criteria, and iteration limit; then autonomously cycle through execution → validation → fix → retry until all success criteria are met or the maximum iteration count is reached.

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

**Output format**: 
```
【Round 0 Baseline Results】
- Task: [task description]
- Baseline metrics: [list all metrics with numeric values]
- Defects found: [checklist of unmet criteria]
- Next: [plan for Round 1]
```

### Step 3: Iteration Core Logic (automatic repeat until exit condition)

Each single iteration follows four fixed steps:

1. **Defect attribution**: Distinguish code bugs, unreasonable parameters, missing logic, data preprocessing errors, boundary scenario omissions
2. **Targeted fix**: Only modify files, parameters, or functions causing the failure; minimal-scope changes; do not break originally working logic
3. **Re-run validation**: Execute complete re-testing process; re-collect metrics and errors
4. **Compare before/after metrics**: Record optimization gain for this round

**Output format per round**: 
```
【Round N Iteration】
- Defects identified: [list]
- Modifications made: [file:line → change description]
- Retest results: [metrics vs previous round]
- Improvement: [numeric delta]
- Currently meets criteria? [Yes/No → list remaining gaps]
```

**Rollback mechanism**: If metrics worsen by >10% compared to previous round, automatically rollback changes and try alternative fix approach.

### Step 4: Loop Termination Judgment (one of two)

1. **Convergence termination**: All acceptance criteria fully satisfied → immediately stop loop
2. **Upper-limit termination**: Iteration count reaches user-specified maximum → force stop; output current best version; mark remaining unresolved issues

### Step 5: Loop Summary

After loop ends, uniformly output:

```
【Loop Complete Summary】
- Total iterations: [N rounds] ([max M, early convergence exit] or [reached max limit])
- Convergence status: [All criteria met / Partial / Failed]

Metric convergence record:
| Round | [Metric 1] | [Metric 2] | Meets Criteria? |
|-------|-------------|-------------|-----------------|
| 0     | [baseline] | [baseline] | No              |
| ...   | ...         | ...         | ...              |

Final changes:
- Files modified: [list all files with change summary]
- Lines added/removed: [statistics]

Final validation metrics: [all criteria with numeric values]

Remaining risks: [list or "None"]

Optimal result: [attached complete code/document]
```

## Built-in Hard Constraints

1. **Do not arbitrarily expand requirements**: Only iterate around the given loop goal; do not add unrelated features
2. **Minimum modification principle**: Each iteration only fixes defect points; no global large-scale refactoring
3. **Complete traceability**: Each round of modifications must annotate file path, line number, and change reason
4. **Do not silently loop**: Each iteration actively synchronizes progress; inform current metrics and gaps
5. **Fault tolerance control**: Single round encounters fatal environment failure (tool timeout, missing files), automatically log and attempt compatible fix; after 3 consecutive failures, pause loop and ask user to confirm handling plan
6. **Metric quantization**: All validation results must output numerical values; reject vague descriptions like "some improvement"
7. **Rollback safety**: If optimization worsens metrics, automatically rollback and try alternative approach

## Error Handling

### Tool Execution Failures

When a tool execution fails:
1. Log the error with full context (tool name, parameters, error message)
2. Check if error is retryable (timeout, temporary network issue)
3. For retryable errors: retry up to 2 times with exponential backoff
4. For non-retryable errors: pause loop, report to user with options

### Environment Failures

When environment issues occur (missing dependencies, permission errors):
1. Attempt automatic fix (install dependency, request permission)
2. If automatic fix fails, pause loop and present options to user
3. After 3 consecutive environment failures, force terminate loop

### Metric Calculation Errors

When metrics cannot be calculated:
1. Use alternative metric if available
2. If no alternative, mark round as "inconclusive" and continue
3. After 2 consecutive inconclusive rounds, pause and ask user

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
4. If loop paused due to errors, clearly explain pause reason and await user decision

## Differentiation from `/goal` Skill

| Aspect | `/goal` | `/loop` |
|--------|----------|----------|
| Execution | Single complete task, execute once and done | Multiple automatic iterations with retry |
| Retry | No automatic retry | Automatic fix → re-execute cycles |
| Goal | Deliver runnable output | Metric convergence through iteration |
| Use case | One-time development tasks | Tuning, prompt iteration, bug batch fix, strategy backtest optimization |
| Output | Final code/document | Complete iteration history + final output |

## Integration with Other Skills

### With `goal` Skill
- Use `goal` for initial implementation
- Use `loop` for iterative optimization of the implemented solution

### With `skill-creator`
- After creating a skill with `skill-creator`, use `loop` to iteratively optimize the skill based on testing feedback

### With `grill-me` Skill
- Use `grill-me` to critically evaluate your approach before starting loop iterations
- Incorporate feedback from `grill-me` into loop optimization criteria

## Example Execution

### Example 1: Code Optimization

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

**Sample iteration output**:
```
【Round 1 Iteration】
- Defects identified: 
  1. Using simple moving average, should use EWMA
  2. Lookback period too short (10 days), should be 20 days
- Modifications made: 
  - volatility_calc.py:15 → Changed from SMA to EWMA
  - volatility_calc.py:18 → Changed lookback from 10 to 20
- Retest results: 
  - Prediction error: 8.7% → 5.1% (improvement: -3.6%)
- Improvement: -3.6%
- Currently meets criteria? No (5.1% > 3%)
```

**Final output after convergence**:
```
【Loop Complete Summary】
Total iterations: 3 rounds (max 5, early convergence exit)

Metric convergence record:
| Round | Prediction Error | Meets Criteria? |
|-------|-----------------|  ---------------|
| 0     | 8.7%            | No              |
| 1     | 5.1%            | No              |
| 2     | 4.3%            | No              |
| 3     | 2.1%            | Yes             |

Final changes:
- Files modified: volatility_calc.py
- Lines added/removed: +12/-8

Final validation metrics:
- Prediction error: 2.1% (<3% ✓)

Remaining risks: None

Optimal result: [attached complete code]
```

### Example 2: Prompt Optimization

**User input**:
```
/loop optimize futures analysis prompt | hallucination rate ≤5%, logic accuracy ≥65% | maximum 8 rounds
```

This triggers a prompt optimization loop with detailed hallucination and accuracy metrics tracking.

## Troubleshooting

### Loop Stuck (No Progress)

**Symptoms**: Metrics not improving after 3+ rounds

**Possible causes**:
1. Optimization approach is wrong
2. Task requires fundamental different approach
3. Metrics calculation is incorrect

**Solutions**:
1. Pause loop and review optimization approach
2. Consider restarting with different initial strategy
3. Validate metrics calculation logic

### Metrics Worsening

**Symptoms**: Each iteration makes metrics worse

**Possible causes**:
1. Over-optimization (overfitting)
2. Fix is incorrect
3. Metrics have hidden dependencies

**Solutions**:
1. Enable rollback mechanism (automatic in this skill)
2. Reduce iteration step size (smaller changes per round)
3. Add regularization to prevent over-optimization

### Environment Instability

**Symptoms**: Frequent tool timeouts or failures

**Possible causes**:
1. Network issues
2. Resource constraints
3. Tool bugs

**Solutions**:
1. Add retry logic with exponential backoff
2. Switch to more stable tools
3. Reduce parallel operations

## Best Practices

1. **Start with clear metrics**: Ensure success criteria are quantifiable before starting
2. **Use small iteration steps**: Smaller changes are easier to attribute and rollback
3. **Validate metrics calculation**: Ensure metrics accurately reflect task success
4. **Set reasonable iteration limits**: Balance between optimization depth and time cost
5. **Review iteration history**: Use iteration history to identify patterns and improve approach
6. **Consider computational cost**: Some optimizations may require expensive re-computation

## Limitations

1. **Metric dependency**: Requires quantifiable success metrics; cannot optimize subjective tasks
2. **Local optimum risk**: May converge to local optimum, not global optimum
3. **Computational cost**: Each iteration may require expensive re-computation
4. **Overfitting risk**: Excessive iterations may overfit to validation data
5. **No creativity**: Optimizes within defined parameter space; cannot invent new approaches

## Version History

- **v1.0.1** (current): Enhanced with error handling, rollback mechanism, troubleshooting, and best practices
- **v1.0.0**: Initial release with core loop functionality
