import React from 'react';

interface LoginProps {
  onLogin: (email: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [submitted, setSubmitted] = React.useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email.trim()) return;
    onLogin(email.trim());
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div className="login-card">
        <h2>Signed in!</h2>
        <p className="muted">Successfully signed in as {email}. You can now create new records.</p>
      </div>
    );
  }

  return (
    <div className="login-card">
      <h2>Welcome to Hospital Management System</h2>
      <p className="muted">Securely sign in to continue managing your workspace.</p>
      <form onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </label>
        <button type="submit">Sign In</button>
        <p className="form-note">Demo login — any email &amp; password works here.</p>
      </form>
    </div>
  );
};

export default Login;
