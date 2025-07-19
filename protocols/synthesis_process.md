# Protocol: Synthesis of Sub-problem Solutions

## Purpose
Define how to combine insights from multiple Ollama conversations into coherent solutions.

## Synthesis Process

### 1. Collection Phase
- Gather all completed sub-problem responses
- Extract key insights from each
- Note any contradictions or tensions
- Identify common themes

### 2. Organization Phase
- Group related insights
- Order by logical dependencies
- Separate fundamental insights from implementation details
- Flag areas needing clarification

### 3. Integration Phase
- Resolve contradictions through analysis
- Build coherent narrative
- Create actionable recommendations
- Identify remaining unknowns

### 4. Validation Phase
- Check solution completeness
- Verify internal consistency
- Test against original problem
- Consider edge cases raised

## Synthesis Patterns

### Pattern 1: Building Blocks
When sub-problems are independent:
1. Each solution becomes a module
2. Define interfaces between modules
3. Compose into complete system

### Pattern 2: Layered Insights
When sub-problems build on each other:
1. Foundation insights first
2. Build up through layers
3. Top layer addresses full complexity

### Pattern 3: Convergent Analysis
When exploring alternatives:
1. Compare different approaches
2. Extract best elements from each
3. Create hybrid solution

### Pattern 4: Dialectic Resolution
When solutions conflict:
1. Thesis: Solution A
2. Antithesis: Solution B
3. Synthesis: New approach incorporating both

## Synthesis Document Template

```markdown
# Synthesis: [Original Problem]

## Sub-problems Analyzed
1. [Sub-problem 1] - Model: [model], Time: [duration]
2. [Sub-problem 2] - Model: [model], Time: [duration]
...

## Key Insights

### From [Sub-problem 1]:
- [Insight 1]
- [Insight 2]

### From [Sub-problem 2]:
- [Insight 1]
- [Insight 2]

## Integrated Solution

### Core Approach
[Narrative description combining insights]

### Implementation Strategy
1. [Step derived from insights]
2. [Step derived from insights]

### Trade-offs Identified
- [Trade-off from sub-problem X]
- [Trade-off from sub-problem Y]

## Unexpected Discoveries
- [Dimension not originally considered]
- [Connection between seemingly unrelated aspects]

## Remaining Questions
- [Question that emerged from synthesis]
- [Area needing further exploration]

## Confidence Assessment
- High confidence: [aspects well-supported by multiple insights]
- Medium confidence: [aspects with some support]
- Low confidence: [aspects needing more analysis]
```

## Quality Indicators

### Good Synthesis
- ✓ Insights build on each other
- ✓ Contradictions are resolved
- ✓ Solution addresses original problem
- ✓ New understanding emerges
- ✓ Clear next steps

### Poor Synthesis  
- ✗ Just concatenating responses
- ✗ Ignoring contradictions
- ✗ Missing connections
- ✗ No emergent insights
- ✗ Unclear action items

## Meta-Synthesis Option

For complex problems, consider asking Ollama to synthesize:

```
Here are solutions to sub-problems of [original problem]:

[Sub-problem 1]: [solution summary]
[Sub-problem 2]: [solution summary]
...

How do these fit together? What's the overall solution?
```

This can reveal connections you might miss.

## Storage and Learning

- Save synthesis documents in Obsidian
- Tag with: #synthesis #[problem-domain] #[date]
- Link to original sub-problem conversations
- Build library of synthesis patterns for future use
