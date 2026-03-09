import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    IndianRupee,
    PlusCircle,
    Store,
    LogOut,
    Menu,
    X,
    ChevronRight,
    User,
    Users,
    Edit,
    Save,
    XCircle
} from 'lucide-react';
import logo from '../../assets/login_logo.png';
import useAuthStore from '../../store/useAuthStore';
import './Layout.css';

const MainLayout = ({ children }) => {
    const [isSidebarOpen, setSidebarOpen] = useState(true);
    const [isEditingProfile, setIsEditingProfile] = useState(false);
    const [editFormData, setEditFormData] = useState({
        username: '',
        shop_name: ''
    });
    const location = useLocation();
    const navigate = useNavigate();
    const { logout, user } = useAuthStore();

    const menuItems = [
        { name: 'Dashboard', icon: LayoutDashboard, path: '/' },
        { name: 'New Invoice', icon: PlusCircle, path: '/invoice/new' },
        { name: 'Invoices History', icon: IndianRupee, path: '/invoices' },
        { name: 'Inventory', icon: Store, path: '/inventory' },
        { name: 'Customers', icon: Users, path: '/customers' },
    ];

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleEditProfile = () => {
        setEditFormData({
            username: user?.username || '',
            shop_name: user?.shop_name || ''
        });
        setIsEditingProfile(true);
    };

    const handleSaveProfile = () => {
        // Update user data in store
        if (user) {
            const updatedUser = {
                ...user,
                username: editFormData.username,
                shop_name: editFormData.shop_name
            };
            // You can add an API call here to persist to backend
            localStorage.setItem('user', JSON.stringify(updatedUser));
            setIsEditingProfile(false);
        }
    };

    const handleCancelEdit = () => {
        setIsEditingProfile(false);
    };

    return (
        <div className="layout-container">
            {/* Sidebar */}
            <aside className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <div className="logo-container">
                        <div className="logo-icon logo-img-container">
                            <img src={logo} alt="Suji Vegetables" className="sidebar-logo-img" />
                        </div>
                        <span className="logo-text">Suji Vegetables</span>
                    </div>
                    <button className="sidebar-toggle" onClick={() => setSidebarOpen(!isSidebarOpen)}>
                        {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>

                <nav className="sidebar-nav">
                    {menuItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                        >
                            <item.icon size={22} />
                            {isSidebarOpen && <span>{item.name}</span>}
                            {isSidebarOpen && location.pathname === item.path && (
                                <ChevronRight size={16} className="active-indicator" />
                            )}
                        </Link>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="user-profile" onClick={handleEditProfile} style={{ cursor: 'pointer' }}>
                        <div className="avatar">
                            <User size={20} />
                        </div>
                        {isSidebarOpen && (
                            <div className="user-info">
                                <p className="username">{user?.shop_name || user?.username || 'Store'}</p>
                                <p className="shop-name">{user?.username || 'User'}</p>
                            </div>
                        )}
                        {isSidebarOpen && (
                            <div className="edit-profile-icon">
                                <Edit size={14} />
                            </div>
                        )}
                    </div>
                    <button className="logout-btn" onClick={handleLogout}>
                        <LogOut size={20} />
                        {isSidebarOpen && <span>Logout</span>}
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <header className="topbar">
                    <div className="topbar-left">
                        <button className="mobile-menu-trigger" onClick={() => setSidebarOpen(true)}>
                            <Menu size={24} />
                        </button>
                        <div className="page-title">
                            <h2>{menuItems.find(item => item.path === location.pathname)?.name || 'VegBilling'}</h2>
                        </div>
                    </div>
                    <div className="topbar-actions">
                        <button className="notification-btn">
                            <span className="badge"></span>
                        </button>
                    </div>
                </header>

                <section className="page-content">
                    {children}
                </section>

                {/* Mobile Overlay */}
                {isSidebarOpen && (
                    <div
                        className="mobile-overlay"
                        onClick={() => setSidebarOpen(false)}
                    ></div>
                )}
            </main>

            {isEditingProfile && (
                <div className="profile-modal-overlay" onClick={handleCancelEdit}>
                    <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Edit Profile</h3>
                            <button className="modal-close" onClick={handleCancelEdit}>
                                <XCircle size={20} />
                            </button>
                        </div>

                        <div className="modal-body">
                            <div className="form-group-modal">
                                <label>Shop Name</label>
                                <input
                                    type="text"
                                    value={editFormData.shop_name}
                                    onChange={(e) => setEditFormData({ ...editFormData, shop_name: e.target.value })}
                                    placeholder="Enter shop name"
                                />
                            </div>

                            <div className="form-group-modal">
                                <label>Username</label>
                                <input
                                    type="text"
                                    value={editFormData.username}
                                    onChange={(e) => setEditFormData({ ...editFormData, username: e.target.value })}
                                    placeholder="Enter username"
                                />
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button className="btn-save" onClick={handleSaveProfile}>
                                <Save size={16} />
                                Save Changes
                            </button>
                            <button className="btn-cancel" onClick={handleCancelEdit}>
                                <X size={16} />
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MainLayout;
