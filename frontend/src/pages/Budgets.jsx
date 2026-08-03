import React, { useEffect, useState } from 'react';
import { Wallet, Plus, AlertTriangle, CheckCircle, Trash2, Bell } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Budgets = () => {
  const { user } = useAuth();
  const [budgets, setBudgets] = useState([]);
  const [categories, setCategories] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [amountLimit, setAmountLimit] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchBudgets = async () => {
    try {
      const [bRes, cRes] = await Promise.all([
        api.get('/budgets'),
        api.get('/categories')
      ]);
      setBudgets(bRes.data);
      setCategories(cRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgets();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!selectedCategory || !amountLimit) return;
    try {
      await api.post('/budgets', {
        category_id: parseInt(selectedCategory),
        amount_limit: parseFloat(amountLimit),
        period: 'monthly'
      });
      setShowModal(false);
      setSelectedCategory('');
      setAmountLimit('');
      fetchBudgets();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to create budget");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this budget constraint?")) return;
    try {
      await api.delete(`/budgets/${id}`);
      setBudgets(budgets.filter((b) => b.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const currencySymbol = user?.currency || '₹';

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-slate-100">Monthly Category Budgets</h3>
          <p className="text-xs text-slate-400">Set limits and receive Telegram alerts at 80%, 90%, and 100% threshold</p>
        </div>
        <button
          id="create-budget-btn"
          onClick={() => setShowModal(true)}
          className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Category Budget</span>
        </button>
      </div>

      {/* Budget Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {budgets.map((b) => {
          const spent = b.spent || 0;
          const limit = b.amount_limit || 1;
          const pct = Math.min(Math.round((spent / limit) * 100), 100);
          
          let progressColor = 'bg-emerald-500';
          let textColor = 'text-emerald-400';
          if (pct >= 100) {
            progressColor = 'bg-rose-500';
            textColor = 'text-rose-400';
          } else if (pct >= 80) {
            progressColor = 'bg-amber-500';
            textColor = 'text-amber-400';
          }

          return (
            <div key={b.id} className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div 
                    className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white shadow-md text-sm"
                    style={{ backgroundColor: b.category?.color || '#6366f1' }}
                  >
                    {b.category?.name?.charAt(0) || 'B'}
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-100">{b.category?.name}</h4>
                    <p className="text-[11px] text-slate-400">Monthly Budget</p>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(b.id)}
                  className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div>
                <div className="flex items-center justify-between text-xs font-semibold mb-2">
                  <span className="text-slate-400">Spent: {currencySymbol}{spent.toFixed(2)}</span>
                  <span className={textColor}>{pct}% of {currencySymbol}{limit.toFixed(2)}</span>
                </div>
                {/* Progress Bar */}
                <div className="w-full h-3 rounded-full bg-slate-950 border border-slate-800 overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-500 ${progressColor}`}
                    style={{ width: `${pct}%` }}
                  ></div>
                </div>
              </div>

              {/* Alert Status Indicators */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <span className="flex items-center space-x-1">
                  <Bell className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Telegram Alerts:</span>
                </span>
                <div className="flex items-center space-x-1.5">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${b.alert_80_sent ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'}`}>80%</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${b.alert_90_sent ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'}`}>90%</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${b.alert_100_sent ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-800 text-slate-500'}`}>100%</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Modal for creating new budget */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-slate-100 mb-4">Create Category Budget</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  required
                >
                  <option value="">Select Category</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Monthly Limit ({currencySymbol})</label>
                <input
                  type="number"
                  step="0.01"
                  value={amountLimit}
                  onChange={(e) => setAmountLimit(e.target.value)}
                  placeholder="e.g. 5000"
                  className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>

              <div className="flex space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="w-1/2 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-xl text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-1/2 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-indigo-600/30"
                >
                  Save Budget
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;
