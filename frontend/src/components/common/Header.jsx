import React, { useState } from 'react';
import { Search, Bell, Sparkles } from 'lucide-react';
import api from '../../services/api';

const Header = ({ title, subtitle, onSearchResults }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const res = await api.get(`/search?q=${encodeURIComponent(searchQuery)}`);
      if (onSearchResults) {
        onSearchResults(res.data);
      }
    } catch (err) {
      console.error("Search error:", err);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <header className="px-8 py-5 flex items-center justify-between border-b border-slate-800/80 bg-slate-950/60 sticky top-0 backdrop-blur-md z-20">
      <div>
        <h2 className="text-2xl font-bold text-slate-100">{title}</h2>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      {/* Natural Language Search Bar */}
      <div className="flex items-center space-x-4">
        <form onSubmit={handleSearch} className="relative w-80">
          <input
            id="natural-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Try 'How much spent on food?' or 'above 1000'..."
            className="w-full pl-10 pr-10 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
          />
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-2.5" />
          <button type="submit" className="absolute right-3 top-2.5 text-indigo-400 hover:text-indigo-300">
            <Sparkles className={`w-4 h-4 ${isSearching ? 'animate-spin' : ''}`} />
          </button>
        </form>

        <button
          id="notifications-btn"
          className="p-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 hover:text-slate-200 transition-colors relative"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-indigo-500"></span>
        </button>
      </div>
    </header>
  );
};

export default Header;
