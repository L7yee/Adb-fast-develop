const { app } = require('electron');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const temp = fs.mkdtempSync(path.join(os.tmpdir(), 'adb-dashboard-ui-'));
app.setPath('userData', temp);
app.on('browser-window-created', (_event, win) => {
  win.webContents.once('did-finish-load', async () => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 1600));
      const info = await win.webContents.executeJavaScript(`({title: document.title, cards: document.querySelectorAll('.command-card').length, status: document.getElementById('device-title').textContent, errors: document.getElementById('toast').textContent})`);
      if (info.cards < 10) throw new Error(`Only ${info.cards} commands rendered`);
      const shot = await win.capturePage();
      fs.writeFileSync(path.join(__dirname, '..', 'preview.png'), shot.toPNG());
      const interactions = await win.webContents.executeJavaScript(`(async () => {
        document.getElementById('add-command').click();
        const form = document.getElementById('command-form');
        form.elements.label.value = 'Smoke test';
        form.elements.id.value = 'smoke_test';
        form.elements.shell_command.value = 'echo ok';
        form.requestSubmit();
        await new Promise(resolve => setTimeout(resolve, 300));
        const added = document.querySelectorAll('.command-card').length;
        document.getElementById('manage-command').click();
        const managed = document.querySelectorAll('.manager-item').length;
        document.getElementById('manager-dialog').close();
        document.getElementById('open-converter').click();
        document.getElementById('converter-input').value = '01 02';
        document.getElementById('convert-plain').click();
        const converted = document.getElementById('converter-output').value;
        return { added, managed, converted };
      })()`);
      if (interactions.added !== info.cards + 1 || interactions.managed !== info.cards + 1 || interactions.converted !== '15 00 00 02 01 02') throw new Error(`UI interaction failed: ${JSON.stringify(interactions)}`);
      console.log(JSON.stringify({ ...info, interactions }));
      app.quit();
    } catch (error) {
      console.error(error);
      process.exitCode = 1;
      app.quit();
    }
  });
});
app.on('will-quit', () => fs.rmSync(temp, { recursive: true, force: true }));
require('../main');
