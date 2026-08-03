import React, { useState } from 'react';
import { X, Send, Copy, Check, ShieldCheck } from 'lucide-react';
import api from '../../services/api';

const TelegramModal = ({ isOpen, onClose }) => {
  const [code, setCode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleGenerateCode = async () => {
    setLoading(true);
    try {
      const res = await api.post('/auth/generate-telegram-code');
      setCode(res.data.link_code);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyCode = () => {
    if (code) {
      navigator.clipboard.writeText(`/link ${code}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
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

        <div className="flex items-center space-x-3 text-sky-400 mb-4">
          <div className="w-10 h-10 rounded-xl bg-sky-500/20 flex items-center justify-center">
            <Send className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Link Telegram Account</h3>
            <p className="text-xs text-slate-400">Log expenses on the go directly in Telegram</p>
          </div>
        </div>

        <div className="space-y-4 text-xs text-slate-300">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <p className="font-semibold text-slate-200">How it works:</p>
            <ol className="list-decimal list-inside space-y-1 text-slate-400">
              <li>Click generate code below</li>
              <li>Open your Telegram app</li>
              <li>Send <code className="text-sky-400">/link &lt;code&gt;</code> to the bot</li>
            </ol>
          </div>

          {!code ? (
            <button
              id="generate-link-code-btn"
              onClick={handleGenerateCode}
              disabled={loading}
              className="w-full py-3 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-xl shadow-lg shadow-sky-600/30 flex items-center justify-center space-x-2"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{loading ? 'Generating Code...' : 'Generate 6-Digit Link Code'}</span>
            </button>
          ) : (
            <div className="space-y-3">
              <div className="p-4 rounded-xl bg-sky-950/40 border border-sky-800/40 text-center">
                <p className="text-xs text-sky-300 mb-1">Your 6-Digit Linking Code:</p>
                <div className="text-3xl font-extrabold tracking-widest text-sky-400 font-mono my-2">
                  {code}
                </div>
                <p className="text-[11px] text-slate-400">Expires in 15 minutes</p>
              </div>

              <button
                onClick={copyCode}
                className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl border border-slate-700 flex items-center justify-center space-x-2"
              >
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                <span>{copied ? 'Command Copied!' : `Copy "/link ${code}"`}</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TelegramModal;
