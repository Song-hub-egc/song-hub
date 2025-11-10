console.log("Hi, I am a script loaded from auth module");

function revokeSession(sessionId) {
    if (!confirm('Are you sure you want to revoke this session? The device will be logged out immediately.')) {
        return;
    }

    fetch(`/sessions/${sessionId}/revoke`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const row = document.getElementById(`session-${sessionId}`);
            if (row) {
                row.remove();
            }

            const tbody = document.querySelector('tbody');
            if (tbody && tbody.children.length === 0) {
                location.reload();
            }
        } else {
            alert('Error revoking session: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('Error revoking session: ' + error);
    });
}

function revokeAllSessions() {
    if (!confirm('Are you sure you want to revoke all other sessions? All other devices will be logged out immediately.')) {
        return;
    }

    fetch('/sessions/revoke-all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error revoking sessions: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('Error revoking sessions: ' + error);
    });
}
