// Progressive enhancement: all content remains readable without JavaScript.
(() => {
  const tabs = [...document.querySelectorAll('.report-tabs [role="tab"]')];
  const panels = [...document.querySelectorAll('.report-panel')];
  function activate(panel, moveFocus = false) {
    panels.forEach(item => { item.hidden = item !== panel; item.setAttribute('role', 'tabpanel'); });
    tabs.forEach(tab => {
      const selected = tab.getAttribute('aria-controls') === panel.id;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected && moveFocus) tab.focus();
    });
  }
  function followHash() {
    const target = document.getElementById(location.hash.slice(1));
    const panel = target?.closest('.report-panel');
    if (!panel) { activate(panels[0]); return; }
    activate(panel);
    let ancestor = target;
    while (ancestor && ancestor !== panel) {
      if (ancestor.tagName === 'DETAILS') ancestor.open = true;
      ancestor = ancestor.parentElement;
    }
    if (target !== panel) target.scrollIntoView({block: 'start'});
  }
  function select(tab) {
    const id = tab.getAttribute('aria-controls');
    activate(document.getElementById(id), true);
    history.pushState(null, '', '#' + id);
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const destination = {ArrowRight: (index + 1) % tabs.length,
        ArrowLeft: (index + tabs.length - 1) % tabs.length, Home: 0, End: tabs.length - 1}[event.key];
      if (destination === undefined) return;
      event.preventDefault();
      select(tabs[destination]);
    });
  });
  document.documentElement.classList.add('report-enhanced');
  document.querySelector('.report-tabs').hidden = false;
  document.querySelector('#show-diagnostics').addEventListener('change', event => {
    document.querySelector('.league-table').classList.toggle('show-diagnostics', event.target.checked);
  });
  window.addEventListener('hashchange', followHash);
  window.addEventListener('popstate', followHash);
  followHash();
})();
