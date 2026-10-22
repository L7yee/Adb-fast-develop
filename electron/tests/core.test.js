const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { EventEmitter } = require('node:events');
const { CommandStore, normalizeCommand } = require('../config');
const { AdbRunner, parseDevices, shellArgs } = require('../adb');

test('imports valid commands from the existing YAML and persists edits', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'adb-dashboard-'));
  try {
    const store = new CommandStore(dir, path.join(__dirname, '..', 'config', 'commands.yaml'));
    const original = store.read();
    assert.ok(original.length >= 10);
    assert.ok(original.every((command) => command.id && command.shell_command));
    const added = { id: 'test_command', label: '测试', shell_command: 'echo test', category: 'read' };
    store.save(added);
    assert.equal(store.read().at(-1).label, '测试');
    store.reorder(['test_command', ...original.map((command) => command.id)]);
    assert.equal(store.read()[0].id, 'test_command');
    store.delete('test_command');
    assert.equal(store.read().length, original.length);
    assert.throws(() => store.save({ ...added, id: 'bad id' }), /ID/);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test('migrates old streaming commands to one-shot commands', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'adb-dashboard-old-'));
  try {
    fs.writeFileSync(path.join(dir, 'commands.yaml'), `commands:
  - { id: dmesg, label: Kernel, shell_command: 'dmesg -w', category: streaming }
  - { id: events, label: Events, shell_command: 'getevent -l', category: streaming, auto_refresh_capable: true }
  - { id: logcat, label: Logcat, shell_command: logcat, category: streaming }
  - { id: mtk_engineer_mode, label: MTK, shell_command: 'am start example', category: streaming }
`);
    const commands = new CommandStore(dir, path.join(__dirname, '..', 'config', 'commands.yaml')).read();
    assert.equal(commands.length, 3);
    assert.equal(commands.find((item) => item.id === 'events').shell_command, 'getevent -lp');
    assert.equal(commands.find((item) => item.id === 'logcat').shell_command, 'logcat -d');
    assert.equal(commands.find((item) => item.id === 'mtk_engineer_mode').category, 'action');
    assert.ok(commands.every((item) => !('auto_refresh_capable' in item) && item.category !== 'streaming'));
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});

test('parses ADB states and keeps shell commands out of the host shell', () => {
  assert.deepEqual(parseDevices('List of devices attached\nABC\tdevice\nDEF\tunauthorized\n'), [
    { serial: 'ABC', state: 'device' }, { serial: 'DEF', state: 'unauthorized' }
  ]);
  const command = normalizeCommand({ id: 'one', label: 'One', shell_command: 'echo a && echo b', category: 'read' });
  assert.deepEqual(shellArgs('ABC', command), ['-s', 'ABC', 'shell', 'echo a && echo b']);
  assert.match(shellArgs('ABC', { ...command, requires_root: true })[3], /^su 0 sh -c /);
});

test('retries a deprecated SDK install once with the bypass flag and keeps -g', async () => {
  const apkPath = 'C:\\apps\\old target.apk';
  const calls = [];
  const events = [];
  const responses = [
    { code: 1, stderr: 'Failure [INSTALL_FAILED_DEPRECATED_SDK_VERSION: found 20]' },
    { code: 0, stdout: 'Success' }
  ];
  const terminal = new Promise((resolve) => {
    const runner = new AdbRunner((event) => {
      events.push(event);
      if (event.type === 'complete' || event.type === 'error') resolve(event);
    }, (file, args) => {
      calls.push({ file, args });
      const child = new EventEmitter();
      child.stdout = new EventEmitter();
      child.stderr = new EventEmitter();
      child.kill = () => {};
      const response = responses.shift();
      setImmediate(() => {
        if (response.stdout) child.stdout.emit('data', Buffer.from(response.stdout));
        if (response.stderr) child.stderr.emit('data', Buffer.from(response.stderr));
        child.emit('close', response.code);
      });
      return child;
    });
    runner.install(apkPath, 'DEVICE');
  });
  const result = await terminal;
  assert.equal(result.type, 'complete');
  assert.match(result.output, /兼容参数重试.*Success/s);
  assert.equal(calls.length, 2);
  assert.deepEqual(calls[0].args, ['-s', 'DEVICE', 'install', '-r', '-g', apkPath]);
  assert.deepEqual(calls[1].args, ['-s', 'DEVICE', 'install', '--bypass-low-target-sdk-block', '-r', '-g', apkPath]);
  assert.ok(events.some((event) => event.type === 'chunk' && event.text.includes('兼容参数重试')));
});
