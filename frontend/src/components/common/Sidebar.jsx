import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Receipt, 
  PieChart, 
  Wallet, 
  Repeat, 
  FileText, 
  Settings, 
  Sparkles,
  LogOut,
  Send
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ onOpenTelegram, onOpenQuickLog }) => {
  const { user, logout } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Expenses', path: '/expenses', icon: Receipt },
    { name: 'Analytics', path: '/analytics', icon: PieChart },
    { name: 'Budgets', path: '/budgets', icon: Wallet },
    { name: 'Recurring', path: '/recurring', icon: Repeat },
    { name: 'Reports & Export', path: '/reports', icon: FileText },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 min-h-screen flex flex-col justify-between p-4 sticky top-0 h-screen z-30">
      <div>
        {/* Brand Header */}
        <div className="flex items-center space-x-3 px-3 py-4 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
              ExpenseSense AI
            </h1>
            <span className="text-xs text-indigo-400 font-medium">Smart Tracker</span>
          </div>
        </div>

        {/* Action Button: Quick Log */}
        <button
          id="quick-log-btn"
          onClick={onOpenQuickLog}
          className="w-full mb-6 py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all duration-200"
        >
          <Sparkles className="w-4 h-4" />
          <span>Quick Log Expense</span>
        </button>

        {/* Telegram Connect Card */}
        <div className="mb-6 p-3.5 rounded-xl bg-indigo-950/40 border border-indigo-800/40 flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center">
              <Send className="w-4 h-4" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-200">Telegram Bot</p>
              <p className="text-[10px] text-slate-400">
                {user?.telegram_id ? 'Connected' : 'Not Linked'}
              </p>
            </div>
          </div>
          <button
            id="telegram-link-btn"
            onClick={onOpenTelegram}
            className="text-xs font-medium text-sky-400 hover:text-sky-300 underline"
          >
            {user?.telegram_id ? 'Manage' : 'Link'}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                id={`nav-${item.name.toLowerCase().replace(/\s+/g, '-')}`}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20'
                      : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Info & Logout */}
      <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-3 truncate">
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-indigo-400">
            {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
          </div>
          <div className="truncate">
            <p className="text-sm font-medium text-slate-200 truncate">{user?.full_name || 'User'}</p>
            <p className="text-xs text-slate-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          id="logout-btn"
          onClick={logout}
          title="Logout"
          className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
