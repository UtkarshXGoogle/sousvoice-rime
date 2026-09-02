# Rime Evidence — SousVoice

## 1. Project

**Project:** SousVoice  
**Use case:** Hands-free cooking assistant  
**Hard voice problem:** Interruption and recovery during in-flight tool work

SousVoice is a voice-native cooking assistant that guides a user through a
recipe using spoken interaction.

The user can ask for the next recipe step and can interrupt the interaction
with another spoken request.

---

## 2. Hard Voice Problem

### Interruption and Recovery

The primary voice-engineering challenge addressed by SousVoice is:

> What happens when the user interrupts an in-flight recipe operation with a
> new spoken request?

A naive voice assistant can continue processing the original request and later
deliver a stale result even though the user has already changed the request.

SousVoice is designed to prevent this by:

1. Detecting the user's interruption.
2. Cancelling or reconciling the in-flight tool operation.
3. Preventing an interrupted recipe step from advancing application state.
4. Processing the user's new request.
5. Keeping the recipe state consistent with the interaction.

The application uses LiveKit Agents for realtime turn handling and tool
orchestration. Rime provides the primary spoken output.

---

## 3. Why Voice Is Necessary

Cooking is a hands-busy activity.

A user may be holding ingredients, utensils, or cookware and may not want to
touch a phone or computer while following a recipe.

SousVoice therefore uses voice as the primary interaction mechanism:

- The user gives commands using speech.
- Recipe instructions are delivered using speech.
- The user can interrupt the assistant using speech.
- Rime provides the primary spoken output.

Removing voice would materially reduce the usefulness of SousVoice in its
target cooking situation.

---

## 4. Architecture

```text
                Microphone
                     |
                     v
                Deepgram STT
                     |
                     v
              LiveKit Agents
                     |
                     v
                  Groq LLM
                     |
                     v
             Recipe Tools/State
                     |
                     v
                  Rime TTS
                     |
                     v
                User hears
                  response
```
## 5. Rime Integration

Rime is used as the primary text-to-speech provider in the shipped agent.

Current application configuration:

```python
tts=rime.TTS(
    speaker="lyra",
    model="coda",
)
```

## 6. Acceptance Test

The acceptance test focuses on interruption and recovery while a recipe tool
is actively performing work.

Test A — Normal interaction
Start a fresh SousVoice session.
Say Next.
Allow the tool operation to finish.
Verify that the recipe step is returned.
Verify that the application state advances by one step.

Expected log pattern:

NEXT_STEP_START step=N
NEXT_STEP_COMPLETE step=N current_step=N
Test B — Interruption
Start a fresh SousVoice session.
Enable stress-test mode.
Say Next.
Interrupt the operation while the tool is still waiting.
Verify that the interrupted operation does not advance recipe state.
Verify that the new user request is processed.

Expected log pattern:

NEXT_STEP_START step=N
NEXT_STEP_INTERRUPTED step=N current_step=N-1

The critical condition is that current_step remains unchanged after the
interruption.

Test C — Continued interaction

After the interruption has been handled:

Give another Next request.
Allow the operation to complete.
Verify that the voice session remains usable.
Verify that recipe processing continues.

Expected log pattern:

NEXT_STEP_START step=N
NEXT_STEP_COMPLETE step=N current_step=N

## 7. Stress-Test Configuration

The application supports a dedicated stress-test mode through an environment
variable:

STRESS_TEST=true

When stress-test mode is enabled, next_step introduces a deliberate fixed
delay before committing the recipe state.

The delay creates a deterministic window in which the user can interrupt the
operation.

This delay is a testing mechanism and is not intended to represent normal
recipe-processing latency.

Normal operation can run with:

STRESS_TEST=false

##8. Test Environment

The observed tests were performed using:

Local Python SousVoice agent
LiveKit Agents
LiveKit Agents Playground
Browser microphone
Deepgram STT
Groq LLM
Rime TTS
Silero VAD
Simple Pancakes recipe fixture

The agent was started locally with:

python agent.py dev

The LiveKit Playground was used as the realtime interaction interface.

## 9. Interruption Test Procedure

The interruption test was performed as follows:

Start the local SousVoice agent.
Enable:
STRESS_TEST=true
Connect to the LiveKit Playground.
Start a fresh recipe session.
Say:
Next
While the artificial delay is still active, interrupt with a new spoken
request such as:
Wait.
Observe the application logs.
Ask the new question, for example:
How many minutes?
Allow SousVoice to respond.
Continue the recipe with another Next request.

## 10. Observed Interruption Result

A successful interruption test produced the following application log
sequence:

NEXT_STEP_START step=1
NEXT_STEP_INTERRUPTED step=1 current_step=0

The important observation is:

current_step=0

after the interruption.

This means the interrupted Step 1 operation did not commit the recipe-state
transition.

The Playground also showed the user's new request being received after the
interruption.

SousVoice then responded to the new request instead of continuing with the
stale interrupted operation.

Result

The interruption test passed for the tested case:

The in-flight recipe operation was interrupted.
The interrupted step did not advance application state.
The new user request was accepted.
The voice session continued to operate after the interruption.

## 11. Continued Interaction Result

A subsequent recipe interaction produced:

NEXT_STEP_START step=2
NEXT_STEP_COMPLETE step=2 current_step=2

The Playground delivered the corresponding recipe instruction:

Step 2: Add 1 cup milk, 1 egg, and 2 tablespoons melted butter.
Whisk until smooth.

This demonstrates that the agent remained usable after the interruption and
continued processing subsequent recipe requests.

The evidence does not claim that this particular run re-delivered the exact
same interrupted step; it demonstrates successful continued recipe
interaction after the interruption.

## 12. State Consistency

The state-management rule implemented in next_step is:

Start operation
      |
      v
Capture current recipe step
      |
      v
Perform in-flight work
      |
      +----------------------+
      |                      |
      v                      v
Interrupted              Completed
      |                      |
      v                      v
Cancel work              Advance state
      |                      |
      v                      v
Do NOT advance           Return step
state

The recipe state is therefore mutated only after the delayed operation has
successfully completed.

When an interruption occurs, the operation returns without advancing
current_step.

## 13. Relevant Application Logs
Successful normal execution

Observed during testing:

NEXT_STEP_START step=1
NEXT_STEP_COMPLETE step=1 current_step=1
Successful interruption

Observed during testing:

NEXT_STEP_START step=1
NEXT_STEP_INTERRUPTED step=1 current_step=0
Continued execution

Observed during subsequent testing:

NEXT_STEP_START step=2
NEXT_STEP_COMPLETE step=2 current_step=2

These logs are generated by the application itself and make the interruption
behavior observable and reproducible.

## 14. Reproducibility
Start the agent
python agent.py dev
Enable stress-test mode

Set:

STRESS_TEST=true
Test sequence
1. Connect LiveKit Playground
2. Start recipe
3. Say "Next"
4. Interrupt while the tool is in-flight
5. Observe NEXT_STEP_INTERRUPTED
6. Ask the new question
7. Say "Next"
8. Observe subsequent NEXT_STEP_START / NEXT_STEP_COMPLETE
Expected interruption evidence
NEXT_STEP_START step=N
NEXT_STEP_INTERRUPTED step=N current_step=N-1

The exact step number depends on the current recipe state.

## 15. Limitations

This evidence demonstrates the tested interruption path but does not establish
universal performance across all devices, microphones, networks, languages,
or audio environments.

Current limitations include:

Testing was performed through the browser-based LiveKit Playground.
Testing used a browser microphone rather than telephony audio.
The stress-test delay is artificial and exists to create a deterministic
interruption window.
The current recipe is a local fixture rather than a production recipe
database.
The current evidence does not claim a specific interruption latency
measurement.
Performance measurements should only be reported after measuring the final
shipped path.

##16. Security

Credentials are provided through environment variables and are not intended
to be stored in source code.

Secrets must not be included in:

Source files
Documentation
Screenshots
Demo recordings
Client-side code
Git history

The repository should contain an .env.example file containing placeholders
only.

## 17. Evidence Summary
Hard voice problem

Interruption and recovery during in-flight recipe operations.

Acceptance criterion

When the user interrupts an in-flight recipe operation:

The operation must not commit an obsolete recipe-state transition.
The user's new request must be accepted.
The stale interrupted operation must not become the active response.
The voice session must remain usable afterward.
Subsequent recipe interaction must continue from consistent application
state.
Observed interruption
NEXT_STEP_START step=1
NEXT_STEP_INTERRUPTED step=1 current_step=0
Observed subsequent interaction
NEXT_STEP_START step=2
NEXT_STEP_COMPLETE step=2 current_step=2
Overall result

The tested interruption case demonstrated that an in-flight recipe operation
could be interrupted without advancing the recipe state, while the voice
session continued to accept and process subsequent user requests.

## 18. Final Submission Note

Before submission, verify and document the exact Rime configuration used in the
recorded demo:

Rime model ID
Rime speaker
Language
Endpoint
Audio format
Transport
Active speech provider during the demo
Final repository configuration
Final reproducible test procedure
