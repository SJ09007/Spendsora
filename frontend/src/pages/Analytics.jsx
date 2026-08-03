import React, { useEffect, useState } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from 'recharts';
import { PieChart as PieIcon, Award, CreditCard, Sparkles, TrendingUp, Compass } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Analytics = () => {
  const { user } = useAuth();
  const [charts, setCharts] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cRes, sRes] = await Promise.all([
          api.get('/analytics/charts'),
          api.get('/analytics/summary')
        ]);
        setCharts(cRes.data);
        setSummary(sRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const currencySymbol = user?.currency || '₹';

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center space-x-3 text-indigo-400">
          <Sparkles className="w-6 h-6 animate-spin" />
          <span className="text-sm font-medium">Generating Analytics Hub...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Merchants & Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Top Merchants Ranking */}
        <div className="md:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center space-x-2 text-indigo-400 mb-4">
            <Award className="w-5 h-5" />
            <h3 className="text-lg font-bold text-slate-100">Top Vendors & Merchants</h3>
          </div>

          <div className="space-y-4">
            {(charts?.top_merchants || []).map((m, idx) => (
              <div key={m.merchant} className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800/80">
                <div className="flex items-center space-x-3">
                  <span className="w-7 h-7 rounded-lg bg-indigo-500/10 text-indigo-400 font-bold flex items-center justify-center text-xs">
                    #{idx + 1}
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-200">{m.merchant}</p>
                    <p className="text-[11px] text-slate-400">{m.count} transactions</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-slate-100">
                  {currencySymbol}{m.amount.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Modes Analysis */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center space-x-2 text-purple-400 mb-4">
            <CreditCard className="w-5 h-5" />
            <h3 className="text-lg font-bold text-slate-100">Payment Modes</h3>
          </div>

          <div className="space-y-4">
            {(charts?.payment_modes || []).map((pm) => (
              <div key={pm.mode} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">{pm.mode}</span>
                  <p className="text-[10px] text-slate-500">{pm.count} expenses</p>
                </div>
                <span className="text-sm font-bold text-slate-100">
                  {currencySymbol}{pm.amount.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Bar Chart Visualization */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center space-x-2 text-indigo-400 mb-6">
          <PieIcon className="w-5 h-5" />
          <h3 className="text-lg font-bold text-slate-100">Category Spending Comparison</h3>
        </div>

        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={charts?.categories || []}>
              <XAxis dataKey="category_name" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                formatter={(val) => [`${currencySymbol}${val}`, 'Total Spent']}
              />
              <Bar dataKey="total_amount" radius={[8, 8, 0, 0]}>
                {(charts?.categories || []).map((entry, index) => (
                  <Cell key={`bar-${index}`} fill={entry.color || '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
