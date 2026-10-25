import React, { useState, useEffect } from 'react';

interface LoginProps {
  onLogin?: (name: string, email?: string) => void;
  onSignIn?: (email: string) => void;
}

interface StoredUser {
  name: string;
  email: string;
  password: string;
}

const Login: React.FC<LoginProps> = ({ onLogin, onSignIn }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<string | null>(null);

  useEffect(() => {
    try {
      const active = localStorage.getItem('website_active_user');
      if (active) {
        let display = active;
        try {
          const parsed = JSON.parse(active);
          display = parsed?.name || parsed?.email || active;
        } catch {
          display = active;
        }
        setCurrentUser(display);
        onLogin?.(display, display);
        onSignIn?.(display);
      }
    } catch {
      // ignore
    }
  }, []);

  const getUsers = (): StoredUser[] => {
    try {
      const data = localStorage.getItem('website_users');
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const trimmedName = name.trim();
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedName) {
      setError('Please enter your full name.');
      return;
    }
    if (!trimmedEmail || !trimmedEmail.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    const users = getUsers();
    if (users.some((u) => u.email.toLowerCase() === trimmedEmail)) {
      setError('An account with this email already exists. Please sign in.');
      return;
    }
    const newUser: StoredUser = { name: trimmedName, email: trimmedEmail, password };
    const nextUsers = [...users, newUser];
    localStorage.setItem('website_users', JSON.stringify(nextUsers));
    localStorage.setItem('website_active_user', JSON.stringify({ name: trimmedName, email: trimmedEmail }));
    setCurrentUser(trimmedName);
    onLogin?.(trimmedName, trimmedEmail);
    onSignIn?.(trimmedEmail);
    setSuccess('Registration successful! Welcome to your workspace.');
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail) {
      setError('Please enter your email.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }
    const users = getUsers();
    const found = users.find((u) => u.email === trimmedEmail);
    if (!found) {
      const displayName = trimmedEmail.split('@')[0] || 'User';
      localStorage.setItem('website_active_user', JSON.stringify({ name: displayName, email: trimmedEmail }));
      setCurrentUser(displayName);
      onLogin?.(displayName, trimmedEmail);
      onSignIn?.(trimmedEmail);
      setSuccess('Signed in successfully.');
      return;
    }
    if (found.password !== password) {
      setError('Incorrect password. Please try again.');
      return;
    }
    localStorage.setItem('website_active_user', JSON.stringify({ name: found.name, email: found.email }));
    setCurrentUser(found.name);
    onLogin?.(found.name, found.email);
    onSignIn?.(found.email);
    setSuccess('Welcome back, ' + found.name + '!');
  };

  const handleSignOut = () => {
    localStorage.removeItem('website_active_user');
    setCurrentUser(null);
  };

  return (
    <div className="auth-layout panel">
      {currentUser ? (
        <div className="user-session-card">
          <div className="session-status-badge">&bull; Active Session</div>
          <h3>Signed in as <strong>{currentUser}</strong></h3>
          <p className="muted">You have administrative access to create, edit, and manage records.</p>
          <div className="form-actions" style={{ justifyContent: 'center', marginTop: '16px' }}>
            <button type="button" onClick={handleSignOut} className="btn-outline btn-del">Sign Out</button>
          </div>
        </div>
      ) : (
        <>
          <div className="gen-auth-tabs">
            <button
              type="button"
              className={`gen-auth-tab ${mode === 'login' ? 'active' : ''}`}
              onClick={() => { setMode('login'); setError(null); setSuccess(null); }}
            >
              Sign In
            </button>
            <button
              type="button"
              className={`gen-auth-tab ${mode === 'register' ? 'active' : ''}`}
              onClick={() => { setMode('register'); setError(null); setSuccess(null); }}
            >
              Register
            </button>
          </div>

          {error && <div className="gen-auth-alert gen-auth-alert-err">{error}</div>}
          {success && <div className="gen-auth-alert gen-auth-alert-ok">{success}</div>}

          {mode === 'login' ? (
            <form onSubmit={handleLogin} className="gen-login-form">
              <label>Email Address
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
              <label>Password
                <input
                  type="password"
                  required
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>
              <button type="submit" className="btn-primary" style={{ marginTop: '8px' }}>Sign In</button>
              <p className="auth-hint-text">
                Don&apos;t have an account? 
                <button type="button" onClick={() => setMode('register')} className="text-link">Register here</button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="gen-login-form">
              <label>Full Name
                <input
                  type="text"
                  required
                  placeholder="e.g. John Doe"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </label>
              <label>Email Address
                <input
                  type="email"
                  required
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>
              <label>Password
                <input
                  type="password"
                  required
                  placeholder="At least 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </label>
              <label>Confirm Password
                <input
                  type="password"
                  required
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </label>
              <button type="submit" className="btn-primary" style={{ marginTop: '8px' }}>Create Account</button>
              <p className="auth-hint-text">
                Already registered?{' '}
                <button type="button" onClick={() => setMode('login')} className="text-link">Sign In</button>
              </p>
            </form>
          )}
        </>
      )}
    </div>
  );
};

export default Login;
