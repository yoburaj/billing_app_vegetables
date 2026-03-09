import React, { useEffect, useState } from 'react';
import {
    Package,
    Edit,
    RefreshCw,
    TrendingUp,
    AlertTriangle,
    Save,
    Plus,
    Trash2,
    X,
    Check,
    Search,
    ArrowLeft
} from 'lucide-react';
import { inventoryApi } from '../services/api';
import './Inventory.css';

const Inventory = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [editValues, setEditValues] = useState({});
    const [selectedItems, setSelectedItems] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [showLowStockOnly, setShowLowStockOnly] = useState(false);
    const LOW_STOCK_THRESHOLD = 5;

    // Add Item Modal State
    const [showAddModal, setShowAddModal] = useState(false);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [pendingDeleteItem, setPendingDeleteItem] = useState(null); // For single delete

    const [newItem, setNewItem] = useState({
        name: '',
        tamilName: '',
        tanglishName: '',
        category: 'Vegetables',
        price: 0,
        stock: 0,
        image: ''
    });

    useEffect(() => {
        fetchInventory();
    }, []);

    const PRIORITY_ORDER = ['Green Chili', 'Tomato', 'Onion', 'Potato', 'Green Beans', 'Carrot'];

    const filteredItems = items
        .filter(item => {
            const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (item.tamilName && item.tamilName.toLowerCase().includes(searchTerm.toLowerCase())) ||
                (item.tanglishName && item.tanglishName.toLowerCase().includes(searchTerm.toLowerCase()));
            const matchesStock = showLowStockOnly ? item.stock < LOW_STOCK_THRESHOLD : true;
            return matchesSearch && matchesStock;
        })
        .sort((a, b) => {
            const getPriorityIndex = (name) => {
                const n = name.toLowerCase();
                if (n.includes('green chili') || n.includes('green chilly') || n === 'green chilly' || n === 'green chili') return 0;
                if (n === 'tomato') return 1;
                if (n === 'onion') return 2;
                if (n === 'potato') return 3;
                if (n.includes('beans') || n === 'beans') return 4;
                if (n === 'carrot') return 5;
                return -1;
            };

            const indexA = getPriorityIndex(a.name);
            const indexB = getPriorityIndex(b.name);

            if (indexA !== -1 && indexB !== -1) return indexA - indexB;
            if (indexA !== -1) return -1;
            if (indexB !== -1) return 1;

            return a.name.localeCompare(b.name);
        });

    const lowStockItems = items.filter(item => item.stock < LOW_STOCK_THRESHOLD);


    const fetchInventory = async () => {
        setLoading(true);
        try {
            const response = await inventoryApi.getInventory();
            setItems(response.data);
            setSelectedItems([]);
        } catch (error) {
            console.error('Failed to fetch inventory:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (item) => {
        setEditingId(item.vegetableId);
        setEditValues({
            price: item.price,
            stock: item.stock,
            wholesalePrice: item.wholesalePrice,
            retailPrice: item.retailPrice
        });
    };

    const handleSave = async (id) => {
        try {
            await inventoryApi.updateItem(id, {
                price_per_kg: editValues.price,
                stock_kg: editValues.stock,
                wholesale_price: editValues.wholesalePrice,
                retail_price: editValues.retailPrice
            });
            setEditingId(null);
            fetchInventory();
        } catch (error) {
            console.error('Failed to update item:', error);
            alert('Error updating item');
        }
    };

    const handleDeleteClick = (item) => {
        setPendingDeleteItem(item);
        setShowDeleteModal(true);
    };

    const handleConfirmDelete = async () => {
        const itemsToDelete = pendingDeleteItem
            ? [pendingDeleteItem.vegetableId]
            : selectedItems;

        try {
            // Delete sequentially as there is no bulk delete endpoint yet
            for (const id of itemsToDelete) {
                await inventoryApi.deleteItem(id);
            }
            setShowDeleteModal(false);
            setPendingDeleteItem(null);
            fetchInventory();
        } catch (error) {
            console.error('Failed to delete item(s):', error);
            alert('Error deleting item(s)');
        }
    };

    const handleBulkDelete = () => {
        if (selectedItems.length === 0) return;
        setPendingDeleteItem(null);
        setShowDeleteModal(true);
    }

    const toggleSelect = (id) => {
        if (selectedItems.includes(id)) {
            setSelectedItems(selectedItems.filter(itemId => itemId !== id));
        } else {
            setSelectedItems([...selectedItems, id]);
        }
    };

    const toggleSelectAll = () => {
        if (selectedItems.length === items.length) {
            setSelectedItems([]);
        } else {
            setSelectedItems(items.map(item => item.vegetableId));
        }
    };

    const handleAddItem = async (e) => {
        e.preventDefault();
        try {
            // Use bulk-sync endpoint to add single item
            await inventoryApi.addItems({
                items: [newItem]
            });
            setShowAddModal(false);
            setNewItem({
                name: '',
                tamilName: '',
                tanglishName: '',
                category: 'Vegetables',
                price: 0,
                stock: 0,
                image: ''
            });
            fetchInventory();
        } catch (error) {
            console.error('Failed to add item:', error);
            alert('Error adding item');
        }
    };

    const isUpdatedToday = (updatedAt) => {
        if (!updatedAt) return false;
        try {
            const today = new Date();
            const updatedDate = new Date(updatedAt);
            return updatedDate.getDate() === today.getDate() &&
                updatedDate.getMonth() === today.getMonth() &&
                updatedDate.getFullYear() === today.getFullYear();
        } catch (e) {
            return false;
        }
    };

    return (
        <div className="inventory-container">
            <div className="inventory-header">
                <div className="header-info">
                    <div className="inventory-search-container">
                        <Search size={20} className="search-icon" />
                        <input
                            type="text"
                            placeholder="Search inventory..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>
                <div className="header-actions">
                    {showLowStockOnly && (
                        <button className="btn btn-outline" onClick={() => setShowLowStockOnly(false)}>
                            <ArrowLeft size={18} />
                            All Items
                        </button>
                    )}

                    {!showLowStockOnly && (
                        <button
                            className="btn btn-outline low-stock-btn"
                            onClick={() => setShowLowStockOnly(true)}
                        >
                            <AlertTriangle size={18} />
                            Low Stock {lowStockItems.length > 0 && <span className="count-badge">{lowStockItems.length}</span>}
                        </button>
                    )}
                    <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
                        <Plus size={18} />
                        Add Item
                    </button>
                    <button className="btn btn-outline" onClick={fetchInventory}>
                        <RefreshCw size={18} />
                    </button>
                </div>
            </div>

            {lowStockItems.length > 0 && !showLowStockOnly && (
                <div className="alert-banner warning">
                    <AlertTriangle size={20} />
                    <p><strong>Low Stock Alert:</strong> {lowStockItems.length} items are below {LOW_STOCK_THRESHOLD}kg. <button onClick={() => setShowLowStockOnly(true)}>View Items</button></p>
                </div>
            )}

            <div className="inventory-toolbar">
                <div className="selection-info">
                    <input
                        type="checkbox"
                        checked={items.length > 0 && selectedItems.length === items.length}
                        onChange={toggleSelectAll}
                    />
                    <span>{selectedItems.length > 0 ? `${selectedItems.length} Selected` : `Total items: ${items.length}`}</span>
                </div>
                {selectedItems.length > 0 && (
                    <button className="delete-btn" onClick={handleBulkDelete}>
                        <Trash2 size={16} /> Delete Selected
                    </button>
                )}
            </div>

            <div className="inventory-grid">
                {loading ? (
                    <p>Loading inventory...</p>
                ) : filteredItems.map(item => (
                    <div key={item.vegetableId} className={`card inventory-card ${selectedItems.includes(item.vegetableId) ? 'selected' : ''}`}>
                        <div className="card-select-overlay" onClick={() => toggleSelect(item.vegetableId)}>
                            {selectedItems.includes(item.vegetableId) && <div className="selected-check"><Check size={16} color="white" /></div>}
                        </div>

                        <div className="item-header">
                            <div className="item-img">{item.image ? <img src={item.image} alt={item.name} style={{ width: 30, height: 30, borderRadius: '50%' }} onError={(e) => e.target.style.display = 'none'} /> : '🥕'}</div>
                            <div className="item-title">
                                <h3>{item.name}</h3>
                                <span>{item.tamilName} {item.tanglishName && `(${item.tanglishName})`}</span>
                            </div>
                            <div className="card-actions" style={{ display: 'flex', gap: '5px' }}>
                                <button className="edit-icon" onClick={() => handleEdit(item)}>
                                    {editingId === item.vegetableId ? <Save size={18} onClick={() => handleSave(item.vegetableId)} /> : <Edit size={18} />}
                                </button>
                                <button className="delete-icon" onClick={() => handleDeleteClick(item)} style={{ color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer' }}>
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>

                        <div className="item-stats">
                            <div className="item-stat">
                                <label>Stock</label>
                                {editingId === item.vegetableId ? (
                                    <input
                                        type="number"
                                        value={editValues.stock}
                                        onChange={(e) => setEditValues({ ...editValues, stock: parseFloat(e.target.value) })}
                                    />
                                ) : (
                                    <div className="stock-display">
                                        <p className={item.stock < LOW_STOCK_THRESHOLD ? 'text-red' : ''}>{item.stock} kg</p>
                                        {item.stock < LOW_STOCK_THRESHOLD && <AlertTriangle size={14} className="warning-icon" />}
                                    </div>
                                )}
                            </div>
                            <div className="item-stat">
                                <label>Retail Price</label>
                                {editingId === item.vegetableId ? (
                                    <input
                                        type="number"
                                        value={editValues.retailPrice}
                                        onChange={(e) => setEditValues({ ...editValues, retailPrice: parseFloat(e.target.value) })}
                                    />
                                ) : (
                                    <p>₹{item.retailPrice}/kg</p>
                                )}
                            </div>
                            <div className="item-stat">
                                <label>Wholesale Price</label>
                                {editingId === item.vegetableId ? (
                                    <input
                                        type="number"
                                        value={editValues.wholesalePrice}
                                        onChange={(e) => setEditValues({ ...editValues, wholesalePrice: parseFloat(e.target.value) })}
                                    />
                                ) : (
                                    <p>₹{item.wholesalePrice}/kg</p>
                                )}
                            </div>
                        </div>

                        <div className="item-footer">
                            <div className={`trend ${isUpdatedToday(item.priceUpdatedAt) ? 'updated-today' : ''}`}>
                                {isUpdatedToday(item.priceUpdatedAt) ? (
                                    <>
                                        <Check size={14} />
                                        <span>Today rate updated</span>
                                    </>
                                ) : (
                                    <>
                                        <AlertTriangle size={14} />
                                        <span>Rate not updated today</span>
                                    </>
                                )}
                            </div>
                            <div className="category-tag">{item.category || 'General'}</div>
                        </div>
                    </div>
                ))}
            </div>

            {showAddModal && (
                <div className="modal-overlay">
                    <div className="card modal-content premium-modal">
                        <div className="modal-header">
                            <h2>Add New Item</h2>
                            <button className="close-modal" onClick={() => setShowAddModal(false)}>
                                <X size={20} />
                            </button>
                        </div>
                        <form onSubmit={handleAddItem}>
                            <div className="form-section">
                                <div className="form-row names-row">
                                    <div className="form-group">
                                        <label>Name (English)</label>
                                        <input
                                            type="text"
                                            value={newItem.name}
                                            onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                                            required
                                            placeholder="e.g. Tomato"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Name (Tamil)</label>
                                        <input
                                            type="text"
                                            value={newItem.tamilName}
                                            onChange={(e) => setNewItem({ ...newItem, tamilName: e.target.value })}
                                            placeholder="e.g. தக்காளி"
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Name (Tanglish)</label>
                                        <input
                                            type="text"
                                            value={newItem.tanglishName}
                                            onChange={(e) => setNewItem({ ...newItem, tanglishName: e.target.value })}
                                            placeholder="e.g. Thakkali"
                                        />
                                    </div>
                                </div>

                                <div className="form-row">
                                    <div className="form-group">
                                        <label>Price (₹/kg)</label>
                                        <input
                                            type="number"
                                            value={newItem.price}
                                            onChange={(e) => setNewItem({ ...newItem, price: parseFloat(e.target.value) })}
                                            onFocus={(e) => e.target.select()}
                                            required
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label>Initial Stock (kg)</label>
                                        <input
                                            type="number"
                                            value={newItem.stock}
                                            onChange={(e) => setNewItem({ ...newItem, stock: parseFloat(e.target.value) })}
                                            onFocus={(e) => e.target.select()}
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label>Category</label>
                                    <select
                                        value={newItem.category}
                                        onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                                    >
                                        <option value="Vegetables">Vegetables</option>
                                        <option value="Fruits">Fruits</option>
                                        <option value="Leafy">Leafy Greens</option>
                                    </select>
                                </div>

                                <div className="form-group">
                                    <label>Image URL</label>
                                    <input
                                        type="text"
                                        value={newItem.image}
                                        onChange={(e) => setNewItem({ ...newItem, image: e.target.value })}
                                        placeholder="https://..."
                                    />
                                </div>

                                <button type="submit" className="btn submit-btn">
                                    <Plus size={18} /> Add to Inventory
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {showDeleteModal && (
                <div className="modal-overlay">
                    <div className="card modal-content" style={{ maxWidth: '400px', textAlign: 'center' }}>
                        <div style={{ margin: '0 auto 15px', width: 60, height: 60, borderRadius: '50%', background: '#fee2e2', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Trash2 size={30} color="#ef4444" />
                        </div>
                        <h2>Delete Item?</h2>
                        <p style={{ color: '#666', marginBottom: '20px' }}>
                            {pendingDeleteItem
                                ? `Are you sure you want to delete "${pendingDeleteItem.name}"? This action cannot be undone.`
                                : `Are you sure you want to delete ${selectedItems.length} selected items? This action cannot be undone.`
                            }
                        </p>
                        <div className="modal-actions" style={{ justifyContent: 'center', gap: '10px', display: 'flex' }}>
                            <button className="btn btn-outline" onClick={() => setShowDeleteModal(false)}>Cancel</button>
                            <button className="btn btn-primary" style={{ backgroundColor: '#ef4444', borderColor: '#ef4444' }} onClick={handleConfirmDelete}>Confirm Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Inventory;
