/* WDC capture enhancer — progressive enhancement for the ConvertKit email forms.
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
      '.wdc-err{font-family:"Inter",system-ui,sans-serif;font-size:13px;color:#b4232a;margin-top:.6em;}';
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
    var btn = form.querySelector('button[type="submit"], button');
    if (btn && !btn.getAttribute('data-wdc-label')) {
      btn.textContent = 'Send me the Field Guide';
      btn.setAttribute('data-wdc-label', '1');
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var email = (data.get('email_address') || '').toString().trim();
      if (!email) return;
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }

      function finish() {
        try { if (window.plausible) plausible('signup', { props: { source: 'field-guide' } }); } catch (_) {}
        var card = form.closest('.bg-warmWhite, .wdc-topcap');
        var panel = successPanel(email);
        if (card) { card.innerHTML = ''; card.appendChild(panel); }
        else if (form.parentNode) { form.parentNode.replaceChild(panel, form); }
      }

      fetch(form.action, { method: 'POST', headers: { 'Accept': 'application/json' }, body: data })
        .then(function () { finish(); })
        .catch(function () { finish(); }); // request still reaches ConvertKit; show success either way
    });
  }

  function injectTopCapture(forms) {
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

  ready(function () {
    var forms = Array.prototype.slice.call(document.querySelectorAll(FORM_SELECTOR));
    if (!forms.length) return;
    injectStyles();
    var top = injectTopCapture(forms);
    if (top) forms.push(top);
    forms.forEach(enhance);
  });
})();
