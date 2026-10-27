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
      win.setContentSize(1280, 800);
      const info = await win.webContents.executeJavaScript(`({title: document.title, cards: document.querySelectorAll('.command-card').length, status: document.getElementById('device-title').textContent, errors: document.getElementById('toast').textContent})`);
      if (info.cards < 10) throw new Error(`Only ${info.cards} commands rendered`);
      const cardAction = await win.webContents.executeJavaScript(`(() => {
        const previousDevice = device;
        const originalRun = runCommand;
        let runs = 0;
        try {
          runCommand = () => { runs++; };
          device = { state: 'disconnected' };
          renderDevice();
          document.querySelector('.command-card').click();
          const disconnectedRuns = runs;
          device = { state: 'connected', serial: 'SMOKE', root: false };
          renderDevice();
          const card = document.querySelector('.command-card');
          card.click();
          card.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
          card.dispatchEvent(new KeyboardEvent('keydown', { key: ' ', bubbles: true }));
          card.querySelector('.card-menu').click();
          const menuOpened = document.getElementById('command-dialog').open;
          document.getElementById('command-dialog').close();
          return { disconnectedRuns, runs, menuOpened, runButtons: document.querySelectorAll('.run-button').length };
        } finally {
          runCommand = originalRun;
          device = previousDevice;
          renderDevice();
        }
      })()`);
      if (cardAction.disconnectedRuns !== 0 || cardAction.runs !== 3 || !cardAction.menuOpened || cardAction.runButtons !== 0) throw new Error(`Card click failed: ${JSON.stringify(cardAction)}`);
      const identity = await win.webContents.executeJavaScript(`(() => {
        const ids = ['overview-device', 'device-subtitle'];
        const before = ids.map(id => document.getElementById(id).textContent);
        document.getElementById('overview-device').textContent = '已连接';
        document.getElementById('device-subtitle').textContent = '设备已连接';
        return before;
      })()`);
      const shot = await win.capturePage();
      fs.writeFileSync(path.join(__dirname, '..', 'preview.png'), shot.toPNG());
      await win.webContents.executeJavaScript(`(() => {
        document.getElementById('overview-device').textContent = ${JSON.stringify(identity[0])};
        document.getElementById('device-subtitle').textContent = ${JSON.stringify(identity[1])};
      })()`);
      const sidebar = await win.webContents.executeJavaScript(`(() => {
        document.getElementById('sidebar-toggle').click();
        const collapsed = document.querySelector('.sidebar').classList.contains('collapsed');
        document.querySelector('[data-rail-workspace="logs"]').click();
        const railChanged = document.getElementById('breadcrumb-current').textContent === '日志';
        document.querySelector('[data-rail-workspace="commands"]').click();
        document.querySelector('.sidebar-search').click();
        const expanded = !document.querySelector('.sidebar').classList.contains('collapsed');
        const search = document.getElementById('search');
        search.value = 'MTK';
        search.dispatchEvent(new Event('input'));
        const filtered = document.querySelectorAll('.command-card').length;
        search.value = '';
        search.dispatchEvent(new Event('input'));
        return { collapsed, railChanged, expanded, filtered };
      })()`);
      if (!sidebar.collapsed || !sidebar.railChanged || !sidebar.expanded || sidebar.filtered < 1 || sidebar.filtered >= info.cards) throw new Error(`Sidebar interaction failed: ${JSON.stringify(sidebar)}`);
      win.setContentSize(1000, 700);
      const compact = await win.webContents.executeJavaScript(`(() => {
        const command = document.querySelector('.command-section').getBoundingClientRect();
        const result = document.querySelector('.output-section').getBoundingClientRect();
        return { commandHeight: command.height, resultTop: result.top, resultBottom: result.bottom, height: innerHeight };
      })()`);
      if (compact.commandHeight < 200 || compact.resultTop >= compact.height || compact.resultBottom > compact.height) throw new Error(`Compact layout failed: ${JSON.stringify(compact)}`);
      win.setContentSize(1280, 800);
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
        document.getElementById('converter-dialog').close();
        return { added, managed, converted };
      })()`);
      if (interactions.added !== info.cards + 1 || interactions.managed !== info.cards + 1 || interactions.converted !== '15 00 00 02 01 02') throw new Error(`UI interaction failed: ${JSON.stringify(interactions)}`);
      const clock = await win.webContents.executeJavaScript(`(() => {
        document.getElementById('open-mipi-clock').click();
        return { open: document.getElementById('mipi-clock-dialog').open, unit: document.getElementById('clock-needed').nextElementSibling.textContent,
          values: ['clock-needed', 'clock-divider', 'clock-fps', 'clock-mipi'].map(id => document.getElementById(id).textContent) };
      })()`);
      if (!clock.open || clock.unit !== 'Hz' || JSON.stringify(clock.values) !== JSON.stringify(['191,289,600', '1', '60', '1,280'])) throw new Error(`MIPI clock UI failed: ${JSON.stringify(clock)}`);
      const changedClock = await win.webContents.executeJavaScript(`(() => {
        const form = document.getElementById('mipi-clock-form');
        form.elements.sourceMHz.value = '300';
        form.requestSubmit();
        return ['clock-divider', 'clock-fps', 'clock-mipi'].map(id => document.getElementById(id).textContent);
      })()`);
      if (JSON.stringify(changedClock) !== JSON.stringify(['2', '47', '1,000'])) throw new Error(`MIPI clock recalculation failed: ${JSON.stringify(changedClock)}`);
      await win.webContents.executeJavaScript(`document.getElementById('mipi-clock-dialog').close()`);
      const paths = { kernel: path.join(temp, 'kernel.txt'), logcat: path.join(temp, 'logcat.txt') };
      const logs = await win.webContents.executeJavaScript(`(async () => {
        document.querySelector('[data-workspace="logs"]').click();
        const current = { heading: document.getElementById('breadcrumb-current').textContent, cards: document.querySelectorAll('.log-card').length, commandHidden: document.querySelector('.command-section').hidden };
        for (const [kind, filePath] of Object.entries(${JSON.stringify(paths)})) {
          document.getElementById(kind + '-path').value = filePath;
          document.getElementById(kind + '-path').dispatchEvent(new Event('change'));
        }
        await new Promise(resolve => setTimeout(resolve, 200));
        current.paths = await window.dashboard.getLogPaths();
        return current;
      })()`);
      if (logs.heading !== '日志' || logs.cards !== 2 || !logs.commandHidden || logs.paths.kernel !== paths.kernel || logs.paths.logcat !== paths.logcat) throw new Error(`Log workspace failed: ${JSON.stringify(logs)}`);
      await win.webContents.executeJavaScript(`(() => {
        document.getElementById('kernel-path').value = ${JSON.stringify('C:\\Logs\\kernel.log')};
        document.getElementById('logcat-path').value = ${JSON.stringify('C:\\Logs\\logcat.log')};
        document.getElementById('device-subtitle').textContent = '设备已连接';
        document.getElementById('toast').classList.remove('show');
      })()`);
      await new Promise((resolve) => setTimeout(resolve, 300));
      fs.writeFileSync(path.join(__dirname, '..', 'preview-logs.png'), (await win.capturePage()).toPNG());
      await win.webContents.executeJavaScript(`(() => {
        document.getElementById('kernel-path').value = ${JSON.stringify(paths.kernel)};
        document.getElementById('logcat-path').value = ${JSON.stringify(paths.logcat)};
      })()`);
      const captured = {};
      if (process.env.ADB_DASHBOARD_DEVICE_SMOKE === '1') {
        if (info.status !== '已连接') throw new Error('A connected device is required for log capture smoke');
        for (const kind of ['kernel', 'logcat']) {
          const result = await win.webContents.executeJavaScript(`(async () => {
            document.querySelector('.capture-log[data-kind="${kind}"]').click();
            for (let i = 0; i < 240; i++) {
              await new Promise(resolve => setTimeout(resolve, 500));
              const state = document.getElementById('output-state').textContent;
              if (state === '已完成' || state === '出错') return { state, saved: document.getElementById('saved-path').textContent };
            }
            return { state: '超时' };
          })()`);
          if (result.state !== '已完成' || !fs.existsSync(paths[kind])) throw new Error(`${kind} capture failed: ${JSON.stringify(result)}`);
          captured[kind] = fs.statSync(paths[kind]).size;
        }
      }
      console.log(JSON.stringify({ ...info, sidebar, compact, interactions, clock, logs, captured }));
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
