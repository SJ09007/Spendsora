import React, { useEffect, useState } from 'react';
import { 
  DollarSign, 
  Calendar, 
  TrendingUp, 
  Sparkles, 
  Plus, 
  ArrowUpRight, 
  Receipt, 
  Tag, 
  Clock,
  Zap,
  TrendingDown
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import MetricCard from '../components/common/MetricCard';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Dashboard = ({ onOpenQuickLog, searchResult }) => {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);
  const [recentExpenses, setRecentExpenses] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const [sumRes, chartRes, expRes, insRes] = await Promise.all([
        api.get('/analytics/summary'),
        api.get('/analytics/charts'),
        api.get('/expenses?limit=6'),
        api.get('/insights')
      ]);
      setSummary(sumRes.data);
      setCharts(chartRes.data);
      setRecentExpenses(expRes.data);
      setInsights(insRes.data);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const currencySymbol = user?.currency || '₹';

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-indigo-400">
          <Sparkles className="w-6 h-6 animate-spin" />
          <span className="text-sm font-medium">Loading Financial Overview...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Search Result Overlay if Header Natural Search triggered */}
      {searchResult && (
        <div className="p-5 rounded-2xl bg-indigo-950/60 border border-indigo-500/30 space-y-3">
          <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-sm">
            <Sparkles className="w-5 h-5" />
            <span>Natural Search Answer:</span>
          </div>
          <p className="text-base text-slate-100 font-medium">{searchResult.answer}</p>
        </div>
      )}

      {/* AI Insights Bar */}
      {insights.length > 0 && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-indigo-900/40 via-purple-900/40 to-slate-900 border border-indigo-500/20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-indigo-500/20 text-indigo-400">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider">AI Insight</span>
              <p className="text-sm font-medium text-slate-200">{insights[0].content}</p>
            </div>
          </div>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <MetricCard
          title="Total Spending"
          value={`${currencySymbol}${summary?.total_spending?.toLocaleString() || '0'}`}
          change={`${summary?.total_transactions || 0} total transactions`}
          icon={DollarSign}
          color="indigo"
        />
        <MetricCard
          title="Today's Spending"
          value={`${currencySymbol}${summary?.today_spending?.toLocaleString() || '0'}`}
          change="Updated live via Telegram"
          icon={Calendar}
          color="purple"
        />
        <MetricCard
          title="Monthly Spending"
          value={`${currencySymbol}${summary?.monthly_spending?.toLocaleString() || '0'}`}
          change={`Top: ${summary?.top_category || 'N/A'}`}
          icon={TrendingUp}
          color="emerald"
        />
        <MetricCard
          title="Daily Average"
          value={`${currencySymbol}${summary?.avg_per_day?.toLocaleString() || '0'}`}
          change={`Avg/Txn: ${currencySymbol}${summary?.avg_per_transaction || 0}`}
          icon={Sparkles}
          color="amber"
        />
      </div>

      {/* Main Charts & Breakdown Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spending Trend Line Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-100">30-Day Spending Trend</h3>
              <p className="text-xs text-slate-400">Daily spending activity line visualization</p>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts?.daily_trend || []}>
                <defs>
                  <linearGradient id="spendingGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                  formatter={(val) => [`${currencySymbol}${val}`, 'Amount']}
                />
                <Area type="monotone" dataKey="amount" stroke="#6366f1" strokeWidth={2.5} fillOpacity={1} fill="url(#spendingGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Pie Chart */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-100">Category Share</h3>
            <p className="text-xs text-slate-400">Expenses grouped by category</p>
          </div>

          <div className="h-48 w-full my-4 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={charts?.categories || []}
                  dataKey="total_amount"
                  nameKey="category_name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                >
                  {(charts?.categories || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || '#6366f1'} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                  formatter={(val) => [`${currencySymbol}${val}`, 'Spent']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2">
            {(charts?.categories || []).slice(0, 4).map((cat) => (
              <div key={cat.category_name} className="flex items-center justify-between text-xs">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cat.color }}></span>
                  <span className="text-slate-300 font-medium">{cat.category_name}</span>
                </div>
                <span className="text-slate-400">{cat.percentage}% ({currencySymbol}{cat.total_amount})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Expenses List */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-100">Recent Transactions</h3>
            <p className="text-xs text-slate-400">Logged via Telegram bot & web app</p>
          </div>
          <button
            onClick={onOpenQuickLog}
            className="py-2 px-3 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 rounded-xl text-xs font-semibold flex items-center space-x-1.5 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Expense</span>
          </button>
        </div>

        <div className="divide-y divide-slate-800/60">
          {recentExpenses.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">
              No transactions logged yet. Try sending <code>80 chai</code> to your Telegram bot or click Quick Log!
            </div>
          ) : (
            recentExpenses.map((exp) => (
              <div key={exp.id} className="py-3.5 flex items-center justify-between hover:bg-slate-800/30 px-3 rounded-xl transition-colors">
                <div className="flex items-center space-x-3.5">
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-md text-sm"
                    style={{ backgroundColor: exp.category?.color || '#6366f1' }}
                  >
                    {exp.category?.name?.charAt(0) || 'E'}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-100">{exp.description}</p>
                    <div className="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
                      <span>{exp.category?.name || 'Uncategorized'}</span>
                      <span>•</span>
                      <span>{new Date(exp.date).toLocaleDateString()}</span>
                      <span>•</span>
                      <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 uppercase text-[9px]">
                        {exp.payment_mode}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-base font-bold text-slate-100">
                    -{currencySymbol}{floatVal(exp.amount).toFixed(2)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const floatVal = (val) => (typeof val === 'number' ? val : parseFloat(val) || 0);

export default Dashboard;
