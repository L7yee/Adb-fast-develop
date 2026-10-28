const test = require('node:test');
const assert = require('node:assert/strict');
const { parseDisplayInfo, readDisplayInfo } = require('../display-info');

function snapshot(values) {
  return Object.entries(values).map(([source, text]) => `\n__ADB_SCREEN__ ${source}\n${text}\n`).join('');
}

test('reads the connected Unisoc panel from boot arguments and keeps physical and override sizes distinct', () => {
  const info = parseDisplayInfo(snapshot({
    wm: 'Physical size: 1600x2400\nOverride size: 1200x1800',
    cmdline: 'console=ttyS1 lcd_id=ID122015 lcd_name=lcd_jt122wqh009_mipi_wqxga2400 lcd_size=1600x2400',
    properties: '[ro.boot.panel_name]: [a_different_fallback_panel]\n[ro.hardware.sensors]: [himax]',
    '/sys/class/drm/card0-DSI-1/modes': '1600x2400'
  }));
  assert.equal(info.resolution.value, '1600 × 2400');
  assert.equal(info.overrideResolution.value, '1200 × 1800');
  assert.equal(info.panel.value, 'lcd_jt122wqh009_mipi_wqxga2400');
  assert.equal(info.panelId.value, 'ID122015');
  assert.match(info.panel.source, /cmdline.*lcd_name/);
  assert.equal(info.ddi, null);
});

test('supports bootconfig, Android properties and sysfs without treating LCD ID as DDI', () => {
  const info = parseDisplayInfo(snapshot({
    bootconfig: 'androidboot.panel_name = "panel with spaces"\nandroidboot.lcd_id = "0x1234"',
    properties: '[ro.boot.ddi_name]: [NT36523]\n[ro.boot.panel_name]: [fallback]',
    '/sys/class/lcd/panel/lcd_type': 'another_panel',
    '/sys/class/graphics/fb0/panel_id': '0xabcd'
  }));
  assert.equal(info.panel.value, 'panel with spaces');
  assert.equal(info.panelId.value, '0x1234');
  assert.equal(info.ddi.value, 'NT36523');
  assert.match(info.ddi.source, /getprop/);
  const sysfs = parseDisplayInfo(snapshot({
    '/sys/class/lcd/panel/lcd_type': 'SAMSUNG_panel\0',
    '/sys/class/lcd/panel/ddi_id': '01 23 45',
    '/sys/class/drm/card0-DSI-1/modes': '1080x2400\n1080x2400'
  }));
  assert.equal(sysfs.panel.value, 'SAMSUNG_panel');
  assert.equal(sysfs.ddi.value, '01 23 45');
  assert.equal(sysfs.resolution.value, '1080 × 2400');
  assert.equal(parseDisplayInfo(snapshot({ '/sys/class/drm/card0-DSI-1/modes': '1080x2400\n720x1600' })).resolution, null);
  assert.equal(parseDisplayInfo(snapshot({ cmdline: 'lcd_id=ID122015' })).ddi, null);
});

test('retains readable fields when optional root access fails and fills missing fields when it succeeds', async () => {
  const normal = snapshot({ wm: 'Physical size: 1600x2400', cmdline: 'lcd_name=selected_panel' });
  let calls = 0;
  const info = await readDisplayInfo('DEVICE', true, async (args) => {
    calls++;
    assert.deepEqual(args.slice(0, 3), ['-s', 'DEVICE', 'shell']);
    if (calls === 1) return { code: 0, stdout: normal };
    assert.match(args[3], /^su 0 sh -c /);
    return { code: 0, stdout: snapshot({ cmdline: 'lcd_name=other_panel ddi_name=IC1234' }) };
  });
  assert.equal(calls, 2);
  assert.equal(info.serial, 'DEVICE');
  assert.equal(info.panel.value, 'selected_panel');
  assert.equal(info.ddi.value, 'IC1234');
  assert.match(info.ddi.source, /^Root/);
  const partial = await readDisplayInfo('DEVICE', true, async () => {
    if (++calls === 3) return { code: 0, stdout: normal };
    throw new Error('su unavailable');
  });
  assert.equal(partial.panel.value, 'selected_panel');
  assert.equal(partial.ddi, null);
  await assert.rejects(readDisplayInfo('DEVICE', false, async () => ({ timedOut: true })), /超时/);
});
