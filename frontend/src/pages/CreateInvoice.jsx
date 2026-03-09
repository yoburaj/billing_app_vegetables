import React, { useState, useEffect, useMemo } from 'react';
import {
    Plus,
    Trash2,
    Search,
    Save,
    Printer,
    Calendar,
    X,
    ChevronDown,
    FileText,
    User,
    Phone,
    Check,
    Store,
    ShoppingBag,
    ArrowRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { inventoryApi, billingApi } from '../services/api';
import InvoicePreview from '../components/InvoicePreview';
import { searchWithTanglish } from '../utils/tanglishMap';
import './CreateInvoice.css';

const CreateInvoice = () => {
    const [items, setItems] = useState([]);
    const [inventory, setInventory] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [customerName, setCustomerName] = useState('');
    const [customerPhone, setCustomerPhone] = useState('');
    const [isLookingUp, setIsLookingUp] = useState(false);
    const [lookupStatus, setLookupStatus] = useState(null); // 'found', 'reset', 'not_found'
    const [billingType, setBillingType] = useState('Retail');
    const [discount, setDiscount] = useState(0);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [showPreview, setShowPreview] = useState(false);
    const [showResults, setShowResults] = useState(false);
    const [savedBill, setSavedBill] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        fetchInventory();
    }, []);

    const fetchInventory = async () => {
        try {
            const response = await inventoryApi.getInventory();
            setInventory(response.data);
        } catch (error) {
            console.error('Failed to fetch inventory:', error);
        }
    };

    const addItem = (veg) => {
        if (!veg) return;

        const id = veg.id || veg.vegetable_id || veg._id || Math.random();
        const name = veg.name || veg.vegetable_name || 'Unknown Item';
        const tamil = veg.tamil_name || veg.tamilName || '';
        const price = billingType === 'Wholesale'
            ? (veg.wholesale_price || veg.wholesalePrice || veg.price || 0)
            : (veg.retail_price || veg.retailPrice || veg.price || 0);

        setItems(prev => {
            const existing = prev.find(i => i.id === id);
            if (existing) {
                return prev.map(i => i.id === id
                    ? { ...i, quantity: i.quantity + 1, total: (i.quantity + 1) * i.price }
                    : i
                );
            }
            return [...prev, {
                id,
                name,
                tamilName: tamil,
                price,
                quantity: 1,
                total: price,
                unit: 'kg'
            }];
        });
        setSearchTerm('');
    };

    const removeItem = (id) => {
        setItems(items.filter(item => item.id !== id));
    };

    const updateQuantity = (id, newQty) => {
        if (newQty < 0.1) return;
        setItems(prevItems => prevItems.map(item =>
            item.id === id ? { ...item, quantity: Math.round(newQty * 100) / 100, total: (Math.round(newQty * 100) / 100) * item.price } : item
        ));
    };

    const updateItemTotal = (id, newTotal) => {
        setItems(prevItems => prevItems.map(item =>
            item.id === id ? {
                ...item,
                total: newTotal,
                price: item.quantity > 0 ? newTotal / item.quantity : 0
            } : item
        ));
    };

    const updatePrice = (id, newPrice) => {
        setItems(prevItems => prevItems.map(item =>
            item.id === id ? {
                ...item,
                price: newPrice,
                total: newPrice * item.quantity
            } : item
        ));
    };

    const calculateSubtotal = () => items.reduce((sum, item) => sum + item.total, 0);
    const calculateTax = () => calculateSubtotal() * 0; // Assuming 0% tax for now
    const calculateTotal = () => Math.max(0, calculateSubtotal() + calculateTax() - discount);

    const handlePhoneChange = async (value) => {
        setCustomerPhone(value);
        setLookupStatus(null);

        // Auto-lookup if 10 digits
        if (value.length === 10) {
            setIsLookingUp(true);
            try {
                const response = await billingApi.lookupCustomer(value);
                if (response.data) {
                    setCustomerName(response.data.name);
                    setLookupStatus('found');
                }
            } catch (_error) {
                console.log('Customer not found');
                setLookupStatus('not_found');
            } finally {
                setIsLookingUp(false);
            }
        }
    };

    const handleCreateBill = async () => {
        if (items.length === 0) return;
        setLoading(true);
        try {
            const billData = {
                customer_name: customerName,
                customer_mobile: customerPhone,
                billing_type: billingType,
                items: items.map(item => ({
                    id: item.id,
                    name: item.name,
                    tamilName: item.tamilName,
                    quantity: item.quantity,
                    price: item.price,
                    total: item.total
                })),
                subtotal: calculateSubtotal(),
                tax_amount: calculateTax(),
                discount_amount: discount,
                grand_total: calculateTotal()
            };
            const response = await billingApi.createBill(billData);
            setSavedBill(response.data);
            setSuccess(true);
            setItems([]);
            setCustomerName('');
            setDiscount(0);
        } catch (error) {
            console.error('Failed to create bill:', error);
            alert('Error creating bill');
        } finally {
            setLoading(false);
        }
    };

    // Enhanced filter with Tanglish support
    const filteredInventory = useMemo(() => {
        return inventory
            .filter(veg => {
                if (!searchTerm) return true;
                const lowerSearch = searchTerm.toLowerCase();
                const tanglishEquivalent = searchWithTanglish(searchTerm);

                return veg.name.toLowerCase().includes(lowerSearch) ||
                    veg.name.toLowerCase().includes(tanglishEquivalent) ||
                    (veg.tamilName && veg.tamilName.toLowerCase().includes(lowerSearch));
            })
            .sort((a, b) => {
                const getPriorityIndex = (name) => {
                    const lowName = name.toLowerCase();
                    if (lowName.includes('chili') || lowName.includes('chilly')) return 0;
                    if (lowName.includes('tomato')) return 1;
                    if (lowName.includes('onion')) return 2;
                    if (lowName.includes('potato')) return 3;
                    if (lowName.includes('beans')) return 4;
                    if (lowName.includes('carrot')) return 5;
                    return 100;
                };

                const indexA = getPriorityIndex(a.name);
                const indexB = getPriorityIndex(b.name);

                if (indexA !== indexB) return indexA - indexB;
                return a.name.localeCompare(b.name);
            });
    }, [inventory, searchTerm]);

    // Close dropdown on click outside
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (!e.target.closest('.search-box-premium')) {
                setShowResults(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="invoice-page">
            <div className="invoice-left">

                <div className="card customer-card-premium glass">
                    <div className="card-header-minimal">
                        <User size={16} />
                        <span>CUSTOMER INFORMATION</span>
                    </div>
                    <div className="form-grid">
                        <div className="form-group">
                            <label>Mobile Number</label>
                            <div className={`input-with-icon ${lookupStatus}`}>
                                <Phone size={18} className="field-icon" />
                                <input
                                    type="tel"
                                    placeholder="Enter 10-digit mobile"
                                    value={customerPhone}
                                    maxLength={10}
                                    onChange={(e) => handlePhoneChange(e.target.value.replace(/\D/g, ''))}
                                />
                                {isLookingUp && <div className="loader-small"></div>}
                                {lookupStatus === 'found' && <Check className="status-icon success" size={16} />}
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Customer Name</label>
                            <div className="input-with-icon">
                                <User size={18} className="field-icon" />
                                <input
                                    type="text"
                                    placeholder="Enter customer name"
                                    value={customerName}
                                    onChange={(e) => setCustomerName(e.target.value)}
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label>Billing Type</label>
                            <div className="toggle-group-premium">
                                <button
                                    className={billingType === 'Retail' ? 'active' : ''}
                                    onClick={() => setBillingType('Retail')}
                                >Retail</button>
                                <button
                                    className={billingType === 'Wholesale' ? 'active' : ''}
                                    onClick={() => setBillingType('Wholesale')}
                                >Wholesale</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card items-card-premium glass">
                    <div className="table-header">
                        <div className="section-title">
                            <ShoppingBag size={18} />
                            <h3>Bill Items</h3>
                        </div>
                        <div className="search-box-premium">
                            <Search size={18} />
                            <input
                                type="text"
                                placeholder="Search vegetable..."
                                value={searchTerm}
                                onChange={(e) => {
                                    setSearchTerm(e.target.value);
                                    setShowResults(true);
                                }}
                                onFocus={() => setShowResults(true)}
                            />
                            {showResults && (
                                <div className="search-results-floating card glass">
                                    {filteredInventory.length > 0 ? (
                                        filteredInventory.map((veg, index) => (
                                            <div key={veg.id || index} className="search-item" onMouseDown={(e) => {
                                                e.stopPropagation();
                                                e.preventDefault();
                                                addItem(veg);
                                                setShowResults(false);
                                            }}>
                                                <div className="item-icon-circle">
                                                    <Store size={14} />
                                                </div>
                                                <div className="item-details">
                                                    <p className="primary-name">{veg.name}</p>
                                                    <p className="secondary-name">{veg.tamil_name || veg.tamilName}</p>
                                                </div>
                                                <div className="item-price-tag">
                                                    ₹{billingType === 'Wholesale'
                                                        ? (veg.wholesale_price || veg.wholesalePrice || veg.price || 0)
                                                        : (veg.retail_price || veg.retailPrice || veg.price || 0)}
                                                </div>
                                                <Plus size={16} className="add-plus" />
                                            </div>
                                        ))
                                    ) : (
                                        <div className="search-empty">No vegetables found</div>
                                    )}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="table-wrapper">
                        <table className="items-table-premium">
                            <thead>
                                <tr>
                                    <th className="col-name">Vegetable</th>
                                    <th className="col-price">Price/kg</th>
                                    <th className="col-qty">Quantity</th>
                                    <th className="col-total">Total</th>
                                    <th className="col-actions"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {items.map((item, index) => (
                                    <tr key={`${item.id}-${index}`} className="item-row">
                                        <td className="col-name">
                                            <div className="item-display">
                                                <div className="name-main">{item.name}</div>
                                                <div className="name-sub">{item.tamilName}</div>
                                            </div>
                                        </td>
                                        <td className="col-price">
                                            <div className="input-currency-box">
                                                <span className="currency">₹</span>
                                                <input
                                                    type="number"
                                                    value={item.price}
                                                    onChange={(e) => updatePrice(item.id, parseFloat(e.target.value) || 0)}
                                                    onFocus={(e) => e.target.select()}
                                                />
                                            </div>
                                        </td>
                                        <td className="col-qty">
                                            <div className="qty-stepper-premium">
                                                <button className="minus" onClick={() => updateQuantity(item.id, item.quantity - 0.25)}>-</button>
                                                <div className="qty-input-group">
                                                    <input
                                                        type="number"
                                                        value={item.quantity}
                                                        step="0.05"
                                                        onChange={(e) => updateQuantity(item.id, parseFloat(e.target.value))}
                                                        onFocus={(e) => e.target.select()}
                                                    />
                                                    <span className="unit">{item.quantity < 1 ? 'g' : 'kg'}</span>
                                                </div>
                                                <button className="plus" onClick={() => updateQuantity(item.id, item.quantity + 0.25)}>+</button>
                                            </div>
                                        </td>
                                        <td className="col-total">
                                            <div className="item-total-display">
                                                <span className="currency">₹</span>
                                                <input
                                                    type="number"
                                                    value={item.total}
                                                    onChange={(e) => updateItemTotal(item.id, parseFloat(e.target.value) || 0)}
                                                    onFocus={(e) => e.target.select()}
                                                />
                                            </div>
                                        </td>
                                        <td className="col-actions">
                                            <button className="delete-action" onClick={() => removeItem(item.id)}>
                                                <Trash2 size={16} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {items.length === 0 && (
                                    <tr>
                                        <td colSpan="5" className="empty-state">
                                            <div className="empty-content">
                                                <ShoppingBag size={48} />
                                                <p>Your cart is empty</p>
                                                <span>Search or select vegetables above to start billing</span>
                                            </div>
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div className="invoice-right">
                <div className="card summary-card-premium glass sticky-summary">
                    <div className="card-header-minimal">
                        <Store size={16} />
                        <span>BILL SUMMARY</span>
                    </div>

                    <div className="summary-list">
                        <div className="summary-item">
                            <span className="label">Items Count</span>
                            <span className="value-badge">{items.length}</span>
                        </div>
                        <div className="summary-item">
                            <span className="label">Subtotal</span>
                            <span className="value">₹{calculateSubtotal().toFixed(2)}</span>
                        </div>
                        <div className="summary-item">
                            <span className="label">Tax (0%)</span>
                            <span className="value">₹{calculateTax().toFixed(2)}</span>
                        </div>
                        <div className="summary-item discount-row">
                            <span className="label">Discount</span>
                            <div className="discount-input-premium">
                                <span>₹</span>
                                <input
                                    type="number"
                                    min="0"
                                    placeholder="Enter amount"
                                    value={discount}
                                    onChange={(e) => setDiscount(Math.max(0, parseFloat(e.target.value) || 0))}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="grand-total-section">
                        <div className="total-top">
                            <span className="total-label">Payable Amount</span>
                        </div>
                        <div className="total-value-main">
                            <span className="currency">₹</span>
                            <span className="amount">{calculateTotal().toFixed(2)}</span>
                        </div>
                    </div>

                    <div className="summary-actions">
                        <button
                            className="btn btn-primary-gradient full-width"
                            onClick={handleCreateBill}
                            disabled={loading || items.length === 0}
                        >
                            {loading ? 'Processing...' : 'Complete & Save'}
                            <Save size={18} />
                        </button>
                        <button
                            className="btn btn-outline-premium full-width"
                            onClick={() => setShowPreview(true)}
                            disabled={items.length === 0}
                        >
                            Print Preview
                            <Printer size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {showPreview && (
                <InvoicePreview
                    data={success && savedBill ? savedBill : {
                        customerName,
                        customerPhone,
                        billingType,
                        items,
                        subtotal: calculateSubtotal(),
                        taxAmount: calculateTax(),
                        discountAmount: discount,
                        grandTotal: calculateTotal()
                    }}
                    onClose={() => {
                        setShowPreview(false);
                        if (success) setSuccess(false);
                    }}
                />
            )}

            {success && (
                <div className="modal-overlay-premium blur">
                    <div className="card success-modal-premium glass">
                        <div className="success-header">
                            <div className="success-lottie-icon">
                                <Plus size={32} className="check-main" />
                            </div>
                            <h2>Bill Saved!</h2>
                            <p>Invoice <strong>#{savedBill?.billNumber || savedBill?.bill_number}</strong> recorded.</p>
                        </div>

                        <div className="modal-actions-list">
                            <button className="btn btn-primary-gradient" onClick={() => setShowPreview(true)}>
                                <Printer size={18} /> Print Invoice
                            </button>
                            <button className="btn btn-outline-premium" onClick={() => setSuccess(false)}>
                                <Plus size={18} /> New Bill
                            </button>
                            <button
                                className="btn btn-text-link"
                                onClick={() => {
                                    setSuccess(false);
                                    navigate('/invoices');
                                }}
                            >
                                View History <ArrowRight size={14} />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CreateInvoice;

