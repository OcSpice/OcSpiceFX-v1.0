// frontend/src/App.jsx
import { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export default function App() {
  const [config, setConfig] = useState({
    symbol: 'gbpusd',
    start_date: '2022-01-01',
    end_date: '2024-01-01',
    account_size: 10000,
    risk_per_trade_pct: 0.01,
    broker_type: 'prop_firm',
    spread_pips: 0.4,
    slippage_pips: 0.2,
    commission_per_lot: 7.0,
    profit_target_pct: 0.10,
    max_daily_dd_pct: 0.05,
    max_total_dd_pct: 0.10,
    min_trading_days: 3,
    leverage: 2000,
    margin_call_pct: 0.60,
    stop_out_pct: 0.30
  });

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setConfig(prev => ({ ...prev, [name]: type === 'number' ? parseFloat(value) : value }));
  };

  const runBacktest = async () => {
    setLoading(true);
    setResults(null);
    try {
      const res = await axios.post(`${API_URL}/backtest`, config);
      setResults(res.data);
    } catch (err) {
      console.error("Backtest failed", err.response?.data?.detail || err.message);
      alert("Backtest failed: " + (err.response?.data?.detail || err.message));
    }
    setLoading(false);
  };

  // Helper to format Dukascopy symbol (e.g., gbpusd -> GBP/USD)
  const formatDukasSymbol = (sym) => {
    if (sym.includes('usd') && sym.includes('jpy')) return 'USD/JPY';
    if (sym === 'xauusd') return 'XAU/USD';
    if (sym === 'usa30idxusd') return 'USA30.IDX/USD';
    if (sym === 'dollaridxusd') return 'DXY';
    return `${sym.slice(0,3).toUpperCase()}/${sym.slice(3,6).toUpperCase()}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <h1 className="text-4xl font-bold mb-8 text-purple-400">OcSpiceFX Strategy Lab</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Config & Widgets */}
        <div className="lg:col-span-1 space-y-6">
          
          {/* Backtest Config */}
          <div className="bg-gray-800 p-6 rounded-xl shadow-lg">
            <h2 className="text-2xl font-bold mb-4 border-b border-gray-700 pb-2">Backtest Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Asset</label>
                <select name="symbol" value={config.symbol} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded">
                  <option value="xauusd">XAUUSD (Gold)</option>
                  <option value="gbpusd">GBPUSD</option>
                  <option value="gbpjpy">GBPJPY</option>
                  <option value="usdjpy">USDJPY</option>
                  <option value="eurusd">EURUSD</option>
                  <option value="eurjpy">EURJPY</option>
                  <option value="usa30idxusd">US30</option>
                  <option value="dollaridxusd">DXY</option>
                  <option value="audjpy">AUDJPY</option>
                  <option value="nzdusd">NZDUSD</option>
                  <option value="nzdjpy">NZDJPY</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Start Date</label>
                  <input type="date" name="start_date" value={config.start_date} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">End Date</label>
                  <input type="date" name="end_date" value={config.end_date} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Account Size ($)</label>
                  <input type="number" name="account_size" value={config.account_size} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Risk per Trade (%)</label>
                  <input type="number" step="0.005" name="risk_per_trade_pct" value={config.risk_per_trade_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Broker Type</label>
                <select name="broker_type" value={config.broker_type} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded">
                  <option value="prop_firm">Prop Firm (FundedNext/FundingPips)</option>
                  <option value="standard">Standard Broker (Exness/Deriv)</option>
                </select>
              </div>

              {config.broker_type === 'prop_firm' ? (
                <div className="space-y-4 border-l-2 border-purple-500 pl-4 mt-4">
                  <h3 className="font-bold text-purple-300">Prop Firm Rules</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm mb-1">Profit Target (%)</label>
                      <input type="number" step="0.01" name="profit_target_pct" value={config.profit_target_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Max Daily DD (%)</label>
                      <input type="number" step="0.01" name="max_daily_dd_pct" value={config.max_daily_dd_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Max Total DD (%)</label>
                      <input type="number" step="0.01" name="max_total_dd_pct" value={config.max_total_dd_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Min Trading Days</label>
                      <input type="number" name="min_trading_days" value={config.min_trading_days} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4 border-l-2 border-blue-500 pl-4 mt-4">
                  <h3 className="font-bold text-blue-300">Standard Broker Rules</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm mb-1">Leverage (1:x)</label>
                      <input type="number" name="leverage" value={config.leverage} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Margin Call (%)</label>
                      <input type="number" step="0.1" name="margin_call_pct" value={config.margin_call_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                    <div>
                      <label className="block text-sm mb-1">Stop Out (%)</label>
                      <input type="number" step="0.1" name="stop_out_pct" value={config.stop_out_pct} onChange={handleChange} className="w-full bg-gray-700 p-2 rounded" />
                    </div>
                  </div>
                </div>
              )}

              <button 
                onClick={runBacktest} 
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 rounded-lg transition-colors mt-4 disabled:opacity-50"
              >
                {loading ? 'Running Backtest...' : 'Run Simulation'}
              </button>
            </div>
          </div>

          {/* Dukascopy Economic Calendar Widget */}
          <div className="bg-gray-800 p-2 rounded-xl shadow-lg overflow-hidden">
             <div dangerouslySetInnerHTML={{ __html: `<script>(() => { const s = document.createElement('script'); s.src='https://widgets.dukascopy.com/embed/embed.js'; s.async=true; s.type='text/javascript'; s.innerHTML=JSON.stringify({type:"economic-calendar",theme:"dark",border:true,lang:"en"}); document.body.appendChild(s); })();</script>` }} />
          </div>

        </div>

        {/* Right Column: Results & Charts */}
        <div className="lg:col-span-2 space-y-6">
          
          {results && (
            <>
              {/* Status Card */}
              <div className={`p-6 rounded-xl shadow-lg ${results.status === 'Passed' ? 'bg-green-800' : results.status === 'Failed' || results.status === 'Blown' ? 'bg-red-800' : 'bg-gray-800'}`}>
                <h2 className="text-3xl font-bold mb-2">Simulation Status: {results.status}</h2>
                {results.fail_reason && <p className="text-lg text-gray-300">{results.fail_reason}</p>}
                <p className="text-2xl mt-4">Final Balance: ${results.final_balance.toFixed(2)}</p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <MetricCard title="Net P/L" value={`$${results.metrics.net_pnl.toFixed(2)}`} />
                <MetricCard title="Profit Factor" value={results.metrics.profit_factor.toFixed(2)} />
                <MetricCard title="Win Rate" value={results.metrics.win_rate} />
                <MetricCard title="Max Drawdown" value={`${results.metrics.max_drawdown.toFixed(2)}%`} />
              </div>

              {/* Dukascopy Chart Widget */}
              <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
                <h3 className="text-xl font-bold mb-4">Live Chart</h3>
                <div dangerouslySetInnerHTML={{ __html: `<script>(() => { const s = document.createElement('script'); s.src='https://widgets.dukascopy.com/embed/embed.js'; s.async=true; s.type='text/javascript'; s.innerHTML=JSON.stringify({type:"chart",theme:"dark",lang:"en",params:{instrument:"${formatDukasSymbol(config.symbol)}",interval:"15m",series:"CANDLES",offer:"BID"}}); document.body.appendChild(s); })();</script>` }} />
              </div>
            </>
          )}
          
          {!results && !loading && (
            <div className="flex items-center justify-center h-full bg-gray-800 rounded-xl border-2 border-dashed border-gray-700">
              <p className="text-gray-500 text-xl">Configure your backtest and click "Run Simulation"</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value }) {
  return (
    <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
      <p className="text-sm text-gray-400 mb-1">{title}</p>
      <p className="text-2xl font-bold text-white">{value}</p>
    </div>
  );
}
