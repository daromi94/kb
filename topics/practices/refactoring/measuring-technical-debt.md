# Measuring technical debt

"Code smell" is subjective; technical debt should be measurable. Before
starting a refactor, define the ROI with objective metrics.

## Metrics that matter

| Metric          | Question                                            |
|-----------------|-----------------------------------------------------|
| Maintainability | Will this reduce onboarding time for new devs?      |
| Bug density     | Is this module a hotspot for regressions?           |
| Performance     | Does the architecture block scaling or add latency? |

## Aesthetic vs objective

| Justification                 | Type      | Sufficient? |
|-------------------------------|-----------|-------------|
| "It's ugly"                   | Aesthetic | No          |
| "I don't understand it"       | Aesthetic | No          |
| "Cyclomatic complexity is 47" | Objective | Yes         |
| "3 bugs in this file/month"   | Objective | Yes         |
| "Can't add feature X"         | Objective | Yes         |

If you can't quantify the problem, you may be optimizing for personal
preference rather than system health.

---

Return to [Refactoring](_index.md)
