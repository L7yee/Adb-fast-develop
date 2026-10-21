const $ = (id) => document.getElementById(id);
const api = window.dashboard;
const categoryNames = { all: '全部命令', read: '读取信息', streaming: '实时监控', action: '快捷操作' };
const categoryDescriptions = { all: '你常用的 ADB 操作都在这里', read: '快速读取设备状态与系统信息', streaming: '持续观察设备事件和日志', action: '一键执行常用设备操作' };
let commands = [];
let device = { state: 'disconnected' };
let category = 'all';
let editingId = null;
let reorder = false;
let activeId = null;
let running = false;
let auto = null;
let autoTimer = null;
let output = '';
let previous = new Map();
let toastTimer;

function toast(message) {
  $('toast').textContent = message;
  $('toast').classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => $('toast').classList.remove('show'), 2900);
}

function setOutput(text, append = false) {
  output = append ? output + text : text;
  $('output-text').textContent = output;
  $('output-text').scrollTop = $('output-text').scrollHeight;
}

function setOutputState(label, kind = '') {
  $('output-state').textContent = label;
  $('output-state').className = `output-pill ${kind}`;
  $('stop').disabled = !running && !auto;
}

function renderDevice() {
  const connected = device.state === 'connected';
  const names = { connected: '已连接', disconnected: '未连接', unauthorized: '等待授权', multiple: '多台设备', missing: '未找到 ADB', error: '连接异常' };
  $('device-title').textContent = names[device.state] || '检测中';
  $('device-subtitle').textContent = device.message || '正在检测…';
  $('device-dot').className = `status-dot ${connected ? 'connected' : device.state === 'disconnected' ? '' : 'error'}`;
  $('overview-device').textContent = connected ? device.serial : (names[device.state] || '检测中');
  $('overview-root').textContent = connected ? (device.root ? '已获得' : '未获得') : '—';
  $('install-apk').disabled = !connected;
  renderCards();
}

function renderCards() {
  const query = $('search').value.trim().toLowerCase();
  const visible = commands.filter((item) => (category === 'all' || item.category === category) && (!query || `${item.label} ${item.shell_command}`.toLowerCase().includes(query)));
  const grid = $('command-grid');
  grid.replaceChildren();
  for (const item of visible) {
    const card = document.createElement('article');
    card.className = `command-card ${activeId === item.id && running ? 'running' : ''}`;
    card.draggable = reorder;
    card.dataset.id = item.id;
    const icon = { read: '◫', streaming: '◉', action: '↗' }[item.category];
    card.innerHTML = `<div class="card-top"><span class="card-icon ${item.category}">${icon}</span><button class="card-menu" title="编辑命令" aria-label="编辑命令">···</button></div><div class="card-main"><h3></h3><code></code></div><div class="card-footer"><div class="card-tags"></div><div class="card-actions"></div></div>`;
    card.querySelector('h3').textContent = item.label;
    card.querySelector('code').textContent = item.shell_command;
    card.querySelector('.card-menu').addEventListener('click', () => openCommandDialog(item));
    const tags = card.querySelector('.card-tags');
    const type = document.createElement('span');
    type.className = 'tag';
    type.textContent = categoryNames[item.category];
    tags.append(type);
    if (item.requires_root) {
      const root = document.createElement('span');
      root.className = 'tag root';
      root.textContent = 'ROOT';
      tags.append(' ', root);
    }
    const actions = card.querySelector('.card-actions');
    if (item.auto_refresh_capable) {
      const select = document.createElement('select');
      select.className = `refresh-select ${auto?.id === item.id ? 'active' : ''}`;
      select.title = '自动刷新间隔';
      for (const [value, label] of [['0', '自动'], ['1', '1秒'], ['5', '5秒'], ['10', '10秒'], ['30', '30秒']]) {
        const option = document.createElement('option'); option.value = value; option.textContent = label; select.append(option);
      }
      select.value = auto?.id === item.id ? String(auto.seconds) : '0';
      select.addEventListener('change', () => setAuto(item, Number(select.value)));
      actions.append(select);
    }
    const run = document.createElement('button');
    run.className = 'run-button';
    run.textContent = activeId === item.id && running ? '运行中…' : '运行 ↗';
    run.disabled = device.state !== 'connected' || reorder;
    run.addEventListener('click', () => runCommand(item));
    actions.append(run);
    card.addEventListener('dragstart', (event) => { if (!reorder) return; event.dataTransfer.setData('text/plain', item.id); card.classList.add('dragging'); });
    card.addEventListener('dragend', () => card.classList.remove('dragging'));
    card.addEventListener('dragover', (event) => { if (reorder) event.preventDefault(); });
    card.addEventListener('drop', async (event) => {
      if (!reorder) return;
      event.preventDefault();
      const source = event.dataTransfer.getData('text/plain');
      const from = commands.findIndex((command) => command.id === source);
      const to = commands.findIndex((command) => command.id === item.id);
      if (from < 0 || to < 0 || from === to) return;
      const ids = commands.map((command) => command.id);
      ids.splice(to, 0, ids.splice(from, 1)[0]);
      try { commands = await api.reorderCommands(ids); renderCards(); toast('命令顺序已保存'); }
      catch (error) { toast(error.message); }
    });
    grid.append(card);
  }
  $('visible-count').textContent = visible.length;
  $('empty-state').hidden = visible.length !== 0;
  $('overview-count').textContent = `${commands.length} 个`;
  for (const key of Object.keys(categoryNames)) $('count-' + key).textContent = key === 'all' ? commands.length : commands.filter((item) => item.category === key).length;
}

function stopAuto() {
  if (autoTimer) clearInterval(autoTimer);
  autoTimer = null;
  auto = null;
  renderCards();
}

function setAuto(item, seconds) {
  stopAuto();
  if (!seconds) return;
  if (device.state !== 'connected') { toast('请先连接设备'); return; }
  auto = { id: item.id, seconds };
  runCommand(item, true);
  autoTimer = setInterval(() => { if (!running && auto?.id === item.id) runCommand(item, true); }, seconds * 1000);
  renderCards();
}

async function runCommand(item, fromAuto = false) {
  if (!fromAuto) stopAuto();
  if (running) await api.stop();
  activeId = item.id;
  running = true;
  $('output-label').textContent = item.label;
  $('output-shell').textContent = `adb shell ${item.shell_command}`;
  $('compare-note').hidden = true;
  setOutputState(item.category === 'streaming' ? '实时输出' : '执行中', 'running');
  renderCards();
  try { await api.runCommand(item.id); }
  catch (error) {
    running = false;
    if (fromAuto) stopAuto();
    setOutput(`错误：${error.message}`);
    setOutputState('出错', 'error');
    renderCards();
  }
}

function showComparison(before, after) {
  const oldLines = before.split('\n');
  const newLines = after.split('\n');
  const view = $('output-text');
  view.replaceChildren();
  const max = Math.max(oldLines.length, newLines.length);
  let changes = 0;
  for (let i = 0; i < max; i++) {
    if (oldLines[i] === newLines[i]) {
      view.append(document.createTextNode((newLines[i] || '') + '\n'));
    } else {
      changes++;
      if (oldLines[i] !== undefined) {
        const removed = document.createElement('span'); removed.className = 'removed'; removed.textContent = `− ${oldLines[i]}\n`; view.append(removed);
      }
      if (newLines[i] !== undefined) {
        const added = document.createElement('span'); added.className = 'added'; added.textContent = `+ ${newLines[i]}\n`; view.append(added);
      }
    }
  }
  $('compare-note').textContent = changes ? `与上次相比有 ${changes} 行变化` : '与上次结果相同';
  $('compare-note').hidden = false;
}

function onAdbEvent(event) {
  if (event.type === 'stopped') { running = false; setOutputState(auto ? '自动刷新' : '已停止'); renderCards(); return; }
  if (event.type === 'start') {
    running = true;
    activeId = event.id;
    $('output-label').textContent = event.label;
    $('output-shell').textContent = event.id === '__install__' ? event.shell : `adb shell ${event.shell}`;
    $('compare-note').hidden = true;
    if (event.streaming) setOutput(`[${new Date().toLocaleTimeString()}] ${event.label}\n${$('output-shell').textContent}\n${'─'.repeat(48)}\n`);
    setOutputState(event.streaming ? '实时输出' : '执行中', 'running');
    renderCards();
    return;
  }
  if (event.type === 'chunk') { setOutput(event.text, true); return; }
  if (event.type === 'error') {
    running = false;
    if (auto) stopAuto();
    setOutput(`${output ? output + '\n' : ''}错误：${event.message}`);
    setOutputState('出错', 'error');
    renderCards();
    return;
  }
  if (event.type === 'complete') {
    running = false;
    if (!event.streaming) {
      output = event.output || '命令已完成，没有返回内容。';
      if ($('compare-toggle').checked && previous.has(event.id)) showComparison(previous.get(event.id), output);
      else setOutput(output);
      if ($('compare-toggle').checked) previous.set(event.id, output);
    }
    setOutputState(auto ? '自动刷新' : '已完成');
    renderCards();
  }
}

function openCommandDialog(item = null) {
  if ($('manager-dialog').open) $('manager-dialog').close();
  editingId = item?.id || null;
  const form = $('command-form');
  form.reset();
  for (const field of ['id', 'label', 'shell_command', 'category']) form.elements[field].value = item?.[field] || (field === 'category' ? 'read' : '');
  form.elements.auto_refresh_capable.checked = Boolean(item?.auto_refresh_capable);
  form.elements.requires_root.checked = Boolean(item?.requires_root);
  $('command-dialog-title').textContent = item ? '编辑命令' : '新建命令';
  $('delete-command').hidden = !item;
  $('form-error').hidden = true;
  $('command-dialog').showModal();
  form.elements.label.focus();
}

function openManager() {
  const list = $('manager-list');
  list.replaceChildren();
  for (const item of commands) {
    const row = document.createElement('button');
    row.className = 'manager-item';
    const info = document.createElement('span');
    const name = document.createElement('strong'); name.textContent = item.label;
    const shell = document.createElement('small'); shell.textContent = item.shell_command;
    info.append(name, shell);
    const edit = document.createElement('span'); edit.textContent = '编辑 ›';
    row.append(info, edit);
    row.addEventListener('click', () => openCommandDialog(item));
    list.append(row);
  }
  $('manager-dialog').showModal();
}

async function saveCommand(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const command = {
    id: form.elements.id.value.trim(), label: form.elements.label.value.trim(),
    shell_command: form.elements.shell_command.value.trim(), category: form.elements.category.value,
    auto_refresh_capable: form.elements.auto_refresh_capable.checked,
    requires_root: form.elements.requires_root.checked
  };
  try {
    commands = await api.saveCommand(command, editingId);
    $('command-dialog').close();
    renderCards();
    toast('命令已保存');
  } catch (error) { $('form-error').textContent = error.message; $('form-error').hidden = false; }
}

function convert(format) {
  const error = $('converter-error'); error.hidden = true;
  const prefix = [ $('short-prefix').value.trim(), $('long-prefix').value.trim() ];
  if (prefix.some((value) => !/^[\da-fA-F]{2}$/.test(value))) { error.textContent = '前缀必须是两位十六进制数'; error.hidden = false; return; }
  const lines = $('converter-input').value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (!lines.length) { error.textContent = '请先输入数据'; error.hidden = false; return; }
  const converted = [];
  for (let i = 0; i < lines.length; i++) {
    const bytes = lines[i].split(/\s+/);
    if (bytes.some((part) => !/^[\da-fA-F]{2}$/.test(part))) { error.textContent = `第 ${i + 1} 行有无效字节`; error.hidden = false; return; }
    if (bytes.length > 255) { error.textContent = `第 ${i + 1} 行超过 255 字节`; error.hidden = false; return; }
    const values = [bytes.length === 2 ? prefix[0] : prefix[1], '00', '00', bytes.length.toString(16).padStart(2, '0'), ...bytes].map((value) => value.toUpperCase());
    converted.push(format === 'cstyle' ? values.map((value) => `0x${value}`).join(', ') + ',' : values.join(' '));
  }
  $('converter-output').value = converted.join('\n');
}

async function refreshCommands() { commands = await api.listCommands(); renderCards(); }

document.querySelectorAll('#category-nav .nav-item').forEach((button) => button.addEventListener('click', () => {
  category = button.dataset.category;
  document.querySelectorAll('#category-nav .nav-item').forEach((item) => item.classList.toggle('active', item === button));
  $('page-title').textContent = categoryNames[category];
  $('breadcrumb-current').textContent = categoryNames[category];
  $('category-description').textContent = categoryDescriptions[category];
  renderCards();
}));
$('search').addEventListener('input', renderCards);
$('add-command').addEventListener('click', () => openCommandDialog());
$('manage-command').addEventListener('click', openManager);
$('manager-add').addEventListener('click', () => openCommandDialog());
$('command-form').addEventListener('submit', saveCommand);
$('delete-command').addEventListener('click', async () => {
  if (!editingId || !confirm('确定删除这条命令吗？')) return;
  try { commands = await api.deleteCommand(editingId); $('command-dialog').close(); renderCards(); toast('命令已删除'); }
  catch (error) { $('form-error').textContent = error.message; $('form-error').hidden = false; }
});
document.querySelectorAll('[data-close]').forEach((button) => button.addEventListener('click', () => $(button.dataset.close).close()));
$('reorder').addEventListener('click', () => { reorder = !reorder; $('reorder').classList.toggle('active', reorder); $('reorder').textContent = reorder ? '完成排序' : '调整顺序'; renderCards(); });
$('refresh-device').addEventListener('click', async () => { device = await api.checkDevice(); renderDevice(); toast(device.state === 'connected' ? '设备已连接' : device.message); });
$('install-apk').addEventListener('click', async () => { stopAuto(); try { await api.installApk(); } catch (error) { toast(error.message); } });
$('open-converter').addEventListener('click', () => $('converter-dialog').showModal());
$('convert-plain').addEventListener('click', () => convert('plain'));
$('convert-cstyle').addEventListener('click', () => convert('cstyle'));
$('copy-converted').addEventListener('click', async () => { await navigator.clipboard.writeText($('converter-output').value); toast('已复制转换结果'); });
$('stop').addEventListener('click', async () => { stopAuto(); await api.stop(); running = false; setOutputState('已停止'); renderCards(); });
$('clear').addEventListener('click', async () => { stopAuto(); await api.stop(); running = false; setOutput(''); setOutputState('就绪'); });
$('copy').addEventListener('click', async () => { await navigator.clipboard.writeText(output); toast('已复制输出'); });
$('save').addEventListener('click', async () => { if (await api.saveOutput(output)) toast('输出已保存'); });
$('compare-toggle').addEventListener('change', () => { previous.clear(); $('compare-note').hidden = true; });
document.addEventListener('keydown', (event) => {
  const modifier = event.ctrlKey || event.metaKey;
  const editing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName);
  if (modifier && event.key.toLowerCase() === 'r') { event.preventDefault(); $('refresh-device').click(); }
  if (modifier && event.key.toLowerCase() === 's' && !editing) { event.preventDefault(); $('save').click(); }
  if (modifier && event.key.toLowerCase() === 'c' && !editing && !window.getSelection().toString()) { event.preventDefault(); $('copy').click(); }
  if (event.key === 'Escape' && !document.querySelector('dialog[open]')) { $('stop').click(); }
  if (modifier && /^[0-9]$/.test(event.key) && !editing) {
    const index = event.key === '0' ? 9 : Number(event.key) - 1;
    if (commands[index]) { event.preventDefault(); runCommand(commands[index]); }
  }
});
api.onAdbEvent(onAdbEvent);
api.onDeviceChanged((next) => { device = next; if (next.state !== 'connected' && auto) stopAuto(); renderDevice(); });
refreshCommands().catch((error) => toast(error.message));
api.checkDevice().then((next) => { device = next; renderDevice(); });
