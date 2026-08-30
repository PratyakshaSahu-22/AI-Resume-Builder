/**
 * AI Resume Builder – Main JavaScript
 */

// ── Auto-dismiss alerts after 5 seconds ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });
});

// ── Character counter for textareas ─────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('textarea[maxlength]').forEach(function (ta) {
    const max = parseInt(ta.getAttribute('maxlength'), 10);
    const counter = document.createElement('div');
    counter.className = 'form-text text-end char-counter';
    counter.textContent = '0 / ' + max;
    ta.insertAdjacentElement('afterend', counter);
    ta.addEventListener('input', function () {
      const len = ta.value.length;
      counter.textContent = len + ' / ' + max;
      counter.style.color = len > max * 0.9 ? '#dc2626' : '#6b7280';
    });
    // Fire on load for pre-filled values
    ta.dispatchEvent(new Event('input'));
  });
});

// ── Confirm form submissions with data-confirm attribute ─────────────────────
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });
});

// ── Skill tag input helper (profile/skills) ───────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {
  const skillsInput = document.querySelector('input[name="skills_text"]');
  if (skillsInput) {
    skillsInput.addEventListener('keydown', function (e) {
      // Allow Enter to add a comma automatically
      if (e.key === 'Enter') {
        e.preventDefault();
        const val = this.value.trim();
        if (val && !val.endsWith(',')) {
          this.value = val + ', ';
        }
      }
    });
  }
});
