const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('dashboard', {
  listCommands: () => ipcRenderer.invoke('commands:list'),
  saveCommand: (command, previousId) => ipcRenderer.invoke('commands:save', command, previousId),
  deleteCommand: (id) => ipcRenderer.invoke('commands:delete', id),
  reorderCommands: (ids) => ipcRenderer.invoke('commands:reorder', ids),
  checkDevice: () => ipcRenderer.invoke('device:check'),
  runCommand: (id) => ipcRenderer.invoke('adb:run', id),
  stop: () => ipcRenderer.invoke('adb:stop'),
  installApk: () => ipcRenderer.invoke('apk:install'),
  saveOutput: (content) => ipcRenderer.invoke('output:save', content),
  onAdbEvent: (handler) => ipcRenderer.on('adb:event', (_event, data) => handler(data)),
  onDeviceChanged: (handler) => ipcRenderer.on('device:changed', (_event, data) => handler(data))
});
