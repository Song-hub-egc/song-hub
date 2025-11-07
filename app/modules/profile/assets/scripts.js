console.log("Hi, I am a script loaded from profile module");

let backupCodes = [];

function goToStep(step) {
    document.querySelectorAll('.step-content').forEach(el => el.style.display = 'none');
    document.querySelectorAll('[id$="-indicator"]').forEach(el => el.classList.remove('active'));

    document.getElementById('step' + step).style.display = 'block';
    document.getElementById('step' + step + '-indicator').classList.add('active');

    if (step === 2) {
        const tokenInput = document.getElementById('token');
        if (tokenInput) tokenInput.focus();
    }
}

async function verifyCode(event) {
    event.preventDefault();

    const token = document.getElementById('token').value;
    const errorDiv = document.getElementById('error-message');
    const submitBtn = document.getElementById('verify-btn');
    const btnText = document.getElementById('verify-btn-text');
    const btnSpinner = document.getElementById('verify-btn-spinner');

    if (!token || token.length !== 6) {
        errorDiv.textContent = 'Please enter a valid 6-digit code';
        errorDiv.style.display = 'block';
        return false;
    }

    errorDiv.style.display = 'none';
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnSpinner.style.display = 'inline-block';

    try {
        const verifyUrl = submitBtn.getAttribute('data-verify-url');
        const response = await fetch(verifyUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: token })
        });

        const data = await response.json();

        if (data.success) {
            backupCodes = data.backup_codes;
            displayBackupCodes();
            goToStep(3);
        } else {
            errorDiv.textContent = data.error || 'Invalid verification code';
            errorDiv.style.display = 'block';
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
        }
    } catch (error) {
        errorDiv.textContent = 'An error occurred. Please try again.';
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnSpinner.style.display = 'none';
    }

    return false;
}

function displayBackupCodes() {
    const list = document.getElementById('backup-codes-list');
    if (!list) return;

    list.innerHTML = '';

    backupCodes.forEach(code => {
        const col = document.createElement('div');
        col.className = 'col-md-6 mb-2';
        const codeEl = document.createElement('code');
        codeEl.className = 'fs-5';
        codeEl.textContent = code;
        col.appendChild(codeEl);
        list.appendChild(col);
    });
}

function downloadCodes() {
    if (!backupCodes || backupCodes.length === 0) return;

    const text = 'UVLHUB Two-Factor Backup Codes\n\n' +
                 backupCodes.join('\n') +
                 '\n\nKeep these codes in a safe place. Each code can only be used once.';
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'uvlhub_backup_codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
