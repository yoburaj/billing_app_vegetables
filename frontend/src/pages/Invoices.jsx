import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import {
    FileText,
    Download,
    Eye,
    Search,
    Filter,
    Calendar,
    X
} from 'lucide-react';
import { billingApi } from '../services/api';
import { format } from 'date-fns';
import InvoicePreview from '../components/InvoicePreview';
import { searchWithTanglish } from '../utils/tanglishMap';
import './Invoices.css';

const Invoices = () => {
    const location = useLocation();
    const [invoices, setInvoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState(location.state?.search || '');
    const [showFilterModal, setShowFilterModal] = useState(false);
    const [showDateRangeModal, setShowDateRangeModal] = useState(false);
    const [showViewModal, setShowViewModal] = useState(false);
    const [selectedInvoice, setSelectedInvoice] = useState(null);

    // Filter states
    const [dateRange, setDateRange] = useState({ start: '', end: '' });
    const [typeFilter, setTypeFilter] = useState('all');

    useEffect(() => {
        fetchInvoices();
    }, []);

    const fetchInvoices = async () => {
        try {
            const response = await billingApi.getHistory();
            console.log('API Response:', response.data);
            setInvoices(response.data);
        } catch (error) {
            console.error('Failed to fetch history:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPdf = async (id, billNumber) => {
        try {
            const response = await billingApi.getBillPdf(id);
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `bill_${billNumber}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Failed to download PDF:', error);
        }
    };

    const handleViewInvoice = async (invoice) => {
        try {
            const response = await billingApi.getBill(invoice.id);
            setSelectedInvoice(response.data);
            setShowViewModal(true);
        } catch (error) {
            console.error('Failed to fetch invoice details:', error);
            // Fallback to using the invoice from list
            setSelectedInvoice(invoice);
            setShowViewModal(true);
        }
    };

    const normalizedInvoices = invoices.map(inv => ({
        ...inv,
        billNumber: inv.billNumber || inv.bill_number || '',
        customerName: inv.customerName || inv.customer_name || '',
        customerMobile: inv.customerMobile || inv.customer_mobile || '',
        mode: inv.mode || inv.billing_type || 'Retail',
        grandTotal: inv.grandTotal || inv.total_amount || 0,
        date: inv.date || inv.created_at || new Date().toISOString()
    }));

    const filteredInvoices = normalizedInvoices.filter(inv => {
        if (!filter && typeFilter === 'all' && !dateRange.start && !dateRange.end) return true;

        const searchLower = filter.toLowerCase();
        const tanglishEquivalent = searchWithTanglish(filter);

        const matchesSearch = !filter || (
            inv.billNumber.toLowerCase().includes(searchLower) ||
            inv.customerName.toLowerCase().includes(searchLower) ||
            inv.customerMobile.includes(searchLower) ||
            // Check if any vegetable item name matches original or tanglish search
            (inv.items && inv.items.some(item => {
                const itemName = (item.name || item.vegetable_name || '').toLowerCase();
                const itemTamil = (item.tamilName || item.tamil_name || '').toLowerCase();
                return itemName.includes(searchLower) ||
                    itemName.includes(tanglishEquivalent) ||
                    itemTamil.includes(searchLower);
            }))
        );

        const matchesType = typeFilter === 'all' || inv.mode.toLowerCase() === typeFilter.toLowerCase();

        let matchesDate = true;
        if (dateRange.start || dateRange.end) {
            const invDate = new Date(inv.date);
            if (dateRange.start) {
                matchesDate = matchesDate && invDate >= new Date(dateRange.start);
            }
            if (dateRange.end) {
                matchesDate = matchesDate && invDate <= new Date(dateRange.end);
            }
        }

        return matchesSearch && matchesType && matchesDate;
    });

    const applyDateRange = () => {
        setShowDateRangeModal(false);
    };

    const clearDateRange = () => {
        setDateRange({ start: '', end: '' });
        setShowDateRangeModal(false);
    };

    const applyFilters = () => {
        setShowFilterModal(false);
    };

    return (
        <div className="invoices-container">
            <div className="card toolbar-card">
                <div className="search-bar">
                    <Search size={20} />
                    <input
                        type="text"
                        placeholder="Search by Bill #, Customer or Items (e.g. thakkali)"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    />
                </div>
                <div className="toolbar-actions">
                    <button className="btn btn-outline" onClick={() => setShowDateRangeModal(true)}>
                        <Calendar size={18} />
                        Date Range
                    </button>
                    <button className="btn btn-outline" onClick={() => setShowFilterModal(true)}>
                        <Filter size={18} />
                        Filter
                    </button>
                </div>
            </div>

            <div className="card table-card">
                <table className="invoices-table">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Bill Number</th>
                            <th>Customer</th>
                            <th>Type</th>
                            <th>Amount</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan="6" className="loading-row">Loading invoices...</td></tr>
                        ) : filteredInvoices.length > 0 ? (
                            filteredInvoices.map(inv => (
                                <tr key={inv.id}>
                                    <td>{format(new Date(inv.date), 'dd MMM yyyy')}</td>
                                    <td className="bill-num">{inv.billNumber}</td>
                                    <td>{inv.customerName || 'Walking Customer'}</td>
                                    <td>
                                        <span className={`badge ${inv.mode?.toLowerCase() || 'retail'}`}>
                                            {inv.mode}
                                        </span>
                                    </td>
                                    <td className="amount">₹{inv.grandTotal?.toFixed(2)}</td>
                                    <td>
                                        <div className="actions">
                                            <button title="View Detail" onClick={() => handleViewInvoice(inv)}>
                                                <Eye size={18} />
                                            </button>
                                            <button
                                                title="Download PDF"
                                                onClick={() => handleDownloadPdf(inv.id, inv.billNumber)}
                                            >
                                                <Download size={18} />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr><td colSpan="6" className="empty-row">No invoices found.</td></tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Date Range Modal */}
            {showDateRangeModal && (
                <div className="modal-overlay">
                    <div className="card modal-content" style={{ maxWidth: '400px' }}>
                        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <h2>Select Date Range</h2>
                            <button onClick={() => setShowDateRangeModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                                <X size={24} />
                            </button>
                        </div>
                        <div className="form-group">
                            <label>Start Date</label>
                            <input
                                type="date"
                                value={dateRange.start}
                                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>End Date</label>
                            <input
                                type="date"
                                value={dateRange.end}
                                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                            />
                        </div>
                        <div className="modal-actions" style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                            <button className="btn btn-outline" onClick={clearDateRange}>Clear</button>
                            <button className="btn btn-primary" onClick={applyDateRange}>Apply</button>
                        </div>
                    </div>
                </div>
            )}

            {/* Filter Modal */}
            {showFilterModal && (
                <div className="modal-overlay">
                    <div className="card modal-content" style={{ maxWidth: '400px' }}>
                        <div className="modal-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
                            <h2>Filter Invoices</h2>
                            <button onClick={() => setShowFilterModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
                                <X size={24} />
                            </button>
                        </div>
                        <div className="form-group">
                            <label>Billing Type</label>
                            <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                                <option value="all">All Types</option>
                                <option value="retail">Retail</option>
                                <option value="wholesale">Wholesale</option>
                            </select>
                        </div>
                        <div className="modal-actions" style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                            <button className="btn btn-outline" onClick={() => { setTypeFilter('all'); setShowFilterModal(false); }}>Clear</button>
                            <button className="btn btn-primary" onClick={applyFilters}>Apply</button>
                        </div>
                    </div>
                </div>
            )}

            {/* View Invoice Modal */}
            {showViewModal && selectedInvoice && (
                <InvoicePreview
                    data={selectedInvoice}
                    onClose={() => setShowViewModal(false)}
                />
            )}
        </div>
    );
};

export default Invoices;
