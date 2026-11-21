"use strict";
const dataset = JSON.parse(document.querySelector('#review-data').textContent);
const el = id => document.getElementById(id);
const ns = 'http://www.w3.org/2000/svg';
const colours = ['#81919f', '#006ea5', '#00806a', '#8b4bb1', '#bc6405', '#c02d65', '#604f34'];
const storageKey = `wfp-heading-review-${dataset.label_hash}`;
let reviews = {};
try { reviews = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch { /* Export works without storage. */ }
let current = dataset.documents.find(d => d.id === 611) || dataset.documents[0];
let pageNumber = current.review_pages.find(p => p > 10) || current.review_pages[0];
function node(tag, attributes = {}, text = '') {
  const value = document.createElement(tag);
  Object.entries(attributes).forEach(([k, v]) => value.setAttribute(k, v));
  value.textContent = text;
  return value;
}
function svgNode(tag, attributes) {
  const value = document.createElementNS(ns, tag);
  Object.entries(attributes).forEach(([k, v]) => value.setAttribute(k, v));
  return value;
}
function saveReview() {
  try { localStorage.setItem(storageKey, JSON.stringify(reviews)); } catch { /* Keep in memory for export. */ }
  el('review-count').textContent = `${Object.keys(reviews).length} saved review items`;
}
function editItem(item, reference) {
  const key = `${current.id}:${item.line_ids.join('+')}`;
  const existing = reviews[key] || {};
  const editor = el('editor'); editor.hidden = false; editor.replaceChildren();
  editor.append(node('strong', {}, `PDF ${item.page} · ${reference ? 'Assistant H' + item.level : 'Other text'}`),
    node('p', {}, item.text));
  const decision = node('select', {'aria-label': 'Review decision'});
  ['Confirm', 'Change', 'Uncertain'].forEach(value => decision.append(node('option', {value}, value)));
  decision.value = existing.decision || 'Uncertain';
  const level = node('select', {'aria-label': 'Proposed heading level'});
  for (let i = 0; i <= 6; i++) level.append(node('option', {value: i}, i ? `H${i}` : 'Not a heading'));
  level.value = existing.proposed_level ?? item.level ?? 0;
  const note = node('textarea', {placeholder: 'Reason, missing heading, or wrapped-line grouping…', 'aria-label': 'Review note'});
  note.value = existing.note || '';
  const save = node('button', {class: 'primary'}, 'Save assessment');
  save.onclick = () => {
    reviews[key] = {report_id: current.id, page: item.page, line_ids: item.line_ids,
      text: item.text, original_level: reference ? item.level : (current.review_pages.includes(item.page) ? 0 : null),
      decision: decision.value, proposed_level: Number(level.value), note: note.value};
    saveReview(); renderPage();
  };
  const remove = node('button', {}, 'Remove assessment');
  remove.onclick = () => { delete reviews[key]; saveReview(); renderPage(); editor.hidden = true; };
  editor.append(decision, level, note, save, remove);
  editor.scrollIntoView({behavior: 'smooth', block: 'nearest'});
}
function addMark(svg, item, box, mode, part) {
  const reference = mode === 'reference';
  const group = svgNode('g', {class: `mark ${mode} ${mode === 'other' ? 'negative' : ''}`});
  const colour = reference ? colours[item.level] : (mode === 'model' ? '#d52186' : '#899aaa');
  const key = `${current.id}:${item.line_ids.join('+')}`;
  const rect = svgNode('rect', {x: box[0], y: box[1], width: Math.max(2, box[2] - box[0]),
    height: Math.max(3, box[3] - box[1]), fill: colour, 'fill-opacity': reference ? .10 : 0,
    stroke: colour, 'stroke-width': mode === 'other' ? .4 : 1.2,
    'stroke-dasharray': mode === 'model' ? '4 2' : 'none', class: reviews[key] ? 'reviewed-line' : ''});
  const title = svgNode('title', {});
  title.textContent = `${mode} ${item.level ? 'H' + item.level : '0'}: ${item.text}`;
  group.append(rect, title);
  if (part === 0 && mode !== 'other') {
    const x = Math.max(1, box[0] - 30);
    const y = Math.max(10, box[1] + 9);
    const text = svgNode('text', {x, y: mode === 'model' ? y + 9 : y, fill: colour,
      stroke: 'white', 'stroke-width': 2, 'paint-order': 'stroke'});
    text.textContent = `${mode === 'model' ? 'M' : 'H'}${item.level}`; group.append(text);
  }
  if (mode !== 'model') group.onclick = () => editItem(item, reference);
  svg.append(group);
}
function renderPage() {
  const page = current.pages.find(p => p.number === pageNumber);
  el('page-select').value = pageNumber;
  const area = el('page'); area.replaceChildren();
  area.classList.toggle('show-other', el('other-toggle').checked);
  area.append(node('img', {src: page.image, alt: `${current.title}, PDF page ${pageNumber}`}));
  const svg = svgNode('svg', {viewBox: `0 0 ${page.width} ${page.height}`, 'aria-label': 'Heading annotation overlay'});
  const annotations = current.annotations.filter(a => a.page === pageNumber);
  const assigned = new Set(annotations.flatMap(a => a.line_ids));
  page.lines.filter(line => !assigned.has(line.id)).forEach(line =>
    addMark(svg, {...line, level: 0, line_ids: [line.id]}, line.bbox, 'other', 0));
  if (el('annotations-toggle').checked) annotations.forEach(a => a.bboxes.forEach((b, i) => addMark(svg, a, b, 'reference', i)));
  if (el('predictions-toggle').checked) current.predictions.filter(p => p.page === pageNumber)
    .forEach(p => p.bboxes.forEach((b, i) => addMark(svg, p, b, 'model', i)));
  area.append(svg); el('source-image').href = page.image;
  el('page-note').textContent = current.review_pages.includes(pageNumber)
    ? `Reviewed page · ${annotations.length} heading groups · H1 blue / H2 green / H3 purple / H4 amber / H5 pink. M labels are model predictions.`
    : 'TOC context only — this page was not in the labelled training/evaluation sample.';
}
function renderDocument() {
  el('doc-title').textContent = `${current.id} · ${current.title}`;
  el('doc-meta').replaceChildren(node('span', {class: 'badge'}, current.split),
    document.createTextNode(` · ${current.language} · ${current.year} · ${current.total_pages} pages · `),
    node('a', {href: current.url, target: '_blank', rel: 'noopener'}, 'Source PDF'));
  const outline = el('outline'); outline.replaceChildren();
  current.annotations.forEach(annotation => {
    const li = node('li', {style: `margin-left:${(annotation.level - 1) * 12}px`});
    const button = node('button', {}, `H${annotation.level} · p${annotation.page} · ${annotation.text}`);
    button.onclick = () => {pageNumber = annotation.page; renderPage(); editItem(annotation, true); el('page').scrollIntoView({block: 'start', behavior: 'smooth'});};
    li.append(button); outline.append(li);
  });
  const toc = el('toc'); toc.replaceChildren();
  current.toc_pages.forEach(number => {
    const page = current.pages.find(p => p.number === number);
    const a = node('a', {href: page.image, target: '_blank', rel: 'noopener'});
    a.append(node('img', {src: page.image, alt: `Contents PDF page ${number}`, loading: 'lazy'}),
      node('span', {}, `PDF page ${number} · open image`)); toc.append(a);
  });
  el('toc-note').textContent = current.toc_note;
  const options = el('page-select'); options.replaceChildren();
  current.pages.forEach(p => options.append(node('option', {value: p.number},
    `${p.number}${current.toc_pages.includes(p.number) ? ' · contents' : ''}${current.review_pages.includes(p.number) ? ' · reviewed' : ' · context'}`)));
  el('editor').hidden = true; renderPage();
}
function populateReports() {
  const split = el('split-select').value;
  const docs = dataset.documents.filter(d => split === 'all' || d.split === split);
  const select = el('report-select'); select.replaceChildren();
  docs.forEach(d => select.append(node('option', {value: d.id}, `${d.id} · ${d.split} · ${d.title}`)));
  if (!docs.includes(current)) {current = docs[0]; pageNumber = current.review_pages[0];}
  select.value = current.id; renderDocument();
}
el('report-select').onchange = event => {
  current = dataset.documents.find(d => d.id === Number(event.target.value));
  pageNumber = current.review_pages[0]; renderDocument();
};
el('split-select').onchange = populateReports;
el('page-select').onchange = event => {pageNumber = Number(event.target.value); renderPage();};
['annotations-toggle', 'predictions-toggle', 'other-toggle'].forEach(id => el(id).onchange = renderPage);
function stepPage(delta) {
  const index = current.pages.findIndex(p => p.number === pageNumber);
  pageNumber = current.pages[Math.max(0, Math.min(current.pages.length - 1, index + delta))].number;
  renderPage();
}
el('previous').onclick = () => stepPage(-1); el('next').onclick = () => stepPage(1);
el('export').onclick = () => {
  const payload = JSON.stringify({schema: 1, label_sha256: dataset.label_hash, reviews: Object.values(reviews)}, null, 2);
  el('export-json').value = payload; el('export-preview').hidden = false; el('export-preview').open = true;
  const blob = new Blob([payload], {type: 'application/json'});
  const url = URL.createObjectURL(blob), a = node('a', {href: url, download: 'wfp-heading-review.json'});
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
el('import').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    const input = JSON.parse(await file.text());
    if (input.label_sha256 !== dataset.label_hash || !Array.isArray(input.reviews)) throw new Error('Different annotation version');
    input.reviews.forEach(r => {reviews[`${r.report_id}:${r.line_ids.join('+')}`] = r;});
    saveReview(); renderPage();
  } catch (error) { alert(`Review import failed: ${error.message}`); }
};
populateReports(); saveReview();
