// data-pipeline/convert.js
import path from 'path';
import fs from 'fs-extra';
import csvParser from 'csv-parser';
import { createReadStream } from 'fs';

const symbols = ['xauusd', 'gbpusd', 'gbpjpy', 'usdjpy', 'eurusd', 'eurjpy', 'usa30idxusd', 'dollaridxusd', 'audjpy', 'nzdusd', 'nzdjpy'];
const MERGED_DIR = path.join(process.cwd(), '..', 'data', 'merged');
const PARQUET_DIR = path.join(process.cwd(), '..', 'data', 'parquet');

function parseRowValue(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

async function readMergedCsv(mergedFile) {
  const rows = [];
  return new Promise((resolve, reject) => {
    createReadStream(mergedFile)
      .pipe(csvParser())
      .on('data', (row) => {
        const time = row.Time || row.time;
        rows.push({
          timestamp: time,
          open: parseRowValue(row.Open || row.open),
          high: parseRowValue(row.High || row.high),
          low: parseRowValue(row.Low || row.low),
          close: parseRowValue(row.Close || row.close),
          volume: parseRowValue(row.Volume || row.volume)
        });
      })
      .on('end', () => resolve(rows))
      .on('error', reject);
  });
}

async function main() {
  await fs.ensureDir(PARQUET_DIR);
  const { ParquetSchema, ParquetWriter } = await import('parquets');

  for (const symbol of symbols) {
    const mergedFile = path.join(MERGED_DIR, `${symbol}_m5.csv`);
    const parquetFile = path.join(PARQUET_DIR, `${symbol}_m5.parquet`);

    if (!(await fs.pathExists(mergedFile))) continue;

    console.log(`[Converting] ${symbol}...`);
    const rows = await readMergedCsv(mergedFile);
    if (rows.length === 0) continue;

    const schema = new ParquetSchema({
      timestamp: { type: 'UTF8' },
      open: { type: 'DOUBLE' }, high: { type: 'DOUBLE' },
      low: { type: 'DOUBLE' }, close: { type: 'DOUBLE' },
      volume: { type: 'DOUBLE', optional: true }
    });

    const writer = await ParquetWriter.openFile(schema, parquetFile);
    for (const record of rows) await writer.appendRow(record);
    await writer.close();
    console.log(`  -> Saved Parquet: ${parquetFile}`);
  }
  console.log("Conversion complete!");
}
main();
