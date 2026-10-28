const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const fs = require('node:fs');
const path = require('node:path');
const { CommandStore } = require('./config');
const { AdbRunner, checkDevice, rootDevice } = require('./adb');
const { readDisplayInfo } = require('./display-info');

let window;
let store;
let runner;
let device = { state: 'disconnected' };
let checking = null;
let rootedSerial = null;
let missedDeviceChecks = 0;
const LOG_COMMANDS = {
  kernel: { id: '__kernel_log__', label: '内核日志', shell_command: 'dmesg' },
  logcat: { id: '__logcat_log__', label: 'Logcat 日志', shell_command: 'logcat -d' }
};

function settingsPath() { return path.join(app.getPath('userData'), 'window.json'); }
function logPathsFile() { return path.join(app.getPath('userData'), 'log-paths.json'); }

function logPaths() {
  const defaults = {
    kernel: path.join(app.getPath('documents'), 'kernel-log.txt'),
    logcat: path.join(app.getPath('documents'), 'logcat-log.txt')
  };
  try { return { ...defaults, ...JSON.parse(fs.readFileSync(logPathsFile(), 'utf8')) }; }
  catch { return defaults; }
}

function setLogPath(kind, filePath) {
  if (!LOG_COMMANDS[kind]) throw new Error('日志类型无效');
  if (typeof filePath !== 'string' || !path.isAbsolute(filePath.trim())) throw new Error('请输入完整的保存路径');
  const next = { ...logPaths(), [kind]: filePath.trim() };
  fs.writeFileSync(logPathsFile(), JSON.stringify(next), 'utf8');
  return next[kind];
}

function savedBounds() {
  try { return JSON.parse(fs.readFileSync(settingsPath(), 'utf8')); }
  catch { return { width: 1280, height: 800 }; }
}

function createWindow() {
  const bounds = savedBounds();
  window = new BrowserWindow({
    width: Math.max(940, bounds.width || 1280),
    height: Math.max(640, bounds.height || 800),
    x: bounds.x,
    y: bounds.y,
    minWidth: 940,
    minHeight: 640,
    title: 'ADB Dashboard',
    icon: path.join(__dirname, 'resources', 'icon.png'),
    backgroundColor: '#f5f5f7',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });
  window.removeMenu();
  window.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  window.once('ready-to-show', () => {
    if (bounds.maximized) window.maximize();
    window.show();
  });
  window.on('close', () => {
    const next = { ...window.getNormalBounds(), maximized: window.isMaximized() };
    fs.writeFileSync(settingsPath(), JSON.stringify(next));
    runner.stop();
  });
  runner = new AdbRunner((event) => {
    if (window && !window.isDestroyed()) window.webContents.send('adb:event', event);
  });
}

async function refreshDevice() {
  if (checking) return checking;
  checking = checkDevice().then(async (detected) => {
    let result = detected;
    if (result.state === 'connected' && rootedSerial !== result.serial) {
      rootedSerial = result.serial;
      try { await rootDevice(result.serial); } catch { /* Keep checking if adb root is unavailable. */ }
      result = await checkDevice();
    }
    const wasConnected = device.state === 'connected';
    device = result;
    if (window && !window.isDestroyed()) window.webContents.send('device:changed', result);
    if (wasConnected && result.state !== 'connected') runner.stop();
    if (result.state === 'connected') {
      missedDeviceChecks = 0;
    } else if (result.state === 'disconnected' && ++missedDeviceChecks >= 3) {
      rootedSerial = null;
    } else if (result.state !== 'disconnected') {
      missedDeviceChecks = 0;
    }
    return result;
  }).finally(() => { checking = null; });
  return checking;
}

app.whenReady().then(() => {
  store = new CommandStore(app.getPath('userData'), path.join(__dirname, 'config', 'commands.yaml'));
  createWindow();
  refreshDevice();
  const poll = setInterval(refreshDevice, 5000);
  app.on('before-quit', () => clearInterval(poll));
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });

ipcMain.handle('commands:list', () => store.read());
ipcMain.handle('commands:save', (_event, command, previousId) => store.save(command, previousId));
ipcMain.handle('commands:delete', (_event, id) => store.delete(id));
ipcMain.handle('commands:reorder', (_event, ids) => store.reorder(ids));
ipcMain.handle('device:check', refreshDevice);
ipcMain.handle('device:display', async () => {
  const current = await refreshDevice();
  if (current.state !== 'connected') throw new Error(current.message || '设备未连接');
  return readDisplayInfo(current.serial, current.root);
});
ipcMain.handle('adb:run', async (_event, id) => {
  const command = store.read().find((item) => item.id === id);
  if (!command) throw new Error('命令不存在');
  const current = await refreshDevice();
  if (current.state !== 'connected') throw new Error(current.message || '设备未连接');
  if (command.requires_root && !current.root) throw new Error('该命令需要 root 权限');
  runner.run(command, current.serial);
  return true;
});
ipcMain.handle('logs:paths', () => logPaths());
ipcMain.handle('logs:path:set', (_event, kind, filePath) => setLogPath(kind, filePath));
ipcMain.handle('logs:path:choose', async (_event, kind) => {
  if (!LOG_COMMANDS[kind]) throw new Error('日志类型无效');
  const choice = await dialog.showSaveDialog(window, { title: `选择${LOG_COMMANDS[kind].label}保存位置`, defaultPath: logPaths()[kind], filters: [{ name: '文本文件', extensions: ['txt', 'log'] }] });
  return choice.canceled ? null : setLogPath(kind, choice.filePath);
});
ipcMain.handle('logs:capture', async (_event, kind, filePath) => {
  if (!LOG_COMMANDS[kind]) throw new Error('日志类型无效');
  const destination = setLogPath(kind, filePath);
  const current = await refreshDevice();
  if (current.state !== 'connected') throw new Error(current.message || '设备未连接');
  runner.run({ ...LOG_COMMANDS[kind], requires_root: kind === 'kernel' && current.root }, current.serial, destination);
  return true;
});
ipcMain.handle('adb:stop', () => { runner.stop(); return true; });
ipcMain.handle('apk:install', async () => {
  const current = await refreshDevice();
  if (current.state !== 'connected') throw new Error(current.message || '设备未连接');
  const choice = await dialog.showOpenDialog(window, { title: '选择 APK', properties: ['openFile'], filters: [{ name: 'Android APK', extensions: ['apk'] }] });
  if (choice.canceled) return false;
  runner.install(choice.filePaths[0], current.serial);
  return true;
});
ipcMain.handle('output:save', async (_event, content) => {
  if (typeof content !== 'string' || !content.trim()) return false;
  const choice = await dialog.showSaveDialog(window, { title: '保存输出', defaultPath: 'adb-output.txt', filters: [{ name: '文本文件', extensions: ['txt'] }] });
  if (choice.canceled) return false;
  fs.writeFileSync(choice.filePath, content, 'utf8');
  return true;
});
