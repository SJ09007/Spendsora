import React from 'react';
import { Send, User, Shield, Moon, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Settings = ({ onOpenTelegram }) => {
  const { user } = useAuth();

  return (
    <div className="p-8 space-y-6 max-w-4xl mx-auto">
      <div>
        <h3 className="text-xl font-bold text-slate-100">Account & Application Settings</h3>
        <p className="text-xs text-slate-400">Manage user profile, preferred currency, and Telegram integration</p>
      </div>

      <div className="space-y-6">
        {/* User Profile Info */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md space-y-4">
          <div className="flex items-center space-x-3 text-indigo-400">
            <User className="w-5 h-5" />
            <h4 className="text-base font-bold text-slate-100">Profile Details</h4>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Full Name</label>
              <input
                type="text"
                disabled
                value={user?.full_name || 'N/A'}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300"
              />
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Email Address</label>
              <input
                type="text"
                disabled
                value={user?.email || ''}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300"
              />
            </div>
          </div>
        </div>

        {/* Telegram Integration Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl bg-sky-500/20 text-sky-400 flex items-center justify-center">
              <Send className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base font-bold text-slate-100">Telegram Expense Tracker Bot</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                {user?.telegram_id ? `Linked to Telegram ID: ${user.telegram_id}` : 'Connect your Telegram account to log expenses via chat'}
              </p>
            </div>
          </div>

          <button
            onClick={onOpenTelegram}
            className="py-2.5 px-4 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-sky-600/30 transition-all"
          >
            {user?.telegram_id ? 'Re-link Telegram' : 'Connect Telegram'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
