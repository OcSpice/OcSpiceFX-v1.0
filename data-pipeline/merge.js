// data-pipeline/merge.js
const fs = require("fs-extra");
const path = require("path");

const symbols = ['xauusd', 'gbpusd', 'gbpjpy', 'usdjpy', 'eurusd', 'eurjpy', 'usa30idxusd', 'dollaridxusd', 'audjpy', 'nzdusd', 'nzdjpy'];
const DATA_DIR = path.join(__dirname, '..', 'data');
const MERGED_DIR = path.join(DATA_DIR, 'merged');

fs.ensureDirSync(MERGED_DIR);

for (const symbol of symbols) {
    let merged = [];
    const files = fs.readdirSync(DATA_DIR)
                    .filter(f => f.startsWith(`${symbol}_`) && f.endsWith(".csv"))
                    .sort();

    if (files.length === 0) continue;

    files.forEach((file, index) => {
        const text = fs.readFileSync(path.join(DATA_DIR, file), "utf8").trim();
        const lines = text.split("\n");
        if (index === 0) merged.push(...lines);
        else merged.push(...lines.slice(1));
    });

    fs.writeFileSync(path.join(MERGED_DIR, `${symbol}_m5.csv`), merged.join("\n"));
    console.log(`${symbol} merged.`);
}
