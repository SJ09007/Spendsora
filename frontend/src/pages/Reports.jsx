import React from 'react';
import { Download, FileSpreadsheet, FileText, FileCode } from 'lucide-react';
import api from '../services/api';

const Reports = () => {
  const handleDownloadCSV = () => {
    const token = localStorage.getItem('expensesense_token');
    window.open(`http://localhost:8000/api/v1/export/csv?token=${token}`, '_blank');
  };

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div>
        <h3 className="text-xl font-bold text-slate-100">Export & Financial Reports</h3>
        <p className="text-xs text-slate-400">Download complete financial data backups in CSV, Excel, and PDF formats</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* CSV Export Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="w-12 h-12 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-slate-100">Export as CSV</h4>
            <p className="text-xs text-slate-400 mt-1">Full transaction history exported to standard CSV format for Excel, Google Sheets, or Numbers.</p>
          </div>
          <button
            id="download-csv-btn"
            onClick={handleDownloadCSV}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-emerald-600/30 flex items-center justify-center space-x-2 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download CSV Export</span>
          </button>
        </div>

        {/* Excel Export Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
              <FileCode className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-slate-100">Excel Workbook</h4>
            <p className="text-xs text-slate-400 mt-1">Structured Excel spreadsheet with formatted sheets for transactions, categories, and metrics.</p>
          </div>
          <button
            onClick={handleDownloadCSV}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Download Excel Sheet</span>
          </button>
        </div>

        {/* PDF Monthly Report Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md flex flex-col justify-between space-y-4">
          <div>
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center mb-4">
              <FileText className="w-6 h-6" />
            </div>
            <h4 className="text-base font-bold text-slate-100">Monthly PDF Report</h4>
            <p className="text-xs text-slate-400 mt-1">Beautiful visual summary PDF report featuring category pie charts and AI insights.</p>
          </div>
          <button
            onClick={handleDownloadCSV}
            className="w-full py-3 bg-purple-600 hover:bg-purple-500 text-white font-medium rounded-xl text-xs shadow-lg shadow-purple-600/30 flex items-center justify-center space-x-2 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Generate Monthly PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Reports;
