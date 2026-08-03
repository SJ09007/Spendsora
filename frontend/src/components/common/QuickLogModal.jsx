import React, { useState } from 'react';
import { X, Sparkles, AlertCircle } from 'lucide-react';
import api from '../../services/api';

const QuickLogModal = ({ isOpen, onClose, onSuccess }) => {
  const [naturalInput, setNaturalInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!naturalInput.trim()) return;
    setLoading(true);
    setError('');

    try {
      await api.post('/expenses/parse', { text: naturalInput });
      setNaturalInput('');
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to log expense. Try format like "80 chai"');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1 text-slate-400 hover:text-slate-200 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 text-indigo-400 mb-2">
          <Sparkles className="w-5 h-5" />
          <h3 className="text-lg font-bold text-slate-100">AI Natural Language Expense Log</h3>
        </div>

        <p className="text-xs text-slate-400 mb-4">
          Type naturally like in Telegram. ExpenseSense AI will automatically detect amount, merchant, and category!
        </p>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Expense Expression
            </label>
            <input
              id="quick-log-input"
              type="text"
              value={naturalInput}
              onChange={(e) => setNaturalInput(e.target.value)}
              placeholder="e.g. 80 chai, 350 petrol, 1200 Amazon, 499 Netflix"
              className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              autoFocus
            />
          </div>

          <div className="flex items-center space-x-2 text-[11px] text-slate-500">
            <span>Examples:</span>
            <button
              type="button"
              onClick={() => setNaturalInput("80 chai")}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              80 chai
            </button>
            <button
              type="button"
              onClick={() => setNaturalInput("350 petrol via UPI")}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              350 petrol
            </button>
            <button
              type="button"
              onClick={() => setNaturalInput("1200 Amazon")}
              className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              1200 Amazon
            </button>
          </div>

          <button
            id="submit-quick-log"
            type="submit"
            disabled={loading || !naturalInput.trim()}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all"
          >
            {loading ? (
              <Sparkles className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                <span>Log Expense Instantly</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default QuickLogModal;
