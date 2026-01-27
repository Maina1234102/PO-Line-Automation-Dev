import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginPage.css';

const LoginPage = () => {
    const [credentials, setCredentials] = useState({ email: '', password: '' });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setCredentials(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        // Real authentication logic calling the backend
        try {
            const response = await fetch('https://172.16.10.130:8000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('isAuthenticated', 'true');
                localStorage.setItem('userEmail', credentials.email);
                localStorage.setItem('userPassword', credentials.password);
                navigate('/');
            } else {
                setError(data.detail || 'Invalid email or password.');
            }
        } catch (err) {
            console.error('Login error:', err);
            setError('Unable to connect to the server. Please try again later.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-glass-card">
                <div className="login-header">
                    <h1>Poline Creation</h1>
                    <p>Enter your credentials to access the portal</p>
                </div>
                <form className="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email Address</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={credentials.email}
                            onChange={handleChange}
                            placeholder="name@company.com"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={credentials.password}
                            onChange={handleChange}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    {error && <div className="login-error-message">{error}</div>}
                    <button type="submit" className={`login-button ${isLoading ? 'loading' : ''}`} disabled={isLoading}>
                        {isLoading ? 'Signing in...' : 'Sign In'}
                    </button>
                    <div className="login-footer">
                        <p>© 2026 Poline Creation Systems. All rights reserved.</p>
                    </div>
                </form>
            </div>
            <div className="background-decor">
                <div className="circle circle-1"></div>
                <div className="circle circle-2"></div>
                <div className="circle circle-3"></div>
            </div>
        </div>
    );
};

export default LoginPage;
