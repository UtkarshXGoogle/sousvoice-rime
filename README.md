# SousVoice

**Hands-free cooking assistant powered by Rime TTS**

SousVoice is a voice-native cooking assistant that guides users through a
recipe without requiring them to touch a screen.

The primary voice-engineering problem solved by SousVoice is **interruption
and recovery during in-flight recipe operations**.

A user can start a recipe step and interrupt the assistant with a new spoken
request. SousVoice prevents the interrupted recipe operation from incorrectly
advancing application state and continues the conversation with the user's
new request.

---

## Problem

Cooking is a hands-busy activity. Users may be holding ingredients, utensils,
or cookware and may not want to interact with a phone or computer while
following a recipe.

SousVoice allows the user to control recipe progression using speech.

The key engineering challenge is not simply speech recognition or
text-to-speech. It is maintaining correct application state when the user
interrupts an operation that is already in progress.

See [PROBLEM.md](./Problem.md) for the problem definition.

See [RIME_EVIDENCE.md](./RIME_EVIDENCE.md) for the acceptance test and observed
interruption results.

---

## Hard Voice Problem

### Interruption and Recovery

The acceptance scenario is:

```text
User: "Next"
        |
        v
Recipe operation starts
        |
        v
User interrupts with a new request
        |
        v
In-flight operation is interrupted
        |
        v
Recipe state is NOT advanced
        |
        v
New request is processed
        |
        v
User can continue the recipe
```

The critical requirement is that an interrupted operation must not leave stale
application state behind.

---

## Architecture

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
Recipe Tools + State
    |
    v
Rime TTS
    |
    v
User hears response
```

### Components

| Component | Role |
|---|---|
| LiveKit Agents | Realtime voice session, turn handling, interruption handling, and tool orchestration |
| Deepgram | Speech-to-text |
| Groq | Language model |
| Rime | Primary text-to-speech provider |
| Silero VAD | Voice activity detection |
| Python | Application logic and recipe state |

---

## Rime Integration

Rime provides the primary spoken output of SousVoice.

Current application configuration:

```python
tts=rime.TTS(
    speaker="lyra",
    model="coda",
)
```

### Rime configuration

| Setting | Value |
|---|---|
| Provider | Rime |
| Model | `coda` |
| Speaker | `lyra` |
| Language | To be verified from final shipped configuration |
| Endpoint | To be verified from final shipped configuration |
| Audio format | To be verified from final shipped configuration |
| Transport | To be verified from final shipped configuration |

The final submission documentation will use the exact configuration exercised
during the recorded demo.

---

## Interruption Handling

SousVoice uses LiveKit's speech interruption state to coordinate in-flight
application work.

The `next_step` tool captures the current recipe step before beginning the
operation.

When stress-test mode is enabled, a deliberate delay creates a deterministic
window for the user to interrupt the operation.

State is only advanced after the operation successfully completes.

```text
Start operation
      |
      v
Capture current step
      |
      v
In-flight work
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
```

This prevents an interrupted operation from consuming a recipe step that was
never successfully delivered.

---

## Stress-Test Mode

The repository supports a dedicated interruption stress test.

Enable it through the environment:

```env
STRESS_TEST=true
```

When enabled, the `next_step` tool introduces a deliberate fixed delay before
committing recipe state.

This delay exists only to make interruption testing deterministic. It is not
intended to represent normal recipe-processing latency.

Normal operation:

```env
STRESS_TEST=false
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/UtkarshXGoogle/sousvoice-rime.git
cd sousvoice-rime
```

### 2. Create a Python virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

If a `requirements.txt` file is present:

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

```env
STRESS_TEST=false
```

Add the required LiveKit, Deepgram, Groq, and Rime credentials to your local
`.env` file.

**Never commit real API keys or credentials to GitHub.**

### 5. Start the agent

```bash
python agent.py dev
```

### 6. Open the LiveKit Playground

Connect the local agent through the LiveKit Agents Playground and allow
microphone access.

---

## Reproducing the Interruption Test

Enable stress-test mode:

```env
STRESS_TEST=true
```

Start the agent:

```bash
python agent.py dev
```

Then:

1. Connect to the LiveKit Playground.
2. Start a fresh recipe session.
3. Say **"Next"**.
4. Interrupt the operation while the artificial delay is active.
5. Ask a new question such as **"How many minutes?"**.
6. Allow SousVoice to answer.
7. Say **"Next"** again.
8. Observe the application logs.

Expected interruption log:

```text
NEXT_STEP_START step=N
NEXT_STEP_INTERRUPTED step=N current_step=N-1
```

Expected subsequent successful interaction:

```text
NEXT_STEP_START step=N
NEXT_STEP_COMPLETE step=N current_step=N
```

See [RIME_EVIDENCE.md](./RIME_EVIDENCE.md) for the detailed acceptance test,
observed logs, and limitations.

---

## Example Interaction

```text
SousVoice:
Starting recipe: Simple Pancakes. Say "next" when you're ready for step one.

User:
Next

SousVoice:
Step 1...

User:
Wait! How many minutes?

SousVoice:
[Answers the new request]

User:
Next

SousVoice:
[Continues the recipe]
```

The important behavior is that the interrupted recipe operation does not
incorrectly advance the recipe state.

---

## Evidence

The repository contains:

- `RIME_EVIDENCE.md` — acceptance test, interruption evidence, logs, and
  limitations
- `Problem.md` — problem definition
- `agent.py` — voice agent and interruption-aware recipe tool
- `recipe.py` — recipe fixture
- `test_rime.py` — Rime-related testing
- `.env.example` — environment configuration template

---

## Known Limitations

- The current recipe is a local Python fixture rather than a production recipe
  database.
- The interruption stress test uses an artificial delay to create a
  deterministic testing window.
- Testing has been performed through the browser-based LiveKit Playground.
- Testing uses browser microphone input rather than telephony audio.
- The demonstrated behavior does not establish universal performance across
  all devices, microphones, networks, or audio environments.
- No specific interruption-latency claim is made without a measurement from
  the final shipped path.
- The final demo should use the exact Rime configuration documented in the
  submission.

---

## Security

API credentials are loaded through environment variables.

Real credentials must never be placed in:

- Source code
- README files
- Evidence files
- Screenshots
- Demo recordings
- Client-side code
- Git history

Use `.env.example` for placeholder configuration only.

---

## Project Structure

```text
sousvoice-rime/
|
├── agent.py
├── recipe.py
├── test_rime.py
├── Problem.md
├── RIME_EVIDENCE.md
├── README.md
├── .env.example
└── .gitignore
```

---

## Status

### Core voice flow

- [x] LiveKit voice session
- [x] Deepgram speech-to-text
- [x] Groq LLM integration
- [x] Rime TTS integration
- [x] Recipe state management
- [x] `next_step` tool
- [x] `repeat_step` tool
- [x] Interruption detection
- [x] In-flight operation cancellation/reconciliation
- [x] State preservation after interruption
- [x] Subsequent conversation after interruption
- [x] Interruption evidence documented

### Final submission

- [ ] Verify final Rime language
- [ ] Verify Rime endpoint
- [ ] Verify Rime audio format
- [ ] Verify Rime transport
- [ ] Finalize reproducible evidence
- [ ] Record final demo
