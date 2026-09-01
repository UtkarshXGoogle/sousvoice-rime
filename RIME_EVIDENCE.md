# RIME_EVIDENCE.md (Draft — before build)

## Claim
SousVoice handles barge-in interruption immediately — stops queued 
Rime audio, answers the unrelated question correctly, and resumes 
at the exact correct step — without corrupting state.

## Acceptance Test

### Normal flow
1. User says: "start recipe"
2. Rime reads out step 1
3. User says: "next" → Rime reads out step 2
4. Repeat for step 3

### Stress / failure case
1. While Rime is speaking step 3 (mid-sentence, before it completes)
2. User interrupts: "how many grams is that in cups?"
3. The system must immediately stop the queued Rime audio

## Measurements (pass/fail criteria)
| # | Metric | Target |
|---|--------|--------|
| 1 | Time from interrupt to audio-stop | < 300ms |
| 2 | Stale step-3 audio does not finish playing | Audio must stop mid-sentence |
| 3 | Question is answered correctly | Manual check |
| 4 | Resume happens at exact step 3 (not step 4 or step 1) | Exact match |
| 5 | Internal state (step index) is consistent with what the user actually heard | Exact match |

## Procedure
- A fixed script/fixture will be used: interrupt triggered at an 
  exact, repeatable timing (hardcoded delay or automated test)
- Run 3 times, log the values each time
- Save audio clips (before/after) as evidence

## Result
[To be filled in after build — currently TBD]

## Limitations
[To be filled in after build — e.g. which languages aren't 
supported, how much background noise is tolerated, etc.]
