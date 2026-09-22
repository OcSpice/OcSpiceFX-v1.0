import fs from 'fs-extra';
import path from 'path';
import { instruments } from './instruments.js';

const DATA_DIR = path.join(process.cwd(), '..', 'data');
const RAW_DIR = path.join(DATA_DIR, 'raw');
const MERGED_DIR = path.join(DATA_DIR, 'merged');
fs.ensureDirSync(MERGED_DIR);

for (const instrument of instruments) {
  const files = (await fs.readdir(RAW_DIR))
    .filter(file => file.startsWith(`${instrument.symbol}_`) && file.endsWith('.csv'))
    .sort();

  if (files.length === 0) {
    console.log(`[Skip] No raw files for ${instrument.projectSymbol}`);
    continue;
  }

  const merged = [];
  for (const [index, file] of files.entries()) {
    const text = (await fs.readFile(path.join(RAW_DIR, file), 'utf8')).trim();
    if (!text) continue;
    const lines = text.split(/\r?\n/);
    if (index === 0) merged.push(...lines);
    else merged.push(...lines.slice(1));
  }

  const output = path.join(MERGED_DIR, `${instrument.projectSymbol}_m5.csv`);
  await fs.writeFile(output, merged.join('\n') + '\n');
  console.log(`[Merged] ${instrument.projectSymbol}: ${files.length} yearly files -> ${output}`);
}
