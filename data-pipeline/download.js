// data-pipeline/download.js
import fs from 'fs';
import path from 'path';
import { getHistoricalRates } from 'dukascopy-node';

const symbols = [
    'xauusd', 'gbpusd', 'gbpjpy', 'usdjpy', 
    'eurusd', 'eurjpy', 'usa30idxusd', 'dollaridxusd', 
    'audjpy', 'nzdusd', 'nzdjpy'
];

const DATA_DIR = path.join(process.cwd(), '..', 'data');

if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

async function downloadYear(symbol, year) {
    const from = new Date(Date.UTC(year, 0, 1));
    const to = new Date(Date.UTC(year + 1, 0, 1));
    const filePath = path.join(DATA_DIR, `${symbol}_${year}.csv`);
    
    if (fs.existsSync(filePath) && fs.statSync(filePath).size > 100) {
        console.log(`[Cache] ${symbol} ${year} already downloaded.`);
        return;
    }

    console.log(`[Downloading] ${symbol} ${year}...`);
    try {
        const csvData = await getHistoricalRates({
            instrument: symbol, timeframe: 'm5', priceType: 'ask', volumes: true,
            dates: { from, to }, format: 'csv', batchSize: 6, pauseBetweenBatchesMs: 500, useCache: false
        });
        
        if (csvData && csvData.length > 100) {
            fs.writeFileSync(filePath, csvData, 'utf8');
            console.log(`[Success] Saved ${symbol} ${year}.csv`);
        }
    } catch (error) {
        console.error(`[Error] Failed ${symbol} ${year}: ${error.message}`);
    }
}

async function main() {
    for (const symbol of symbols) {
        for (let year = 2005; year <= 2024; year++) {
            await downloadYear(symbol, year);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
    console.log("All downloads complete!");
}
main();
