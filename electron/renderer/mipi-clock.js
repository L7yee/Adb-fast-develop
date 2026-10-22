function calculateMipiClock(input) {
  const fields = {
    width: '宽度', height: '高度', fps: '目标 FPS', lanes: 'Lane 数', sourceMHz: 'DPI 时钟源',
    hfp: 'HFP', hbp: 'HBP', hsync: 'HSYNC', vfp: 'VFP', vbp: 'VBP', vsync: 'VSYNC'
  };
  const values = {};
  for (const [key, label] of Object.entries(fields)) {
    if (input[key] === '' || input[key] == null) throw new Error(`请输入${label}`);
    const value = Number(input[key]);
    const positive = ['width', 'height', 'fps', 'lanes', 'sourceMHz'].includes(key);
    const integer = !['fps', 'sourceMHz'].includes(key);
    if (!Number.isFinite(value) || (positive ? value <= 0 : value < 0) || (integer && !Number.isInteger(value))) {
      throw new Error(`${label}数值无效`);
    }
    values[key] = value;
  }

  const horizontalTotal = values.width + values.hfp + values.hbp + values.hsync;
  const verticalTotal = values.height + values.vfp + values.vbp + values.vsync;
  const neededDpiHz = horizontalTotal * verticalTotal * values.fps;
  const sourceHz = values.sourceMHz * 1000000;
  if (!Number.isFinite(neededDpiHz) || !Number.isFinite(sourceHz)) throw new Error('计算结果超出范围');

  const baseDivider = Math.floor(sourceHz / neededDpiHz);
  const remainder = sourceHz - baseDivider * neededDpiHz;
  const divider = neededDpiHz / 2 > remainder ? baseDivider : baseDivider + 1;
  if (divider < 1) throw new Error('DPI 时钟源过低，无法得到有效分频值');

  const actualFps = sourceHz / divider / horizontalTotal / verticalTotal;
  const mipiClockHz = sourceHz / divider * 3 * 8 / 0.9 / values.lanes;
  if (!Number.isFinite(mipiClockHz)) throw new Error('计算结果超出范围');
  return {
    horizontalTotal, verticalTotal, neededDpiHz, divider,
    actualFps, actualFpsInteger: Math.floor(actualFps),
    mipiClockHz, mipiClockMHzInteger: Math.floor(mipiClockHz / 1000000)
  };
}

if (typeof module !== 'undefined') module.exports = { calculateMipiClock };
