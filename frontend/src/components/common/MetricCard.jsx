import React from 'react';

const MetricCard = ({ title, value, change, icon: Icon, color = 'indigo' }) => {
  const colorStyles = {
    indigo: 'from-indigo-500/10 to-indigo-600/5 border-indigo-500/20 text-indigo-400',
    purple: 'from-purple-500/10 to-purple-600/5 border-purple-500/20 text-purple-400',
    emerald: 'from-emerald-500/10 to-emerald-600/5 border-emerald-500/20 text-emerald-400',
    rose: 'from-rose-500/10 to-rose-600/5 border-rose-500/20 text-rose-400',
    amber: 'from-amber-500/10 to-amber-600/5 border-amber-500/20 text-amber-400',
  };

  return (
    <div className={`p-5 rounded-2xl bg-gradient-to-br border ${colorStyles[color]} backdrop-blur-md transition-all duration-300 hover:scale-[1.02]`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-400 tracking-wide uppercase">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-xl bg-slate-900/60 border border-slate-800 ${colorStyles[color].split(' ')[3]}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="mt-3">
        <h3 className="text-2xl font-bold text-slate-100 tracking-tight">{value}</h3>
        {change && (
          <p className="text-xs text-slate-400 mt-1 font-medium">
            {change}
          </p>
        )}
      </div>
    </div>
  );
};

export default MetricCard;
