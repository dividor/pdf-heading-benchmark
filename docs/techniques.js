// Preserve ordinary source links when JavaScript or native dialogs are unavailable.
(() => {
  let opener = null;
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[data-technique]');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const panel = document.getElementById(link.dataset.technique);
    if (!panel || typeof panel.showModal !== 'function') return;
    event.preventDefault();
    opener = link;
    panel.showModal();
    panel.querySelector('h2').focus();
  });
  document.querySelectorAll('.technique-dialog').forEach((panel) => {
    panel.querySelector('.technique-close').addEventListener('click', () => panel.close());
    panel.addEventListener('click', (event) => {
      if (event.target === panel) panel.close();
    });
    panel.addEventListener('close', () => {
      if (opener) opener.focus();
      opener = null;
    });
  });
})();
