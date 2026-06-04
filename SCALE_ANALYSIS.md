# Scale Analysis: 50 vs 300 Documents

## Question: Is 50 documents insufficient for simulating 300?

**Answer: Yes, 50 is insufficient for realistic simulation of 300.**

## Why Scale Matters

Problems that don't exist at 50 become critical at 300:

| Phenomenon | At 50 | At 300 | Mitigation |
|------------|-------|--------|------------|
| State file I/O | ~0.1s | ~2s | SQLite required |
| Ollama queue buildup | 10 min total | 60 min total | Circuit breaker + batching |
| Error rate (5% failure) | 2–3 files | 15 files | Retry + quarantine |
| Memory pressure | Negligible | Extracted text accumulates | Streaming + chunking |
| Graph view pollution | Minor | Severe | Proper vault routing |
| Review queue overwhelm | Manageable | Paralysis | Backpressure pause |

## The Statistical Argument

With 50 documents, you see **individual file behaviors**. With 300, you see **systemic behaviors**:

- **Long-tail latency:** One PDF that takes 5 minutes to extract is an anomaly at 50. At 300, it's a guaranteed occurrence.
- **Error clustering:** Network blips or Ollama memory pressure cause correlated failures. You need enough volume to observe this pattern.
- **Confidence distribution:** With 50 samples, the sigmoid normalization is unstable. With 300, you get a reliable distribution curve.

## Recommended Scale Tiers

| Tier | Document Count | Purpose |
|------|---------------|---------|
| Unit test | 1 | Validate single-file logic |
| Integration test | 10 | Validate pipeline end-to-end |
| Validation | 50 | Verify output quality, tag accuracy |
| Stress test | 300 | Find bottlenecks, measure throughput |
| Production simulation | 500+ | Evaluate review queue, routing accuracy |

## Proposed Simulation Strategy

Instead of jumping from 50 to 300 real documents, use **synthetic scaling**:

1. **Duplicate test files with variations:** Copy your 50 real files 6 times with randomized names. This tests the pipeline mechanics at 300 without needing 300 real documents.
2. **Vary document sizes:** Ensure the 300 include small (100 words), medium (2,000 words), and large (10,000+ words) documents in realistic proportions.
3. **Inject failure modes:** Deliberately include 5% corrupted files, 5% extremely large files, and 5% encoding-mismatched files. This tests resilience.

## Conclusion

50 documents validates that the pipeline *works*. 300 documents reveals how it *behaves under load*. Both are necessary, but they answer different questions.

**Recommendation:**
- Validate with 50 real files this week
- Stress test with 300 synthetic files next week
- Tune batch size, timeouts, and backpressure based on the 300-file run
- Then process real documents at the tuned rate
