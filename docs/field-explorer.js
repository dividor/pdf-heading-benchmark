(() => {
  const root = document.getElementById('field-explorer');
  const points = [...root.querySelectorAll('.field-point')];
  const filter = root.querySelector('#field-filter');
  const select = root.querySelector('#field-system');
  const tooltip = root.querySelector('.field-tooltip');
  function inspect(point) {
    points.forEach(item => item.classList.toggle('selected', item === point));
    select.value = point.dataset.index;
    const label = tooltip.querySelector('text');
    const box = tooltip.querySelector('rect');
    const hit = point.querySelector('.field-hit');
    label.textContent = point.dataset.name + ' · ' + point.dataset.text + ' text / ' + point.dataset.layout + ' layout';
    tooltip.removeAttribute('hidden');
    const width = label.getComputedTextLength() + 20;
    const x = Math.max(10, Math.min(990 - width, Number(hit.getAttribute('cx')) - width / 2));
    const y = Number(hit.getAttribute('cy')) - 43;
    tooltip.setAttribute('transform', 'translate(' + x + ' ' + y + ')');
    box.setAttribute('width', String(width));
    box.setAttribute('height', '32');
    label.setAttribute('x', '10');
    label.setAttribute('y', '23');
  }
  function openModel(index) {
    root.querySelector('#field-model-' + index).showModal();
  }
  function applyFilter() {
    const visible = points.filter(point => filter.value === 'all' || point.dataset.category === filter.value);
    points.forEach(point => { point.toggleAttribute('hidden', !visible.includes(point)); });
    root.querySelectorAll('.field-label').forEach(label => {
      label.toggleAttribute('hidden', !visible.some(point => point.dataset.index === label.dataset.for));
    });
    [...select.options].forEach(option => {
      const shown = filter.value === 'all' || option.dataset.category === filter.value;
      option.hidden = !shown;
      option.disabled = !shown;
    });
    root.querySelector('#field-count').textContent = visible.length + ' systems · Layout scores above 70 · Higher is better';
    if (!visible.some(point => point.dataset.index === select.value)) select.value = visible[0].dataset.index;
    tooltip.setAttribute('hidden', 'hidden');
  }
  points.forEach(point => {
    ['pointerenter', 'focus'].forEach(event => point.addEventListener(event, () => inspect(point)));
    point.addEventListener('pointerleave', () => tooltip.setAttribute('hidden', 'hidden'));
    point.addEventListener('blur', () => tooltip.setAttribute('hidden', 'hidden'));
    point.addEventListener('click', () => { inspect(point); openModel(point.dataset.index); });
    point.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openModel(point.dataset.index); }
    });
  });
  root.querySelectorAll('.field-model-dialog').forEach(dialog => {
    dialog.querySelector('.field-dialog-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  });
  root.querySelectorAll('[data-open-model]').forEach(button => {
    button.addEventListener('click', () => openModel(button.dataset.openModel));
  });
  select.addEventListener('change', () => inspect(points.find(point => point.dataset.index === select.value)));
  root.querySelector('#field-open-model').addEventListener('click', () => openModel(select.value));
  filter.addEventListener('change', applyFilter);
  select.value = points.find(point => point.dataset.name === 'LlamaParse').dataset.index;
  applyFilter();
})();
