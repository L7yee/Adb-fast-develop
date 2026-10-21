const fs = require('node:fs');
const path = require('node:path');
const YAML = require('yaml');

const CATEGORIES = new Set(['read', 'streaming', 'action']);

function normalizeCommand(value) {
  if (!value || typeof value !== 'object') throw new Error('命令数据无效');
  const id = String(value.id || '').trim();
  const label = String(value.label || '').trim();
  const shell_command = String(value.shell_command || '').trim();
  if (!/^[a-zA-Z0-9_-]+$/.test(id)) throw new Error('命令 ID 只能包含字母、数字、下划线和连字符');
  if (!label || !shell_command) throw new Error('名称和 ADB 命令不能为空');
  const category = CATEGORIES.has(value.category) ? value.category : 'read';
  return {
    id, label, shell_command, category,
    auto_refresh_capable: category === 'read' && Boolean(value.auto_refresh_capable),
    requires_root: Boolean(value.requires_root)
  };
}

class CommandStore {
  constructor(userData, bundledPath) {
    this.path = path.join(userData, 'commands.yaml');
    fs.mkdirSync(userData, { recursive: true });
    if (!fs.existsSync(this.path)) fs.copyFileSync(bundledPath, this.path);
  }

  read() {
    const data = YAML.parse(fs.readFileSync(this.path, 'utf8')) || {};
    const seen = new Set();
    return (Array.isArray(data.commands) ? data.commands : []).flatMap((raw) => {
      try {
        const command = normalizeCommand(raw);
        if (seen.has(command.id)) return [];
        seen.add(command.id);
        return [command];
      } catch {
        return [];
      }
    });
  }

  write(commands) {
    const next = commands.map(normalizeCommand);
    if (new Set(next.map((item) => item.id)).size !== next.length) throw new Error('命令 ID 不能重复');
    const tmp = `${this.path}.tmp`;
    fs.writeFileSync(tmp, YAML.stringify({ commands: next }), 'utf8');
    fs.renameSync(tmp, this.path);
    return next;
  }

  save(value, previousId) {
    const command = normalizeCommand(value);
    const commands = this.read();
    const index = commands.findIndex((item) => item.id === (previousId || command.id));
    if (commands.some((item, i) => item.id === command.id && i !== index)) throw new Error('命令 ID 已存在');
    if (index < 0) commands.push(command);
    else commands[index] = command;
    return this.write(commands);
  }

  delete(id) {
    return this.write(this.read().filter((item) => item.id !== id));
  }

  reorder(ids) {
    const commands = this.read();
    if (ids.length !== commands.length || new Set(ids).size !== ids.length) throw new Error('排序数据无效');
    const byId = new Map(commands.map((item) => [item.id, item]));
    if (ids.some((id) => !byId.has(id))) throw new Error('排序数据无效');
    return this.write(ids.map((id) => byId.get(id)));
  }
}

module.exports = { CommandStore, normalizeCommand };
