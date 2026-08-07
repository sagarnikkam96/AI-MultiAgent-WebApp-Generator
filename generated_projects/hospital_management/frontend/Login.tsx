import { useState } from 'react';
import './Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    // Simulate login process (replace with actual authentication logic)
    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      // Handle successful login
    } catch (error) {
      console.error(error);
      alert('Login failed. Please check your credentials.');
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={(e) => e.preventDefault()}>
        <div className="input-group">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="input-group">
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" onClick={handleLogin}>
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;