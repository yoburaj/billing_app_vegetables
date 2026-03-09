import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { billingApi } from '../services/api';
import {
    Users,
    Search,
    Phone,
    Calendar,
    Receipt,
    IndianRupee,
    ArrowUpRight,
    User,
    ChevronRight,
    Clock,
    Filter
} from 'lucide-react';
import './Customers.css';

const Customers = () => {
    const navigate = useNavigate();
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('all'); // 'all', 'regular', 'new'

    useEffect(() => {
        fetchCustomers();
    }, []);

    const fetchCustomers = async () => {
        try {
            setLoading(true);
            const response = await billingApi.getCustomerStats();
            setCustomers(response.data);
        } catch (error) {
            console.error("Error fetching customers:", error);
        } finally {
            setLoading(false);
        }
    };

    const filteredCustomers = customers.filter(customer => {
        const matchesSearch =
            customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            customer.mobile_number.includes(searchTerm);

        if (filterType === 'regular') return matchesSearch && customer.total_purchases > 5;
        if (filterType === 'new') return matchesSearch && customer.total_purchases <= 1;

        return matchesSearch;
    });

    const stats = {
        totalCustomers: customers.length,
        regularCustomers: customers.filter(c => c.total_purchases > 5).length,
        totalRevenue: customers.reduce((acc, c) => acc + c.total_spent, 0)
    };

    return (
        <div className="customers-container">
            <div className="customers-header">
                <div className="header-title">
                    <div className="title-icon">
                        <Users size={24} color="var(--primary-color)" />
                    </div>
                    <div>
                        <h1>Customer Directory</h1>
                        <p>Manage and view your customer purchase history</p>
                    </div>
                </div>

                <div className="header-stats">
                    <div className="mini-stat-card">
                        <User size={18} />
                        <div>
                            <span>Total</span>
                            <strong>{stats.totalCustomers}</strong>
                        </div>
                    </div>
                    <div className="mini-stat-card regular">
                        <Clock size={18} />
                        <div>
                            <span>Regular</span>
                            <strong>{stats.regularCustomers}</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div className="customers-toolbar">
                <div className="search-box">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Search by name or phone..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <div className="filter-options">
                    <button
                        className={`filter-btn ${filterType === 'all' ? 'active' : ''}`}
                        onClick={() => setFilterType('all')}
                    >
                        All
                    </button>
                    <button
                        className={`filter-btn ${filterType === 'regular' ? 'active' : ''}`}
                        onClick={() => setFilterType('regular')}
                    >
                        Regulars
                    </button>
                    <button
                        className={`filter-btn ${filterType === 'new' ? 'active' : ''}`}
                        onClick={() => setFilterType('new')}
                    >
                        New
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="loading-state">
                    <div className="spinner"></div>
                    <p>Loading customers...</p>
                </div>
            ) : filteredCustomers.length > 0 ? (
                <div className="customers-grid">
                    {filteredCustomers.map((customer, index) => (
                        <div key={index} className="customer-card">
                            <div className="customer-card-header">
                                <div className="customer-avatar">
                                    {customer.name.charAt(0).toUpperCase()}
                                </div>
                                <div className="customer-info">
                                    <h3>{customer.name}</h3>
                                    <div className="mobile-link">
                                        <Phone size={14} />
                                        <span>{customer.mobile_number}</span>
                                    </div>
                                </div>
                                <div className="customer-badge">
                                    {customer.total_purchases > 5 ? 'REGULAR' : 'NEW'}
                                </div>
                            </div>

                            <div className="customer-card-stats">
                                <div className="card-stat">
                                    <Receipt size={16} />
                                    <div>
                                        <label>Visits</label>
                                        <p>{customer.total_purchases}</p>
                                    </div>
                                </div>
                                <div className="card-stat">
                                    <IndianRupee size={16} />
                                    <div>
                                        <label>Total Spent</label>
                                        <p>₹{customer.total_spent.toLocaleString()}</p>
                                    </div>
                                </div>
                            </div>

                            <div className="recent-purchase">
                                <div className="recent-label">
                                    <Calendar size={14} />
                                    <span>Last Purchase</span>
                                </div>
                                <div className="recent-details">
                                    <strong>{customer.last_bill_number}</strong>
                                    <span>{new Date(customer.last_purchase_date).toLocaleDateString()}</span>
                                </div>
                            </div>

                            <button
                                className="view-history-btn"
                                onClick={() => navigate('/invoices', { state: { search: customer.mobile_number } })}
                            >
                                View History <ChevronRight size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state">
                    <Users size={48} />
                    <h3>No customers found</h3>
                    <p>Try adjusting your search or filters</p>
                </div>
            )}
        </div>
    );
};

export default Customers;
