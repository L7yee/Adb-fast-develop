const { collect, shellArgs } = require('./adb');

const DISPLAY_SCRIPT = `
printf '\\n__ADB_SCREEN__ wm\\n'
wm size 2>/dev/null
printf '\\n__ADB_SCREEN__ cmdline\\n'
cat /proc/cmdline 2>/dev/null
printf '\\n__ADB_SCREEN__ bootconfig\\n'
cat /proc/bootconfig 2>/dev/null
printf '\\n__ADB_SCREEN__ properties\\n'
getprop | grep -iE 'lcd|lcm|panel|ddi'
for f in /sys/class/graphics/fb0/panel_name /sys/class/graphics/fb0/lcm_name /sys/class/lcd/panel/lcd_type /sys/class/graphics/fb0/panel_id /sys/class/lcd/panel/window_type /sys/class/lcd/panel/ddi_name /sys/class/lcd/panel/ddi_id /sys/class/graphics/fb0/ddi_name /sys/class/drm/card*-DSI-*/panel_name /sys/class/drm/card*-DSI-*/panel_id /sys/class/drm/card*-DSI-*/ddi_name /sys/class/drm/card*-DSI-*/modes; do
  if [ -r "$f" ]; then
    printf '\\n__ADB_SCREEN__ %s\\n' "$f"
    head -c 4096 "$f" 2>/dev/null
  fi
done
exit 0
`;

const KEYS = {
  panel: ['lcd_name', 'lcm_name', 'panel_name', 'androidboot.lcd_name', 'androidboot.lcm_name', 'androidboot.panel_name', 'mdss_mdp.panel', 'msm_drm.dsi_display0'],
  panelId: ['lcd_id', 'lcm_id', 'panel_id', 'androidboot.lcd_id', 'androidboot.panel_id'],
  ddi: ['ddi_name', 'ddi', 'androidboot.ddi_name', 'androidboot.ddi'],
  resolution: ['lcd_size', 'androidboot.lcd_size']
};
const PROPERTIES = {
  panel: ['ro.boot.lcd_name', 'ro.boot.lcm_name', 'ro.boot.panel_name', 'ro.vendor.lcd_name', 'ro.vendor.panel_name'],
  panelId: ['ro.boot.lcd_id', 'ro.boot.panel_id', 'ro.vendor.lcd_id'],
  ddi: ['ro.boot.ddi_name', 'ro.boot.ddi', 'ro.vendor.ddi_name', 'ro.vendor.lcd.ddi']
};

function clean(value) {
  const text = String(value || '').replace(/\0/g, '').trim().replace(/^['"]|['"]$/g, '').trim();
  return !text || /^(unknown|null|none|n\/a|not found)$/i.test(text) ? null : text;
}

function dimensions(value) {
  const match = String(value || '').match(/^(\d{2,5})\s*[x×]\s*(\d{2,5})$/i);
  return match ? `${Number(match[1])} × ${Number(match[2])}` : null;
}

function parseDisplayInfo(output) {
  const sections = new Map();
  let source;
  for (const line of output.replace(/\r/g, '').split('\n')) {
    const marker = line.match(/^__ADB_SCREEN__ (.+)$/);
    if (marker) { source = marker[1]; sections.set(source, ''); }
    else if (source) sections.set(source, sections.get(source) + line + '\n');
  }
  const info = { resolution: null, overrideResolution: null, panel: null, panelId: null, ddi: null };
  const wm = sections.get('wm') || '';
  for (const [label, field] of [['Physical', 'resolution'], ['Override', 'overrideResolution']]) {
    const match = wm.match(new RegExp(`${label} size:\\s*(\\d+x\\d+)`, 'i'));
    if (match && dimensions(match[1])) info[field] = { value: dimensions(match[1]), source: `wm size · ${label}` };
  }
  if (!info.resolution) info.resolution = info.overrideResolution;

  for (const name of ['cmdline', 'bootconfig']) {
    const text = sections.get(name) || '';
    const values = new Map();
    const pattern = name === 'cmdline' ? /(?:^|\s)([\w.,-]+)=("[^"]*"|'[^']*'|\S+)/g : /^\s*([\w.,-]+)\s*=\s*(.*?)\s*$/gm;
    for (const match of text.matchAll(pattern)) values.set(match[1], clean(match[2]));
    for (const [field, keys] of Object.entries(KEYS)) {
      if (info[field]) continue;
      const key = keys.find((candidate) => values.get(candidate));
      if (key) {
        const value = field === 'resolution' ? dimensions(values.get(key)) : values.get(key);
        if (value) info[field] = { value, source: `/proc/${name} · ${key}` };
      }
    }
  }

  const properties = new Map();
  for (const match of (sections.get('properties') || '').matchAll(/^\[([^\]]+)\]: \[(.*?)\]$/gm)) properties.set(match[1], clean(match[2]));
  for (const [field, keys] of Object.entries(PROPERTIES)) {
    const key = keys.find((candidate) => properties.get(candidate));
    if (!info[field] && key) info[field] = { value: properties.get(key), source: `getprop · ${key}` };
  }
  for (const [file, text] of sections) {
    if (!file.startsWith('/sys/')) continue;
    const value = clean(text);
    if (!value) continue;
    const field = /\/(panel_name|lcm_name|lcd_type)$/.test(file) ? 'panel'
      : /\/(panel_id|window_type)$/.test(file) ? 'panelId'
        : /\/(ddi_name|ddi_id)$/.test(file) ? 'ddi' : null;
    if (field && !info[field]) info[field] = { value, source: file };
    if (!info.resolution && file.endsWith('/modes')) {
      const modes = [...new Set(text.trim().split('\n').map(dimensions).filter(Boolean))];
      if (modes.length === 1) info.resolution = { value: modes[0], source: file };
    }
  }
  return info;
}

async function readDisplayInfo(serial, root = false, execute = collect) {
  const result = await execute(['-s', serial, 'shell', DISPLAY_SCRIPT], 10000);
  if (result.timedOut) throw new Error('屏幕信息读取超时，请重试');
  if (result.code !== 0) throw new Error(result.stderr.trim() || '屏幕信息读取失败');
  const info = parseDisplayInfo(result.stdout);
  if (root && ['resolution', 'panel', 'panelId', 'ddi'].some((key) => !info[key])) {
    try {
      const elevated = await execute(shellArgs(serial, { requires_root: true, shell_command: DISPLAY_SCRIPT }), 10000);
      if (elevated.code === 0 && !elevated.timedOut) {
        const extra = parseDisplayInfo(elevated.stdout);
        for (const key of Object.keys(info)) {
          if (!info[key] && extra[key]) info[key] = { ...extra[key], source: `Root · ${extra[key].source}` };
        }
      }
    } catch { /* Keep the fields already available without su. */ }
  }
  return { serial, ...info, readAt: Date.now() };
}

module.exports = { parseDisplayInfo, readDisplayInfo };
