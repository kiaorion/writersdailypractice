/* WDC capture enhancer: progressive enhancement for the ConvertKit email forms.
   Goals (from the conversion data, June 2026):
   1. Keep the reader on the page (AJAX submit, no bounce to ConvertKit's hosted page).
   2. Deliver the lead magnet instantly: the Writer's Field Guide.
   3. Add a high-intent capture near the top of the page (after the profile card).
   Without JS the forms still submit normally, so nothing breaks. */
(function () {
  var GUIDE = '/writers-field-guide/';
  var FORM_SELECTOR = 'form[action*="convertkit.com/forms"], form[action*="kit.com/forms"]';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  function injectStyles() {
    if (document.getElementById('wdc-cap-style')) return;
    var s = document.createElement('style');
    s.id = 'wdc-cap-style';
    s.textContent =
      '.wdc-topcap{background:#fbf9f4;border:1px solid #eee4c8;border-left:4px solid #E8B931;border-radius:12px;padding:1.6em;margin:2.2em 0;}' +
      '.wdc-topcap-h{font-family:"Playfair Display",Georgia,serif;font-size:21px;font-weight:700;color:#111;margin:0 0 .35em;line-height:1.2;}' +
      '.wdc-topcap-s{font-family:"Inter",system-ui,sans-serif;font-size:14px;line-height:1.5;color:#555;margin:0 0 1.1em;}' +
      '.wdc-success{background:#fff;border-radius:14px;padding:1.6em;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.12);max-width:460px;margin:0 auto;}' +
      '.wdc-success-h{font-family:"Playfair Display",Georgia,serif;font-size:22px;font-weight:700;color:#111;margin:0 0 .35em;}' +
      '.wdc-success-s{font-family:"Inter",system-ui,sans-serif;font-size:15px;line-height:1.55;color:#555;margin:0 0 1.2em;}' +
      '.wdc-success-btn{display:inline-block;background:linear-gradient(to right,#E8B931,#F5D060);color:#1a1a1a;font-weight:700;padding:.75em 1.5em;border-radius:9999px;text-decoration:none;font-family:"Inter",system-ui,sans-serif;font-size:14px;}' +
      '.wdc-unlocked-note{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:1em 1.2em;font-family:"Inter",system-ui,sans-serif;font-size:14px;line-height:1.5;color:#166534;text-align:center;}' +
      '.wdc-err{font-family:"Inter",system-ui,sans-serif;font-size:13px;color:#b4232a;margin-top:.6em;text-align:center;}';
    document.head.appendChild(s);
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function successPanel(email) {
    var panel = document.createElement('div');
    panel.className = 'wdc-success';
    panel.innerHTML =
      '<p class="wdc-success-h">You’re in.</p>' +
      '<p class="wdc-success-s">Your Writer’s Field Guide is ready. Open it below, and watch your inbox to confirm.</p>' +
      '<a class="wdc-success-btn" href="' + GUIDE + '">Open the Field Guide →</a>';
    return panel;
  }

  function enhance(form) {
    if (form.getAttribute('data-wdc') === '1') return;
    form.setAttribute('data-wdc', '1');
    form.removeAttribute('onsubmit'); // we fire the signup event ourselves, on success
    // Gated forms (data-wdc-unlock) unlock a payoff instead of showing the Field Guide panel,
    // and keep their own button label + their own signup source.
    var unlockKey = form.getAttribute('data-wdc-unlock');
    var unlockTarget = form.getAttribute('data-wdc-unlock-target');
    var srcEl = form.querySelector('[name="fields[source_page]"]');
    var source = (srcEl && srcEl.value) || 'field-guide';
    var btn = form.querySelector('button[type="submit"], button');
    if (btn && !unlockKey && !btn.getAttribute('data-wdc-label')) {
      btn.textContent = 'Send me the Field Guide';
      btn.setAttribute('data-wdc-label', '1');
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var email = (data.get('email_address') || '').toString().trim();
      if (!email) return;
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

      function showError(msg) {
        if (btn) { btn.disabled = false; btn.textContent = unlockKey ? 'Try again' : 'Send me the Field Guide'; }
        var existing = form.querySelector('.wdc-err');
        if (existing) existing.remove();
        var err = document.createElement('p');
        err.className = 'wdc-err';
        err.textContent = msg || 'Something went wrong. Please try again.';
        form.appendChild(err);
      }

      function finish() {
        try { if (window.plausible) plausible('signup', { props: { source: source } }); } catch (_) {}
        if (unlockKey) {
          try { localStorage.setItem('wdc_unlock_' + unlockKey, '1'); } catch (_) {}
          if (unlockTarget) {
            var t = document.querySelector(unlockTarget);
            if (t) { t.style.display = ''; t.classList.remove('wdc-locked'); }
          }
          var note = document.createElement('div');
          note.className = 'wdc-unlocked-note';
          note.innerHTML = '<strong>You’re in.</strong> Unlocked. Your free Writer’s Field Guide is on its way to your inbox.';
          if (form.parentNode) form.parentNode.replaceChild(note, form);
          try { window.dispatchEvent(new CustomEvent('wdc:unlocked', { detail: { key: unlockKey } })); } catch (_) {}
          return;
        }
        var card = form.closest('.bg-warmWhite, .wdc-topcap');
        var panel = successPanel(email);
        if (card) { card.innerHTML = ''; card.appendChild(panel); }
        else if (form.parentNode) { form.parentNode.replaceChild(panel, form); }
      }

      fetch(form.action, { method: 'POST', headers: { 'Accept': 'application/json' }, body: data })
        .then(function (response) {
          if (response.ok) { finish(); return; }
          // ConvertKit returns real error bodies (e.g. invalid email, rate limit); surface them
          // instead of silently declaring success, which is what this used to do unconditionally.
          response.json().then(function (j) {
            showError(j && j.message ? j.message : 'Signup failed (' + response.status + '). Please try again.');
          }).catch(function () {
            showError('Signup failed (' + response.status + '). Please try again.');
          });
        })
        .catch(function () {
          showError('Network error. Check your connection and try again.');
        });
    });
  }

  // Exposed so tools/quiz can check unlock state (survives reloads via localStorage).
  window.wdcUnlocked = function (key) {
    try { return localStorage.getItem('wdc_unlock_' + key) === '1'; } catch (_) { return false; }
  };

  function injectTopCapture(forms) {
    if (document.querySelector('.wdc-topcap')) return null;
    var profile = document.querySelector('.profile-card');
    if (!profile || !forms.length) return null;
    var clone = forms[0].cloneNode(true);
    clone.removeAttribute('data-wdc');
    var qb = clone.querySelector('button[data-wdc-label]');
    if (qb) qb.removeAttribute('data-wdc-label');
    var box = document.createElement('div');
    box.className = 'wdc-topcap';
    box.innerHTML =
      '<p class="wdc-topcap-h">Get the free Writer’s Field Guide</p>' +
      '<p class="wdc-topcap-s">The daily writing routines of 90+ famous authors, distilled into one guide. Enter your email and it’s yours.</p>';
    box.appendChild(clone);
    profile.parentNode.insertBefore(box, profile.nextSibling);
    return clone;
  }

  function scan() {
    var forms = Array.prototype.slice.call(document.querySelectorAll(FORM_SELECTOR));
    if (!forms.length) return;
    injectStyles();
    var top = injectTopCapture(forms);
    if (top) forms.push(top);
    forms.forEach(enhance);
  }
  // Exposed so dynamically-rendered forms (e.g. the genre-quiz result) can be enhanced on demand.
  window.wdcEnhanceForms = scan;
  ready(scan);
})();
