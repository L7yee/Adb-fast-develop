const { app, BrowserWindow } = require('electron');
const fs = require('node:fs');
const path = require('node:path');

app.whenReady().then(async () => {
  const svg = fs.readFileSync(path.join(__dirname, '..', 'resources', 'icon.svg'), 'utf8');
  const win = new BrowserWindow({ width: 256, height: 256, show: false, frame: false, transparent: true, backgroundColor: '#00000000', webPreferences: { sandbox: true } });
  const html = `<html><body style="margin:0;background:transparent"><img width="256" height="256" src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}"></body></html>`;
  await win.loadURL(`data:text/html;base64,${Buffer.from(html).toString('base64')}`);
  win.showInactive();
  await new Promise((resolve) => setTimeout(resolve, 300));
  const png = (await win.capturePage()).toPNG();
  fs.writeFileSync(path.join(__dirname, '..', 'resources', 'icon.png'), png);
  const header = Buffer.alloc(22);
  header.writeUInt16LE(1, 2); // icon
  header.writeUInt16LE(1, 4); // one image
  header.writeUInt16LE(1, 10); // color planes
  header.writeUInt16LE(32, 12); // bit depth
  header.writeUInt32LE(png.length, 14);
  header.writeUInt32LE(22, 18);
  fs.writeFileSync(path.join(__dirname, '..', 'resources', 'icon.ico'), Buffer.concat([header, png]));
  app.quit();
}).catch((error) => { console.error(error); app.exit(1); });
