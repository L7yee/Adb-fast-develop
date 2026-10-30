const { execFileSync } = require('node:child_process');
const path = require('node:path');

const root = path.resolve(__dirname, '..', '..');
const repository = 'https://github.com/L7yee/Adb-fast-develop';
function git(...args) {
  return execFileSync('git', ['-C', root, ...args], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
}
function cell(value) { return String(value).replace(/\|/g, '\\|').replace(/[\r\n]/g, ' '); }

try {
  const rows = git('log', '--decorate=short', '--format=%H%x00%cs%x00%s%x00%D').split('\n');
  console.log('# Commit 与应用版本记录\n');
  console.log('版本取自每个 commit 内的 package.json；文档提交也会列出。同一版本可以包含多个 commit。\n');
  console.log('| Commit | 日期 | 应用版本 | 发布标签 | 修改 |');
  console.log('| --- | --- | --- | --- | --- |');
  for (const row of rows) {
    const [sha, date, subject, decorations = ''] = row.split('\0');
    const files = git('ls-tree', '-r', '--name-only', sha, '--', 'electron/package.json', 'package.json').split('\n');
    // The first Electron commit kept package.json at the repository root.
    const file = files.includes('electron/package.json') ? 'electron/package.json' : files.includes('package.json') ? 'package.json' : null;
    const version = file ? JSON.parse(git('show', `${sha}:${file}`)).version : '—';
    const tags = [...decorations.matchAll(/(?:^|, )tag: ([^,]+)/g)].map((match) => match[1]).join(', ') || '—';
    console.log(`| [${sha.slice(0, 7)}](${repository}/commit/${sha}) | ${date} | ${cell(version)} | ${cell(tags)} | ${cell(subject)} |`);
  }
} catch (error) {
  console.error(`无法读取版本记录：${error.message}`);
  process.exitCode = 1;
}
