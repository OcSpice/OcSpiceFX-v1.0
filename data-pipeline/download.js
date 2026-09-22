import fs from 'fs';
import path from 'path';
import { getHistoricalRates } from 'dukascopy-node';
import { instruments, START_YEAR, END_YEAR } from './instruments.js';

const DATA_DIR = path.join(process.cwd(), '..', 'data', 'raw');
fs.mkdirSync(DATA_DIR, { recursive: true });

async function downloadYear(instrument, year) {
  const from = new Date(Date.UTC(year, 0, 1));
  const requestedTo = new Date(Date.UTC(year + 1, 0, 1));
  const to = requestedTo > new Date() ? new Date() : requestedTo;
  const filePath = path.join(DATA_DIR, `${instrument.symbol}_${year}.csv`);

  if (fs.existsSync(filePath) && fs.statSync(filePath).size > 100) {
    console.log(`[Cache] ${instrument.projectSymbol} ${year} already downloaded.`);
    return;
  }

  console.log(`[Downloading] ${instrument.projectSymbol} ${year} (${instrument.symbol})...`);
  try {
    const csvData = await getHistoricalRates({
      instrument: instrument.symbol,
      timeframe: 'm5',
      priceType: 'ask',
      volumes: true,
      dates: { from, to },
      format: 'csv',
      batchSize: 6,
      pauseBetweenBatchesMs: 500,
      useCache: false
    });

    if (csvData && csvData.length > 100) {
      fs.writeFileSync(filePath, csvData, 'utf8');
      console.log(`[Success] Saved ${filePath}`);
    } else {
      console.log(`[No data] ${instrument.projectSymbol} ${year}`);
    }
  } catch (error) {
    console.error(`[Error] Failed ${instrument.projectSymbol} ${year}: ${error.message}`);
  }
}

async function main() {
  console.log(`Downloading M5 historical data for ${instruments.length} instruments, ${START_YEAR}-${END_YEAR}...`);
  for (const instrument of instruments) {
    for (let year = START_YEAR; year <= END_YEAR; year++) {
      await downloadYear(instrument, year);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  console.log('Download stage complete.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
