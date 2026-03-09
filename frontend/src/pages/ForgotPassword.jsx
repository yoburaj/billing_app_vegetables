import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Mail,
    Phone,
    Lock,
    Eye,
    EyeOff,
    ArrowLeft,
    CheckCircle,
    ShieldCheck,
    KeyRound,
    Loader2,
} from 'lucide-react';
import { authApi } from '../services/api';
import logo from '../assets/login_logo.png';
import './Auth.css';
import './ForgotPassword.css';

// ─── Step indicators ───────────────────────────────────────────────────────────
const STEPS = [
    { id: 1, label: 'Verify Identity' },
    { id: 2, label: 'Reset Password' },
];

const ForgotPassword = () => {
    // ── shared state ──────────────────────────────────────────────────────────
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

    // ── step 1 ────────────────────────────────────────────────────────────────
    const [username, setUsername] = useState('');
    const [mobile, setMobile] = useState('');

    // ── step 2 ────────────────────────────────────────────────────────────────
    const [resetToken, setResetToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const navigate = useNavigate();

    // ── password strength ────────────────────────────────────────────────────
    const getStrength = (pwd) => {
        let score = 0;
        if (pwd.length >= 8) score++;
        if (/[A-Z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return score; // 0-4
    };

    const strengthLabel = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthClass = ['', 'weak', 'fair', 'good', 'strong'];
    const pwdStrength = getStrength(newPassword);

    // ── handlers ─────────────────────────────────────────────────────────────
    const handleVerify = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const res = await authApi.forgotPassword({
                username: username.trim(),
                mobile_number: mobile.trim(),
            });
            setResetToken(res.data.reset_token);
            setStep(2);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                'Verification failed. Check your username and mobile number.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = async (e) => {
        e.preventDefault();
        setError('');

        if (newPassword !== confirmPassword) {
            setError('Passwords do not match.');
            return;
        }
        if (pwdStrength < 2) {
            setError('Password is too weak. Add uppercase letters, numbers, or symbols.');
            return;
        }

        setLoading(true);
        try {
            await authApi.resetPassword({
                reset_token: resetToken,
                new_password: newPassword,
            });
            setSuccess(true);
        } catch (err) {
            const msg =
                err?.response?.data?.detail ||
                'Failed to reset password. The reset session may have expired.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    // ── success screen ────────────────────────────────────────────────────────
    if (success) {
        return (
            <div className="auth-container">
                <div className="auth-card glass fp-success-card">
                    <div className="fp-success-icon">
                        <CheckCircle size={64} strokeWidth={1.5} />
                    </div>
                    <h2 className="fp-success-title">Password Reset!</h2>
                    <p className="fp-success-sub">
                        Your password has been updated successfully. You can now log in with
                        your new credentials.
                    </p>
                    <button
                        className="btn btn-primary login-btn"
                        onClick={() => navigate('/login')}
                    >
                        Go to Login
                    </button>
                </div>
            </div>
        );
    }

    // ── main render ───────────────────────────────────────────────────────────
    return (
        <div className="auth-container">
            <div className="auth-card glass">
                {/* Logo */}
                <div className="auth-header">
                    <div className="auth-logo-img">
                        <img src={logo} alt="Suji Vegetables" />
                    </div>
                    <h1>{step === 1 ? 'Forgot Password' : 'Set New Password'}</h1>
                    <p>
                        {step === 1
                            ? 'Enter your username and registered mobile number to continue'
                            : 'Choose a strong new password for your account'}
                    </p>
                </div>

                {/* Step indicators */}
                <div className="fp-steps">
                    {STEPS.map((s, idx) => (
                        <React.Fragment key={s.id}>
                            <div
                                className={`fp-step ${step === s.id ? 'active' : step > s.id ? 'done' : ''
                                    }`}
                            >
                                <div className="fp-step-circle">
                                    {step > s.id ? <CheckCircle size={16} /> : s.id}
                                </div>
                                <span className="fp-step-label">{s.label}</span>
                            </div>
                            {idx < STEPS.length - 1 && (
                                <div
                                    className={`fp-step-line ${step > s.id ? 'done' : ''}`}
                                />
                            )}
                        </React.Fragment>
                    ))}
                </div>

                {/* Error banner */}
                {error && <div className="auth-error fp-error">{error}</div>}

                {/* ── STEP 1: Verify Identity ─────────────────────────────────────── */}
                {step === 1 && (
                    <form onSubmit={handleVerify} className="auth-form fp-form-enter">
                        <div className="form-group">
                            <label>Username</label>
                            <div className="input-with-icon">
                                <Mail size={20} />
                                <input
                                    id="fp-username"
                                    type="text"
                                    placeholder="Enter your username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                    autoComplete="username"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Registered Mobile Number</label>
                            <div className="input-with-icon">
                                <Phone size={20} />
                                <input
                                    id="fp-mobile"
                                    type="tel"
                                    placeholder="Enter your mobile number"
                                    value={mobile}
                                    onChange={(e) => setMobile(e.target.value)}
                                    required
                                    autoComplete="tel"
                                />
                            </div>
                        </div>

                        <button
                            id="fp-verify-btn"
                            type="submit"
                            className="btn btn-primary login-btn"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 size={20} className="fp-spin" />
                                    Verifying…
                                </>
                            ) : (
                                <>
                                    <ShieldCheck size={20} />
                                    Verify Identity
                                </>
                            )}
                        </button>
                    </form>
                )}

                {/* ── STEP 2: Set New Password ────────────────────────────────────── */}
                {step === 2 && (
                    <form onSubmit={handleReset} className="auth-form fp-form-enter">
                        {/* New password */}
                        <div className="form-group">
                            <label>New Password</label>
                            <div className="input-with-icon">
                                <Lock size={20} />
                                <input
                                    id="fp-new-password"
                                    type={showNew ? 'text' : 'password'}
                                    placeholder="••••••••"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    required
                                    autoComplete="new-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowNew((v) => !v)}
                                >
                                    {showNew ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>

                            {/* Strength bar */}
                            {newPassword && (
                                <div className="fp-strength-wrap">
                                    <div className="fp-strength-bars">
                                        {[1, 2, 3, 4].map((lvl) => (
                                            <div
                                                key={lvl}
                                                className={`fp-strength-bar ${pwdStrength >= lvl ? strengthClass[pwdStrength] : ''
                                                    }`}
                                            />
                                        ))}
                                    </div>
                                    <span className={`fp-strength-label ${strengthClass[pwdStrength]}`}>
                                        {strengthLabel[pwdStrength]}
                                    </span>
                                </div>
                            )}
                        </div>

                        {/* Confirm password */}
                        <div className="form-group">
                            <label>Confirm Password</label>
                            <div className="input-with-icon">
                                <Lock size={20} />
                                <input
                                    id="fp-confirm-password"
                                    type={showConfirm ? 'text' : 'password'}
                                    placeholder="••••••••"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                    autoComplete="new-password"
                                />
                                <button
                                    type="button"
                                    className="password-toggle"
                                    onClick={() => setShowConfirm((v) => !v)}
                                >
                                    {showConfirm ? <EyeOff size={20} /> : <Eye size={20} />}
                                </button>
                            </div>

                            {/* Match indicator */}
                            {confirmPassword && (
                                <p
                                    className={`fp-match-hint ${newPassword === confirmPassword ? 'match' : 'mismatch'
                                        }`}
                                >
                                    {newPassword === confirmPassword
                                        ? '✓ Passwords match'
                                        : '✗ Passwords do not match'}
                                </p>
                            )}
                        </div>

                        <button
                            id="fp-reset-btn"
                            type="submit"
                            className="btn btn-primary login-btn"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <Loader2 size={20} className="fp-spin" />
                                    Resetting…
                                </>
                            ) : (
                                <>
                                    <KeyRound size={20} />
                                    Reset Password
                                </>
                            )}
                        </button>

                        <button
                            type="button"
                            className="fp-back-btn"
                            onClick={() => {
                                setStep(1);
                                setError('');
                            }}
                        >
                            <ArrowLeft size={16} />
                            Back to verification
                        </button>
                    </form>
                )}

                {/* Footer */}
                <div className="auth-footer">
                    <p>
                        Remember your password?{' '}
                        <Link to="/login">Sign in</Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default ForgotPassword;
