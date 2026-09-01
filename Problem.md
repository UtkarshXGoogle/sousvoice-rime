# SousVoice — Problem Statement

## User
A home cook actively cooking in the kitchen — hands busy or dirty 
with dough, batter, or raw meat. They cannot touch a phone or 
tablet without washing their hands first.

## Situation
The user is following a recipe step-by-step. Midway through, they 
have a question (measurement conversion, substitution, timing) and 
need a quick answer without re-reading the whole recipe — but 
touching the screen isn't an option.

## Why voice is essential (not optional)
Remove voice, and the product becomes unusable at the exact moment 
it's needed most — when hands are dirty. No visual UI can substitute 
for this. This isn't a "chatbot with a play button" — the entire 
normal-flow interaction has to be voice-only.

## Hard voice problem chosen: Interruption and Recovery
When Rime is mid-sentence reading step 3 and the user interrupts 
with an unrelated question, the system must:
- Immediately stop the stale audio
- Answer the question correctly
- Resume at the exact step where it left off
- Keep internal state consistent with what the user actually heard, 
  not with what the system was mid-sentence saying

This matters because if the system resumes at the wrong step or 
repeats itself, the user loses trust and gets confused mid-recipe — 
at a moment when scrolling back to check isn't even possible.
