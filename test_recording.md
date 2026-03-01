# Manual Testing Checklist for Workout Recording Feature

## Setup
1. Start the Flask server:
   ```bash
   python web_app.py
   ```
2. Open browser to http://127.0.0.1:5000

## Test 1: Basic Recording with Single Round
**Goal:** Verify recording starts, tracks reps, and saves correctly

**Steps:**
1. Click "Save Workout" button
   - ✓ Button should change to "Stop Recording"
   - ✓ Status message shows "Recording started"
2. Perform 10 jumping jacks (or wait for counter to increment to 10)
3. Wait 8 seconds (to trigger inactivity round close)
4. Click "Stop Recording"
   - ✓ Status message shows "Saved: 1 rounds, 10 total reps"
   - ✓ Button returns to "Save Workout"
5. Click "View History" to verify session was saved
   - ✓ Should see 1 session with 10 total reps
   - ✓ Should show 1 round with 10 reps

## Test 2: Multiple Rounds via Inactivity
**Goal:** Verify rounds auto-close after inactivity

**Steps:**
1. Click "Save Workout" to start recording
2. Do 5 jumping jacks
3. Wait 8 seconds (round should auto-close)
4. Do 8 more jumping jacks
5. Wait 8 seconds (round should auto-close)
6. Do 7 more jumping jacks
7. Click "Stop Recording"
   - ✓ Status should show "Saved: 3 rounds, 20 total reps"
8. Check history:
   - ✓ Should show 3 rounds: 5, 8, 7 reps

## Test 3: Multiple Rounds via Counter Reset
**Goal:** Verify rounds close when counter resets to 0

**Steps:**
1. Click "Save Workout" to start recording
2. Do 12 jumping jacks
3. Click "Reset Counter" (should close round)
4. Do 8 jumping jacks
5. Click "Reset Counter" (should close round)
6. Click "Stop Recording"
   - ✓ Status should show "Saved: 2 rounds, 20 total reps"
7. Check history:
   - ✓ Should show 2 rounds: 12, 8 reps

## Test 4: Empty Recording
**Goal:** Verify "nothing to save" works correctly

**Steps:**
1. Click "Save Workout" to start recording
2. Immediately click "Stop Recording" (without doing any reps)
   - ✓ Status should show "Nothing to save"
   - ✓ Button returns to "Save Workout"
   - ✓ No session saved to database

## Test 5: Recording Doesn't Break Normal Counting
**Goal:** Verify counter works normally when NOT recording

**Steps:**
1. Do NOT click "Save Workout"
2. Do 15 jumping jacks
   - ✓ Counter should increment normally on screen
3. Wait for inactivity reset
   - ✓ Counter should reset to 0 after 7 seconds
4. Do 10 more jumping jacks
   - ✓ Counter should work normally
5. Click "View History"
   - ✓ No new sessions should appear (nothing was recorded)

## Test 6: View All Sessions
**Goal:** Verify GET /api/sessions returns all data

**Steps:**
1. After completing Tests 1-3, check history page
2. Should see at least 3 sessions listed
3. Each session should show:
   - ✓ Date/time
   - ✓ Total reps
   - ✓ Number of rounds
   - ✓ Individual round breakdown with reps

## Test 7: API Direct Test (Optional)
**Goal:** Test POST endpoint directly

**Steps:**
1. Open terminal, run:
   ```bash
   curl -X POST http://127.0.0.1:5000/api/sessions \
     -H "Content-Type: application/json" \
     -d '{
       "total_reps": 25,
       "rounds": [
         {"round_index": 1, "reps": 10, "ended_at": "2026-03-01T12:00:00"},
         {"round_index": 2, "reps": 15, "ended_at": "2026-03-01T12:01:00"}
       ]
     }'
   ```
2. ✓ Should return: `{"ok": true, "session_id": <number>}`
3. Verify in history page

## Known Configuration
- INACTIVITY_SECONDS = 7 (configurable in index.html line 289)
- Counter polling interval = 200ms
- Inactivity check interval = 250ms

## Edge Cases to Watch For
- Button should disable briefly during save (prevents double-click)
- Multiple rapid clicks on "Save Workout" should not cause issues
- Refreshing page during recording should reset state
- Counter reset during recording should properly close round
