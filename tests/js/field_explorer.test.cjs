const test = require('node:test');
const assert = require('node:assert/strict');

class Element {
  constructor(dataset = {}) {
    this.dataset = dataset;
    this.attributes = new Map();
    this.events = new Map();
    this.children = new Map();
    this.classes = new Set();
    this.classList = { toggle: (name, enabled) => enabled ? this.classes.add(name) : this.classes.delete(name) };
    this.textContent = '';
  }
  addEventListener(name, handler) { this.events.set(name, handler); }
  fire(name, event = {}) { this.events.get(name)({ target: this, ...event }); }
  querySelector(selector) { return this.children.get(selector); }
  setAttribute(name, value) { this.attributes.set(name, value); }
  getAttribute(name) { return this.attributes.get(name); }
  removeAttribute(name) { this.attributes.delete(name); }
  toggleAttribute(name, present) { present ? this.attributes.set(name, '') : this.attributes.delete(name); }
  getComputedTextLength() { return this.textContent.length * 8; }
  showModal() { this.open = true; }
  close() { this.open = false; }
}

function fixture() {
  const root = new Element();
  const filter = new Element(); filter.value = 'all';
  const select = new Element();
  const tooltip = new Element();
  tooltip.children.set('text', new Element());
  tooltip.children.set('rect', new Element());
  const rows = [['LlamaParse', 'hosted'], ['Docling', 'study'], ['Other model', 'local']];
  const points = rows.map(([name, category], i) => {
    const point = new Element({ name, category, index: String(i), text: '80', layout: '90' });
    const hit = new Element(); hit.setAttribute('cx', '400'); hit.setAttribute('cy', '300');
    point.children.set('.field-hit', hit);
    return point;
  });
  select.options = points.map(point => new Element(point.dataset));
  const labels = points.map(point => new Element({ for: point.dataset.index }));
  const buttons = points.map(point => new Element({ openModel: point.dataset.index }));
  const dialogs = points.map(point => {
    const dialog = new Element();
    dialog.children.set('.field-dialog-close', new Element());
    root.children.set('#field-model-' + point.dataset.index, dialog);
    return dialog;
  });
  Object.entries({ '#field-filter': filter, '#field-system': select, '.field-tooltip': tooltip,
    '#field-count': new Element(), '#field-open-model': new Element() })
    .forEach(([key, value]) => root.children.set(key, value));
  const groups = { '.field-point': points, '.field-label': labels,
    '.field-model-dialog': dialogs, '[data-open-model]': buttons };
  root.querySelectorAll = selector => groups[selector];
  global.document = { getElementById: id => { assert.equal(id, 'field-explorer'); return root; } };
  delete require.cache[require.resolve('../../docs/field-explorer.js')];
  require('../../docs/field-explorer.js');
  return { root, points, filter, select, labels, dialogs, buttons, tooltip };
}

test('filters markers, labels and selector options together', () => {
  const f = fixture();
  assert.equal(f.select.value, '0');
  assert.match(f.root.querySelector('#field-count').textContent, /^3 systems/);
  f.filter.value = 'study'; f.filter.fire('change');
  assert.equal(f.select.value, '1');
  assert.equal(f.points[0].attributes.has('hidden'), true);
  assert.equal(f.labels[0].attributes.has('hidden'), true);
  assert.equal(f.select.options[0].disabled, true);
  assert.equal(f.points[1].attributes.has('hidden'), false);
  assert.match(f.root.querySelector('#field-count').textContent, /^1 systems/);
  f.filter.value = 'all'; f.filter.fire('change');
  assert.ok(f.select.options.every(option => !option.disabled));
  assert.ok(f.labels.every(label => !label.attributes.has('hidden')));
});

test('each point opens its own modal by click and keyboard', () => {
  const f = fixture();
  f.points.forEach((point, i) => {
    point.fire('click'); assert.equal(f.dialogs[i].open, true);
    f.dialogs[i].querySelector('.field-dialog-close').fire('click');
    assert.equal(f.dialogs[i].open, false);
    for (const key of ['Enter', ' ']) {
      let prevented = false;
      point.fire('keydown', { key, preventDefault: () => { prevented = true; } });
      assert.equal(prevented, true); assert.equal(f.dialogs[i].open, true);
      f.dialogs[i].fire('click'); assert.equal(f.dialogs[i].open, false);
    }
    point.fire('keydown', { key: 'ArrowRight' }); assert.equal(f.dialogs[i].open, false);
  });
});

test('hover, focus and selection show the matching score label', () => {
  const f = fixture();
  f.points[1].fire('pointerenter');
  assert.match(f.tooltip.querySelector('text').textContent, /^Docling · 80 text \/ 90 layout$/);
  assert.equal(f.tooltip.attributes.has('hidden'), false);
  assert.equal(f.points[1].classes.has('selected'), true);
  f.points[1].fire('pointerleave'); assert.equal(f.tooltip.attributes.has('hidden'), true);
  f.points[2].fire('focus'); assert.equal(f.select.value, '2');
  f.points[2].fire('blur'); assert.equal(f.tooltip.attributes.has('hidden'), true);
  f.select.value = '0'; f.select.fire('change');
  assert.match(f.tooltip.querySelector('text').textContent, /^LlamaParse/);
  f.root.querySelector('#field-open-model').fire('click'); assert.equal(f.dialogs[0].open, true);
  f.dialogs[0].fire('click', { target: new Element() }); assert.equal(f.dialogs[0].open, true);
  f.buttons[2].fire('click'); assert.equal(f.dialogs[2].open, true);
});
