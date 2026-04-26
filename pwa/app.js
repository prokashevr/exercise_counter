const STORAGE_KEY = 'repsCounterState_v1';

let state = {
    sessionTotalReps: 0,
    currentRoundReps: 0,
    completedRounds: 0,
    roundHistory: [],
    sessionStartedAt: null,
    lastAction: null
};

function loadState() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
            const saved = JSON.parse(raw);
            state = { ...state, ...saved };
        }
    } catch (_) {}
    if (!state.sessionStartedAt) {
        state.sessionStartedAt = new Date().toISOString();
    }
}

function saveState() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (_) {}
}

function render() {
    document.getElementById('stat-session').textContent = state.sessionTotalReps;
    document.getElementById('stat-round').textContent   = state.currentRoundReps;
    document.getElementById('stat-rounds').textContent  = state.completedRounds;

    const listEl = document.getElementById('round-list');
    if (state.roundHistory.length === 0) {
        listEl.innerHTML = '<div class="no-rounds-msg">No rounds completed yet</div>';
    } else {
        listEl.innerHTML = [...state.roundHistory].reverse().map(r =>
            `<div class="round-entry">
                <span class="round-entry-label">Round ${r.roundNumber}</span>
                <span class="round-entry-reps">${r.reps}<span class="unit">reps</span></span>
            </div>`
        ).join('');
    }

    document.getElementById('undo-btn').disabled = !state.lastAction;

    if (state.sessionStartedAt) {
        const started = new Date(state.sessionStartedAt);
        const opts = { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' };
        document.getElementById('session-meta').textContent =
            'Started ' + started.toLocaleString('en-US', opts);
    }
}

function addReps(value) {
    state.lastAction = {
        type: 'chip',
        prevCurrentRoundReps: state.currentRoundReps,
        prevSessionTotalReps: state.sessionTotalReps
    };

    state.currentRoundReps  += value;
    state.sessionTotalReps  += value;

    saveState();
    render();
    flashChip(value);

    if (navigator.vibrate) navigator.vibrate(25);
}

function completeRound() {
    if (state.currentRoundReps === 0) {
        showStatus('Add reps first', 'error');
        return;
    }

    state.lastAction = {
        type: 'complete',
        prevCurrentRoundReps: state.currentRoundReps,
        prevCompletedRounds:  state.completedRounds,
        prevRoundHistory:     state.roundHistory.map(r => ({ ...r })),
        prevSessionTotalReps: state.sessionTotalReps
    };

    state.completedRounds += 1;
    state.roundHistory.push({
        roundNumber: state.completedRounds,
        reps: state.currentRoundReps,
        completedAt: new Date().toISOString()
    });
    state.currentRoundReps = 0;

    saveState();
    render();

    if (navigator.vibrate) navigator.vibrate([40, 20, 40]);
    showStatus(`Round ${state.completedRounds} saved`, 'success');
}

function undoLast() {
    if (!state.lastAction) return;

    const action = state.lastAction;
    state.lastAction = null;

    if (action.type === 'chip') {
        state.currentRoundReps = action.prevCurrentRoundReps;
        state.sessionTotalReps = action.prevSessionTotalReps;
    } else if (action.type === 'complete') {
        state.currentRoundReps = action.prevCurrentRoundReps;
        state.completedRounds  = action.prevCompletedRounds;
        state.roundHistory     = action.prevRoundHistory;
        state.sessionTotalReps = action.prevSessionTotalReps;
    }

    saveState();
    render();
    showStatus('Undone', 'success');
}

function resetRound() {
    if (state.currentRoundReps === 0) return;

    state.sessionTotalReps -= state.currentRoundReps;
    state.currentRoundReps  = 0;
    state.lastAction        = null;

    saveState();
    render();
    showStatus('Round reset', 'success');
}

function resetSession() {
    const hasData = state.sessionTotalReps > 0 ||
                    state.currentRoundReps > 0 ||
                    state.completedRounds  > 0;
    if (!hasData) return;

    if (!confirm('Reset the full session? This cannot be undone.')) return;

    state = {
        sessionTotalReps: 0,
        currentRoundReps: 0,
        completedRounds:  0,
        roundHistory:     [],
        sessionStartedAt: new Date().toISOString(),
        lastAction:       null
    };

    saveState();
    render();
    showStatus('Session reset', 'success');
}

function flashChip(value) {
    const el = document.getElementById(`chip-btn-${value}`);
    if (!el) return;
    el.classList.remove('tapped');
    void el.offsetWidth;
    el.classList.add('tapped');
    el.addEventListener('animationend', () => el.classList.remove('tapped'), { once: true });
}

function showStatus(message, type) {
    const el = document.getElementById('status-msg');
    el.textContent = message;
    el.className = 'status-message show ' + type;
    clearTimeout(el._timer);
    el._timer = setTimeout(() => el.classList.remove('show'), 2500);
}

function bindEvents() {
    document.querySelectorAll('.chip').forEach(btn => {
        btn.addEventListener('click', () => addReps(Number(btn.dataset.value)));
    });
    document.getElementById('complete-btn').addEventListener('click', completeRound);
    document.getElementById('undo-btn').addEventListener('click', undoLast);
    document.getElementById('reset-round-btn').addEventListener('click', resetRound);
    document.getElementById('reset-session-btn').addEventListener('click', resetSession);
}

function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').catch(err => {
            console.warn('SW registration failed:', err);
        });
    });
}

loadState();
bindEvents();
render();
registerSW();
