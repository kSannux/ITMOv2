"use strict";
const rows = JSON.parse(document.querySelector('#initial-data').textContent);
const labels = {id: 'ID', name: 'Имя', department: 'Отдел', active: 'Активен'};
const $ = id => document.getElementById(id);
let page = 1, sortKey = 'id', direction = 1, busy = false, currentRows = [];
let tooltipTimer, toastTimer;
const visible = new Set(Object.keys(labels));
const display = value => typeof value === 'boolean' ? (value ? 'Да' : 'Нет') : String(value);

function hideTooltip() { $('export-tooltip').hidden = true; clearTimeout(tooltipTimer); }
function showTooltip() {
  $('export-tooltip').textContent = currentRows.length ? 'Экспортирует текущие видимые строки в JSON' : 'Нет данных для экспорта';
  $('export-tooltip').hidden = false;
  clearTimeout(tooltipTimer);
  tooltipTimer = setTimeout(hideTooltip, 4000);
}
function render() {
  const query = $('search').value.trim().toLocaleLowerCase('ru');
  const filtered = rows.filter(row => Object.values(row).some(value => display(value).toLocaleLowerCase('ru').includes(query)));
  filtered.sort((a, b) => direction * (typeof a[sortKey] === 'string' ? a[sortKey].localeCompare(b[sortKey], 'ru') : Number(a[sortKey]) - Number(b[sortKey])));
  const size = Number($('page-size').value), pages = Math.max(1, Math.ceil(filtered.length / size));
  page = Math.min(page, pages);
  currentRows = filtered.slice((page - 1) * size, page * size);
  $('head').replaceChildren(); $('body').replaceChildren();
  const header = document.createElement('tr');
  for (const key of visible) {
    const th = document.createElement('th'), button = document.createElement('button');
    th.scope = 'col';
    th.setAttribute('aria-sort', key === sortKey ? (direction === 1 ? 'ascending' : 'descending') : 'none');
    button.textContent = labels[key] + (key === sortKey ? (direction === 1 ? ' ↑' : ' ↓') : '');
    button.onclick = () => { direction = key === sortKey ? -direction : 1; sortKey = key; render(); };
    th.append(button); header.append(th);
  }
  $('head').append(header);
  for (const row of currentRows) {
    const tr = document.createElement('tr');
    for (const key of visible) { const td = document.createElement('td'); td.textContent = display(row[key]); tr.append(td); }
    $('body').append(tr);
  }
  $('empty').hidden = currentRows.length !== 0;
  $('export').disabled = busy || currentRows.length === 0;
  $('export').setAttribute('aria-busy', String(busy));
  $('export').textContent = busy ? '⏳ Экспорт…' : 'Экспорт в JSON';
  $('prev').disabled = page === 1; $('next').disabled = page === pages;
  $('page').textContent = `Страница ${page} из ${pages}`;
  $('summary').textContent = `На странице: ${currentRows.length}. Найдено: ${filtered.length} из ${rows.length}.`;
  $('export-tooltip').textContent = currentRows.length ? 'Экспортирует текущие видимые строки в JSON' : 'Нет данных для экспорта';
}
for (const [key, label] of Object.entries(labels)) {
  const wrapper = document.createElement('label'), checkbox = document.createElement('input');
  checkbox.type = 'checkbox'; checkbox.checked = true;
  checkbox.onchange = () => { checkbox.checked ? visible.add(key) : visible.delete(key); render(); };
  wrapper.append(checkbox, document.createTextNode(label)); $('columns').append(wrapper);
}
$('search').oninput = () => { page = 1; render(); };
$('page-size').onchange = () => { page = 1; render(); };
$('prev').onclick = () => { page--; render(); };
$('next').onclick = () => { page++; render(); };
$('export-wrapper').addEventListener('mouseenter', showTooltip);
$('export-wrapper').addEventListener('focusin', showTooltip);
$('export-wrapper').addEventListener('mouseleave', hideTooltip);
$('export-wrapper').addEventListener('focusout', hideTooltip);
document.addEventListener('keydown', event => { if (event.key === 'Escape') hideTooltip(); });
$('export').onclick = async () => {
  if (busy || !currentRows.length) return;
  const snapshot = currentRows.map(row => Object.fromEntries([...visible].map(key => [key, row[key]])));
  const query = $('search').value.trim();
  const filters = query ? {search: query} : {};
  busy = true; $('toast').hidden = true; render();
  try {
    const response = await fetch('/export', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({data: snapshot, filters_applied: filters})});
    if (response.status === 409 && (await response.json()).error === 'empty_dataset') return;
    if (!response.ok) throw new Error('Export failed');
    const blob = await response.blob();
    const filename = /filename="([^"]+)"/.exec(response.headers.get('Content-Disposition') || '')?.[1];
    if (!filename) throw new Error('Missing filename');
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  } catch (error) {
    $('toast').textContent = 'Не удалось выполнить экспорт. Попробуйте позже';
    $('toast').hidden = false; clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { $('toast').hidden = true; }, 6000);
  } finally { busy = false; render(); }
};
render();
