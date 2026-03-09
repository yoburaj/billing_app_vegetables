import React, { useRef, useMemo } from 'react';
import {
    X, Printer, Phone, MapPin, Mail, Calendar, Hash,
    User, ShoppingBag, CheckCircle2, CreditCard,
    Receipt, Clock
} from 'lucide-react';
import logo from '../assets/login_logo.png';
import { format } from 'date-fns';
import './InvoicePreview.css';

const numberToWords = (num) => {
    const a = ['', 'one ', 'two ', 'three ', 'four ', 'five ', 'six ', 'seven ', 'eight ', 'nine ', 'ten ', 'eleven ', 'twelve ', 'thirteen ', 'fourteen ', 'fifteen ', 'sixteen ', 'seventeen ', 'eighteen ', 'nineteen '];
    const b = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'];

    const inWords = (n) => {
        if ((n = n.toString()).length > 9) return 'overflow';
        let nArray = ('000000000' + n).substr(-9).match(/^(\d{2})(\d{2})(\d{2})(\d{1})(\d{2})$/);
        if (!nArray) return '';
        let str = '';
        str += (Number(nArray[1]) !== 0) ? (a[Number(nArray[1])] || b[nArray[1][0]] + ' ' + a[nArray[1][1]]) + 'crore ' : '';
        str += (Number(nArray[2]) !== 0) ? (a[Number(nArray[2])] || b[nArray[2][0]] + ' ' + a[nArray[2][1]]) + 'lakh ' : '';
        str += (Number(nArray[3]) !== 0) ? (a[Number(nArray[3])] || b[nArray[3][0]] + ' ' + a[nArray[3][1]]) + 'thousand ' : '';
        str += (Number(nArray[4]) !== 0) ? (a[Number(nArray[4])] || b[nArray[4][0]] + ' ' + a[nArray[4][1]]) + 'hundred ' : '';
        str += (Number(nArray[5]) !== 0) ? ((str !== '') ? 'and ' : '') + (a[Number(nArray[5])] || b[nArray[5][0]] + ' ' + a[nArray[5][1]]) : '';
        return str;
    };

    const amount = Math.floor(num);
    const paise = Math.round((num - amount) * 100);

    let res = inWords(amount) + 'rupees ';
    if (paise > 0) res += '& ' + inWords(paise) + 'paise ';
    return res.toUpperCase() + 'ONLY';
};

const InvoicePreview = ({ data, onClose }) => {
    const componentRef = useRef();

    const generationTime = useMemo(() => {
        const d = data?.date || data?.created_at;
        return d ? new Date(d) : new Date();
    }, [data?.date, data?.created_at]);

    const handlePrint = () => {
        window.print();
    };

    const {
        customerName,
        customerPhone,
        customerMobile,
        customer_mobile,
        billNumber = "DRAFT-001",
        date = new Date(),
        items = [],
        subtotal = 0,
        taxAmount = 0,
        discountAmount = 0,
        grandTotal = 0,
        billingType,
        mode,
        paymentStatus = "PAID"
    } = data;

    const displayPhone = customerPhone || customerMobile || customer_mobile || 'N/A';

    const displayShopName = "SUJI VEGETABLES";
    const displayType = billingType || mode || "Retail";

    return (
        <div className="preview-overlay">
            <div className="preview-container">
                <div className="preview-header-actions no-print">
                    <div className="title-section">
                        <div className="icon-badge">
                            <Receipt size={20} />
                        </div>
                        <div className="title-text">
                            <h2>Invoice Preview</h2>
                            <p className="subtitle">Professional standard bill format</p>
                        </div>
                    </div>
                    <div className="actions-right">
                        <button className="btn btn-outline" onClick={onClose}>
                            <X size={18} /> <span>Close</span>
                        </button>
                        <button className="btn btn-primary" onClick={handlePrint}>
                            <Printer size={18} /> <span>Print Invoice</span>
                        </button>
                    </div>
                </div>

                <div className="preview-body">
                    <div className="bill-paper" ref={componentRef}>
                        <div className="paper-accent"></div>
                        <div className="watermark-icon">
                            <img src={logo} alt="" className="watermark-logo-img" />
                        </div>

                        <div className="bill-header">
                            <div className="brand-section">
                                <div className="brand-logo brand-logo-img-container">
                                    <img src={logo} alt="Suji Vegetables" className="preview-logo-img" />
                                </div>
                                <div className="shop-info">
                                    <h1 className="shop-name">{displayShopName}</h1>
                                    <p className="shop-tagline">Premium Wholesale & Retail Vegetables</p>
                                    <div className="contact-details">
                                        <div className="detail-item">
                                            <MapPin size={14} color="#ff8d00" />
                                            <span>Pondy-Tindivanam Road, Kiliyanur</span>
                                        </div>
                                        <div className="detail-item">
                                            <Phone size={14} color="#ff8d00" />
                                            <span>+91 9095938085</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="invoice-meta">
                                <div className="meta-header">
                                    <span className="meta-label-top">INVOICE</span>
                                    <span className="type-badge">{displayType}</span>
                                </div>
                                <div className="meta-body">
                                    <div className="meta-row highlight">
                                        <span className="label">BILL NO:</span>
                                        <span className="value">#{billNumber}</span>
                                    </div>
                                    <div className="meta-row">
                                        <span className="label">DATE:</span>
                                        <span className="value">{format(new Date(date), 'dd MMM yyyy')}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="bill-to-section">
                            <div className="section-header">
                                <User size={14} color="#ff8d00" fill="#ff8d00" />
                                <h3>BILL TO</h3>
                            </div>
                            <div className="invoice-customer-card">
                                <p className="customer-name">{customerName || 'Walking Customer'}</p>
                                <p className="customer-phone" style={{ opacity: 0.6 }}>
                                    Contact: {displayPhone}
                                </p>
                            </div>
                        </div>

                        <div className="table-wrapper">
                            <table className="modern-table">
                                <thead>
                                    <tr>
                                        <th className="col-desc">Description</th>
                                        <th className="col-qty">Qty</th>
                                        <th className="col-rate">Rate</th>
                                        <th className="col-amt">Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items.map((item, index) => (
                                        <tr key={index}>
                                            <td className="col-desc">
                                                <span className="item-main">{item.name || item.vegetableName}</span>
                                                {(item.tamilName || item.tamil_name) && (
                                                    <span className="item-sub">{item.tamilName || item.tamil_name}</span>
                                                )}
                                            </td>
                                            <td className="col-qty">
                                                <span className="qty-val">
                                                    {item.quantity}kg
                                                </span>
                                            </td>
                                            <td className="col-rate">₹{(item.price || 0).toFixed(2)}</td>
                                            <td className="col-amt">₹{(item.total || 0).toFixed(2)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="summary-section">
                            <div className="terms-column">
                                <div className="status-seal">
                                    <div className="seal-content">
                                        <CheckCircle2 size={24} fill="#bbf7d0" />
                                        <span>{paymentStatus}</span>
                                    </div>
                                </div>
                                <div className="notes-box">
                                    <h4>Terms:</h4>
                                    <ul>
                                        <li>Items once sold cannot be returned.</li>
                                        <li>Prices inclusive of all taxes.</li>
                                        <li>Thank you for your business!</li>
                                    </ul>
                                </div>
                            </div>
                            <div className="calculation-column">
                                <div className="calc-row">
                                    <span style={{ fontWeight: 700, color: '#64748b' }}>SUBTOTAL</span>
                                    <span style={{ fontWeight: 800, color: '#0f172a' }}>₹{(subtotal).toFixed(2)}</span>
                                </div>
                                <div className="calc-row grand-total">
                                    <div className="total-label">
                                        <span className="main">Total Payable</span>
                                        <span className="words">{numberToWords(grandTotal)}</span>
                                    </div>
                                    <span className="total-value">₹{(grandTotal).toFixed(2)}</span>
                                </div>
                            </div>
                        </div>

                        <div className="bill-footer" style={{ marginTop: '2rem', border: 'none' }}>
                            <div className="system-stamp" style={{ justifyContent: 'center', opacity: 0.4 }}>
                                <span>POWERED BY VEGETABLE ERP V2.0 | OPTIMIZED LAYOUT</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default InvoicePreview;

