import React, { useEffect, useState } from 'react';
import { Search, Filter, Trash2, Edit3, Plus, Calendar, Tag, ArrowUpDown } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const Expenses = ({ onOpenQuickLog }) => {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchExpenses = async () => {
    setLoading(true);
    try {
      let url = '/expenses?limit=100';
      if (selectedCategory) url += `&category_id=${selectedCategory}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;

      const [expRes, catRes] = await Promise.all([
        api.get(url),
        api.get('/categories')
      ]);
      setExpenses(expRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExpenses();
  }, [selectedCategory, search]);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this expense?")) return;
    try {
      await api.delete(`/expenses/${id}`);
      setExpenses(expenses.filter((e) => e.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const currencySymbol = user?.currency || '₹';

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Filters & Action Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex flex-1 items-center space-x-3 w-full md:w-auto">
          {/* Search Input */}
          <div className="relative flex-1 max-w-md">
            <input
              id="expense-search-input"
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter expenses by description or vendor..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          </div>

          {/* Category Dropdown */}
          <select
            id="category-filter-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <button
          id="add-expense-page-btn"
          onClick={onOpenQuickLog}
          className="py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center space-x-2 transition-all w-full md:w-auto justify-center"
        >
          <Plus className="w-4 h-4" />
          <span>Add Expense</span>
        </button>
      </div>

      {/* Expenses Table */}
      <div className="rounded-2xl bg-slate-900/70 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950/80 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider">
              <tr>
                <th className="py-4 px-6">Description</th>
                <th className="py-4 px-6">Category</th>
                <th className="py-4 px-6">Merchant</th>
                <th className="py-4 px-6">Date</th>
                <th className="py-4 px-6">Payment Mode</th>
                <th className="py-4 px-6">Amount</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan="7" className="py-8 text-center text-slate-500">
                    Loading expenses...
                  </td>
                </tr>
              ) : expenses.length === 0 ? (
                <tr>
                  <td colSpan="7" className="py-8 text-center text-slate-500">
                    No matching expenses found.
                  </td>
                </tr>
              ) : (
                expenses.map((exp) => (
                  <tr key={exp.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-4 px-6 font-semibold text-slate-100">
                      {exp.description}
                      {exp.raw_telegram_text && (
                        <p className="text-[10px] text-slate-500 font-normal italic">
                          "{exp.raw_telegram_text}"
                        </p>
                      )}
                    </td>
                    <td className="py-4 px-6">
                      <span 
                        className="px-2.5 py-1 rounded-full text-[11px] font-semibold text-white inline-block shadow-sm"
                        style={{ backgroundColor: exp.category?.color || '#6366f1' }}
                      >
                        {exp.category?.name || 'Other'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-400">{exp.merchant || '-'}</td>
                    <td className="py-4 px-6 text-slate-400">
                      {new Date(exp.date).toLocaleDateString()}
                    </td>
                    <td className="py-4 px-6">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
                        {exp.payment_mode}
                      </span>
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-100">
                      {currencySymbol}{parseFloat(exp.amount).toFixed(2)}
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      <button
                        onClick={() => handleDelete(exp.id)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Expenses;
