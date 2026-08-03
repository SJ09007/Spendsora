import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/common/Sidebar';
import Header from './components/common/Header';
import QuickLogModal from './components/common/QuickLogModal';
import TelegramModal from './components/common/TelegramModal';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Expenses from './pages/Expenses';
import Analytics from './pages/Analytics';
import Budgets from './pages/Budgets';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

const ProtectedLayout = ({ children, onSearchResults, searchResult }) => {
  const { user, loading } = useAuth();
  const [isQuickLogOpen, setIsQuickLogOpen] = useState(false);
  const [isTelegramOpen, setIsTelegramOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-indigo-400">
        Loading ExpenseSense AI...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      <Sidebar
        onOpenQuickLog={() => setIsQuickLogOpen(true)}
        onOpenTelegram={() => setIsTelegramOpen(true)}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title="ExpenseSense AI Dashboard"
          subtitle="Real-time personal finance intelligence & Telegram tracker"
          onSearchResults={onSearchResults}
        />
        <main className="flex-1 overflow-y-auto">
          {React.cloneElement(children, {
            onOpenQuickLog: () => setIsQuickLogOpen(true),
            searchResult: searchResult
          })}
        </main>
      </div>

      <QuickLogModal
        isOpen={isQuickLogOpen}
        onClose={() => setIsQuickLogOpen(false)}
        onSuccess={() => window.location.reload()}
      />
      <TelegramModal
        isOpen={isTelegramOpen}
        onClose={() => setIsTelegramOpen(false)}
      />
    </div>
  );
};

function AppRoutes() {
  const [searchResult, setSearchResult] = useState(null);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route
        path="/"
        element={
          <ProtectedLayout onSearchResults={(res) => setSearchResult(res)} searchResult={searchResult}>
            <Dashboard />
          </ProtectedLayout>
        }
      />
      <Route
        path="/expenses"
        element={
          <ProtectedLayout>
            <Expenses />
          </ProtectedLayout>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedLayout>
            <Analytics />
          </ProtectedLayout>
        }
      />
      <Route
        path="/budgets"
        element={
          <ProtectedLayout>
            <Budgets />
          </ProtectedLayout>
        }
      />
      <Route
        path="/recurring"
        element={
          <ProtectedLayout>
            <Budgets />
          </ProtectedLayout>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedLayout>
            <Reports />
          </ProtectedLayout>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedLayout>
            <Settings />
          </ProtectedLayout>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}
