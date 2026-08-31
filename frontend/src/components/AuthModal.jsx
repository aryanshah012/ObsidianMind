import React, { useState } from 'react';
import {
  Lock,
  Mail,
  User,
  Sparkles,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,
  ShieldCheck,
  AlertCircle,
  FolderLock,
} from 'lucide-react';

export default function AuthModal({ onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_BASE = import.meta.env.VITE_API_BASE || '';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (isRegister) {
        if (!username.trim() || !email.trim() || !password.trim()) {
          throw new Error('Please fill in all required fields.');
        }
        if (password.length < 6) {
          throw new Error('Password must be at least 6 characters long.');
        }

        const res = await fetch(`${API_BASE}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: username.trim(),
            email: email.trim(),
            password: password,
            full_name: fullName.trim() || username.trim(),
          }),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Registration failed.');
        }

        onLoginSuccess(data.token, data.user);
      } else {
        if (!username.trim() || !password.trim()) {
          throw new Error('Please enter your username/email and password.');
        }

        const res = await fetch(`${API_BASE}/api/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username_or_email: username.trim(),
            password: password,
          }),
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Invalid login credentials.');
        }

        onLoginSuccess(data.token, data.user);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemo = async () => {
    setError(null);
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username_or_email: 'demo',
          password: 'demopassword123',
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Demo login failed.');
      }
      onLoginSuccess(data.token, data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm select-none overflow-y-auto animate-fade-in">
      <div className="w-full max-w-md my-8 rounded-2xl bg-surface border border-border/90 p-6 sm:p-8 shadow-2xl space-y-6 relative overflow-hidden">
        {/* Ambient Top Glow */}
        <div className="absolute -top-24 -left-24 w-48 h-48 bg-sage/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Brand Header */}
        <div className="text-center space-y-2 relative">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#183B32] border border-[#2E7D6A]/50 text-emerald-300 shadow-md mb-1">
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="#A7D4C6"
                strokeWidth="1.8"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-charcoal font-sans">
            ObsidianMind
          </h2>
          <p className="text-xs text-charcoal-muted max-w-xs mx-auto">
            {isRegister
              ? 'Create a secure personal knowledge vault isolated for you.'
              : 'Sign in to access your personal knowledge workspace.'}
          </p>
        </div>

        {/* Auth Mode Toggle Tabs */}
        <div className="flex rounded-xl bg-canvas-subtle p-1 border border-border/80">
          <button
            type="button"
            onClick={() => {
              setIsRegister(false);
              setError(null);
            }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              !isRegister
                ? 'bg-surface text-charcoal shadow-sm border border-border/60'
                : 'text-charcoal-muted hover:text-charcoal'
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setIsRegister(true);
              setError(null);
            }}
            className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
              isRegister
                ? 'bg-surface text-charcoal shadow-sm border border-border/60'
                : 'text-charcoal-muted hover:text-charcoal'
            }`}
          >
            Create Account
          </button>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 text-xs flex items-center gap-2.5 animate-fade-in">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {/* Form Fields */}
        <form onSubmit={handleSubmit} className="space-y-3.5">
          {isRegister && (
            <div>
              <label className="block text-[11px] font-mono uppercase tracking-wider text-charcoal-muted font-medium mb-1">
                Full Name (Optional)
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
                <input
                  type="text"
                  placeholder="e.g. Aryan Shah"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-canvas-subtle border border-border rounded-xl pl-9 pr-3.5 py-2.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage font-sans transition-all"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-charcoal-muted font-medium mb-1">
              {isRegister ? 'Username' : 'Username or Email'}
            </label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
              <input
                type="text"
                required
                placeholder={isRegister ? 'e.g. aryan' : 'Enter username or email'}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-canvas-subtle border border-border rounded-xl pl-9 pr-3.5 py-2.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage font-sans transition-all"
              />
            </div>
          </div>

          {isRegister && (
            <div>
              <label className="block text-[11px] font-mono uppercase tracking-wider text-charcoal-muted font-medium mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
                <input
                  type="email"
                  required
                  placeholder="e.g. aryan@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-canvas-subtle border border-border rounded-xl pl-9 pr-3.5 py-2.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage font-sans transition-all"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-[11px] font-mono uppercase tracking-wider text-charcoal-muted font-medium mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-charcoal-subtle" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-canvas-subtle border border-border rounded-xl pl-9 pr-10 py-2.5 text-xs text-charcoal placeholder-charcoal-subtle focus:outline-none focus:border-sage focus:ring-1 focus:ring-sage font-sans transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-charcoal-subtle hover:text-charcoal transition-colors p-1"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? (
                  <EyeOff className="w-3.5 h-3.5" />
                ) : (
                  <Eye className="w-3.5 h-3.5" />
                )}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-2.5 px-4 rounded-xl bg-sage hover:bg-sage-hover text-white text-xs font-semibold font-sans flex items-center justify-center gap-2 transition-all shadow-md active:scale-[0.98] disabled:opacity-60 cursor-pointer mt-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{isRegister ? 'Creating Account...' : 'Signing In...'}</span>
              </>
            ) : (
              <>
                <span>{isRegister ? 'Create Personal Account' : 'Sign In to Workspace'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </form>

        {/* Quick Demo Login Option */}
        <div className="pt-2 border-t border-border/80 space-y-3">
          <div className="flex items-center justify-between text-[11px] text-charcoal-muted">
            <span className="flex items-center gap-1.5 font-mono text-[10px]">
              <ShieldCheck className="w-3.5 h-3.5 text-sage" />
              Personal & Isolated Vaults
            </span>
            <button
              type="button"
              onClick={handleQuickDemo}
              disabled={isLoading}
              className="text-sage hover:text-sage-hover font-semibold flex items-center gap-1 hover:underline transition-all"
            >
              <Sparkles className="w-3 h-3 text-sage" />
              <span>1-Click Demo Login</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
