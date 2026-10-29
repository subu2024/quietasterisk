/* Quiet theme behaviour. No inline handlers: everything is wired by data-* attributes.
   data-view-tab="year|category"   Essays page view switch
   data-load-more="<grid id>"      reveal more cards (data-step = how many)
   #newsletter-form[data-endpoint] newsletter signup (JSON POST to a proxy) */
(function () {
  'use strict';

  /* ---- Essays page: by year / by category ---- */
  function showView(view) {
    document.querySelectorAll('[data-view]').forEach(function (el) {
      el.hidden = el.getAttribute('data-view') !== view;
    });
    document.querySelectorAll('[data-view-tab]').forEach(function (tab) {
      var active = tab.getAttribute('data-view-tab') === view;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-pressed', active ? 'true' : 'false');
    });
  }
  document.querySelectorAll('[data-view-tab]').forEach(function (tab) {
    tab.addEventListener('click', function () { showView(tab.getAttribute('data-view-tab')); });
  });
  if (window.location.hash.indexOf('category') !== -1 && document.querySelector('[data-view="category"]')) {
    showView('category');
    var target = document.getElementById(window.location.hash.substring(1));
    if (target) { setTimeout(function () { target.scrollIntoView(); }, 0); }
  }

  /* ---- Load more ---- */
  document.querySelectorAll('[data-load-more]').forEach(function (button) {
    button.addEventListener('click', function () {
      var grid = document.getElementById(button.getAttribute('data-load-more'));
      var step = parseInt(button.getAttribute('data-step'), 10) || 6;
      if (!grid) { return; }
      var hidden = grid.querySelectorAll('.hidden-post');
      for (var i = 0; i < hidden.length && i < step; i++) { hidden[i].classList.remove('hidden-post'); }
      var remaining = grid.querySelectorAll('.hidden-post').length;
      if (remaining === 0) { button.hidden = true; }
      else { button.textContent = 'Load more (' + remaining + ' remaining)'; }
    });
  });

  /* ---- Newsletter ---- */
  var form = document.getElementById('newsletter-form');
  if (form) {
    var input = document.getElementById('newsletter-email');
    var button = document.getElementById('newsletter-submit');
    var status = document.getElementById('newsletter-status');
    var defaultStatus = status.textContent;
    var label = button.getAttribute('data-label') || button.textContent;

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var email = input.value.trim();
      if (!email) { return; }
      button.disabled = true;
      button.textContent = 'Subscribing…';
      status.textContent = defaultStatus;

      fetch(form.getAttribute('data-endpoint'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
      })
        .then(function (response) {
          if (!response.ok) { throw new Error('Request failed'); }
          return response.json().catch(function () { return {}; });
        })
        .then(function () {
          form.reset();
          status.textContent = form.getAttribute('data-success');
          button.textContent = 'Subscribed';
        })
        .catch(function () {
          status.textContent = form.getAttribute('data-error');
          button.disabled = false;
          button.textContent = label;
        });
    });
  }
})();
