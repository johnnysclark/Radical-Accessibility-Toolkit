# Verifying Maquette on the Mac

Run these once on the Mac with Rhino 8 installed. Steps 1 to 6 are
automated by `python3 maquette/scripts/mac_verify.py`; the rest need
human ears. Every step says what you should hear.

## 1. Install

    pip install -e "maquette[headless,mcp,chat]"
    maquette version

Hear: OK: maquette 0.1.0.

## 2. Listener setup (one time)

    maquette install-listener

Follow the four printed steps: in Rhino Settings, General, add the
startup command it prints (the `_-ScriptEditor _R "..."` line), plus
`_StartScriptServer` on a second line, then restart Rhino. Rhino's
command line should say: [Maquette] Listening on 127.0.0.1:6270.

## 3. Doctor

    maquette doctor

Hear: every line OK (rhinocode line may be a WARNING on Rhino older
than 8.11). Exit code 0.

## 4. Automated round trip

    python3 maquette/scripts/mac_verify.py

Hear: PASS on every line, then RESULT: n passed, 0 failed. This
creates a box in Rhino, measures it, moves it, queries it back, and
undoes it.

## 5. First real model

    maquette init tower && cd tower
    maquette box 10 10 30 at 0,0,0 name "tower base"
    maquette describe object "tower base"

Watch Rhino: the box appears as the OK line is spoken. The describe
size matches 10 by 10 by 30 and says quality measured.

## 6. Booleans evaluate live

    maquette sphere radius 6 at 5,5,30
    maquette union "tower base" m2
    maquette describe

Hear: the union is created with no pending note (live computes it).

## 7. Crash recovery (the big one)

Force-quit Rhino mid-session (Command Option Escape). Then:

    maquette describe        <- still works, from the journal
    (reopen Rhino, wait for the listener line)
    maquette rebuild

Hear: rebuilt N journal steps on backend live, objects realized, and
the model is back in Rhino. WARNING lines only for script ops that
moved (drift detection working).

## 8. No-GUI listener recovery

    maquette listener-stop
    maquette connect --inject

Hear: the listener comes back without touching the Rhino interface.
(Needs `_StartScriptServer` from step 2 and Rhino 8.11 or newer.)

## 9. VoiceOver contract

With VoiceOver in Terminal.app, run `maquette describe --all` and
`maquette journal`. Every line should read cleanly: no symbols, no
tables, short lines, OK or ERROR up front, READY at the end.

## 10. Chat

    maquette chat
    maq> box 2 2 2 name "test cube"        <- instant OK line
    maq> ask Claude to put a pyramid on the test cube
    maq> /transcript
    maq> /quit

Hear: "OK: asking Claude.", then each tool confirmation as it lands,
then Claude's reply read in full (no word-by-word streaming), then
READY:. The transcript file exists and reads back the whole session.

If any step fails, `maquette doctor` first; it knows the fixes.
