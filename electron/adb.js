const { spawn } = require('node:child_process');

function collect(args, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const child = spawn('adb', args, { windowsHide: true, shell: false });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => child.kill(), timeout);
    child.stdout.on('data', (data) => { stdout += data.toString(); });
    child.stderr.on('data', (data) => { stderr += data.toString(); });
    child.on('error', (error) => { clearTimeout(timer); reject(error); });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr, timedOut: child.killed });
    });
  });
}

function parseDevices(output) {
  return output.split(/\r?\n/).slice(1).map((line) => {
    const match = line.trim().match(/^(\S+)\s+(device|unauthorized|offline)\b/);
    return match && { serial: match[1], state: match[2] };
  }).filter(Boolean);
}

async function checkDevice() {
  let result;
  try { result = await collect(['devices'], 10000); }
  catch (error) {
    return { state: 'missing', message: error.code === 'ENOENT' ? '未找到 ADB，请安装 Android Platform Tools 并加入 PATH' : error.message };
  }
  if (result.code !== 0 || result.timedOut) return { state: 'error', message: result.stderr.trim() || 'ADB 响应超时' };
  const devices = parseDevices(result.stdout);
  const ready = devices.filter((item) => item.state === 'device');
  if (ready.length > 1) return { state: 'multiple', message: `检测到 ${ready.length} 台设备，请暂时只连接一台` };
  if (!ready.length) {
    if (devices.some((item) => item.state === 'unauthorized')) return { state: 'unauthorized', message: '请在设备上允许 USB 调试授权' };
    return { state: 'disconnected', message: '连接设备并开启 USB 调试' };
  }
  const serial = ready[0].serial;
  let root = false;
  try {
    const identity = await collect(['-s', serial, 'shell', 'id'], 5000);
    root = identity.stdout.includes('uid=0');
    if (!root) {
      const su = await collect(['-s', serial, 'shell', 'su 0 id'], 5000);
      root = su.stdout.includes('uid=0');
    }
  } catch { /* root status is optional */ }
  return { state: 'connected', serial, root, message: serial };
}

function shellArgs(serial, command) {
  if (!command.requires_root) return ['-s', serial, 'shell', command.shell_command];
  const quoted = command.shell_command.replace(/'/g, `'\\''`);
  return ['-s', serial, 'shell', `su 0 sh -c '${quoted}'`];
}

class AdbRunner {
  constructor(send) {
    this.send = send;
    this.child = null;
    this.sequence = 0;
  }

  stop() {
    this.sequence += 1;
    if (this.child) {
      this.child.kill();
      this.child = null;
    }
    this.send({ type: 'stopped' });
  }

  async run(command, serial) {
    this.stop();
    const sequence = this.sequence;
    const args = shellArgs(serial, command);
    const child = spawn('adb', args, { windowsHide: true, shell: false });
    this.child = child;
    this.send({ type: 'start', id: command.id, label: command.label, shell: command.shell_command, streaming: command.category === 'streaming' });
    let stdout = '';
    let stderr = '';
    let failed = false;
    const streaming = command.category === 'streaming';
    const timer = streaming ? null : setTimeout(() => child.kill(), 30000);
    child.stdout.on('data', (data) => {
      if (sequence !== this.sequence) return;
      const text = data.toString();
      if (streaming) this.send({ type: 'chunk', text });
      else stdout += text;
    });
    child.stderr.on('data', (data) => {
      if (sequence !== this.sequence) return;
      const text = data.toString();
      if (streaming) this.send({ type: 'chunk', text });
      else stderr += text;
    });
    child.on('error', (error) => {
      failed = true;
      if (sequence === this.sequence) this.send({ type: 'error', message: error.code === 'ENOENT' ? '未找到 ADB，请检查 PATH' : error.message });
    });
    child.on('close', (code) => {
      if (timer) clearTimeout(timer);
      if (sequence !== this.sequence) return;
      this.child = null;
      if (failed) return;
      if (code === 0) this.send({ type: 'complete', output: stdout.trim(), label: command.label, id: command.id, shell: command.shell_command, streaming });
      else this.send({ type: 'error', message: child.killed ? '命令执行超时或已停止' : (stderr.trim() || stdout.trim() || `命令退出码 ${code}`) });
    });
  }

  async install(apkPath, serial) {
    this.stop();
    const sequence = this.sequence;
    const child = spawn('adb', ['-s', serial, 'install', '-r', apkPath], { windowsHide: true, shell: false });
    this.child = child;
    let failed = false;
    this.send({ type: 'start', id: '__install__', label: '安装 APK', shell: apkPath, streaming: true });
    let output = '';
    for (const stream of [child.stdout, child.stderr]) {
      stream.on('data', (data) => {
        if (sequence !== this.sequence) return;
        const text = data.toString();
        output += text;
        this.send({ type: 'chunk', text });
      });
    }
    child.on('error', (error) => {
      failed = true;
      if (sequence === this.sequence) this.send({ type: 'error', message: error.message });
    });
    child.on('close', (code) => {
      if (sequence !== this.sequence) return;
      this.child = null;
      if (failed) return;
      if (code === 0) this.send({ type: 'complete', output: output.trim(), id: '__install__', streaming: true });
      else this.send({ type: 'error', message: output.trim() || `安装失败，退出码 ${code}` });
    });
  }
}

module.exports = { AdbRunner, checkDevice, parseDevices, shellArgs };
