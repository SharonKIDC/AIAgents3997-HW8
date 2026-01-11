// Tenant Management System - React Frontend

const { useState, useEffect } = React;

// API Base URL
const API_BASE = '';

// API helper functions
const api = {
    async get(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response.json();
    },
    async post(endpoint, data) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    },
    async put(endpoint, data) {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `API Error: ${response.status}`);
        }
        return response.json();
    },
    async delete(endpoint) {
        const response = await fetch(`${API_BASE}${endpoint}`, { method: 'DELETE' });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        return response.json();
    }
};

// Validation Config Context
const ValidationConfigContext = React.createContext(null);

function useValidationConfig() {
    return React.useContext(ValidationConfigContext);
}

// Navigation Component
function Navigation({ currentView, setCurrentView }) {
    const navItems = [
        { id: 'dashboard', label: 'Dashboard', icon: '📊' },
        { id: 'tenants', label: 'Tenants', icon: '👥' },
        { id: 'register', label: 'Register Tenant', icon: '➕' }
    ];

    return (
        <nav className="bg-blue-600 text-white shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    <h1 className="text-xl font-bold">Tenant Management System</h1>
                    <div className="flex space-x-4">
                        {navItems.map(item => (
                            <button
                                key={item.id}
                                onClick={() => setCurrentView(item.id)}
                                className={`px-4 py-2 rounded-lg transition ${
                                    currentView === item.id
                                        ? 'bg-blue-800'
                                        : 'hover:bg-blue-700'
                                }`}
                            >
                                {item.icon} {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </nav>
    );
}

// Dashboard Component
function Dashboard() {
    const [buildings, setBuildings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadBuildings();
    }, []);

    async function loadBuildings() {
        try {
            setLoading(true);
            const data = await api.get('/api/buildings');
            setBuildings(data.buildings || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} />;

    const totalApartments = buildings.reduce((sum, b) => sum + b.total_apartments, 0);
    const totalOccupied = buildings.reduce((sum, b) => sum + (b.occupied || 0), 0);
    const totalVacant = totalApartments - totalOccupied;
    const occupancyRate = totalApartments > 0 ? ((totalOccupied / totalApartments) * 100).toFixed(1) : 0;

    return (
        <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard title="Total Buildings" value={buildings.length} color="blue" />
                <StatCard title="Total Apartments" value={totalApartments} color="green" />
                <StatCard title="Occupied" value={totalOccupied} color="yellow" />
                <StatCard title="Vacant" value={totalVacant} color="red" />
            </div>
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Overall Occupancy Rate</h3>
                <div className="relative pt-1">
                    <div className="flex mb-2 items-center justify-between">
                        <span className="text-sm font-semibold text-blue-600">{occupancyRate}%</span>
                    </div>
                    <div className="overflow-hidden h-4 text-xs flex rounded bg-blue-100">
                        <div
                            style={{ width: `${occupancyRate}%` }}
                            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-500"
                        />
                    </div>
                </div>
            </div>
            <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b">
                    <h3 className="text-lg font-semibold">Buildings Overview</h3>
                </div>
                <div className="p-4">
                    {buildings.length === 0 ? (
                        <p className="text-gray-500 text-center py-4">No buildings found</p>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {buildings.map(building => (
                                <BuildingCard key={building.number} building={building} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function StatCard({ title, value, color }) {
    const colors = {
        blue: 'bg-blue-500',
        green: 'bg-green-500',
        yellow: 'bg-yellow-500',
        red: 'bg-red-500'
    };
    return (
        <div className={`${colors[color]} rounded-lg shadow p-6 text-white`}>
            <h3 className="text-sm font-medium opacity-80">{title}</h3>
            <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
    );
}

function BuildingCard({ building }) {
    const occupied = building.occupied || 0;
    const total = building.total_apartments;
    const rate = total > 0 ? ((occupied / total) * 100).toFixed(0) : 0;
    return (
        <div className="card bg-gray-50 rounded-lg p-4 border hover:shadow-md">
            <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-lg">Building {building.number}</h4>
                <span className="text-sm text-gray-500">{rate}% occupied</span>
            </div>
            <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                    <span className="text-gray-600">Total Apartments:</span>
                    <span className="font-medium">{total}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-600">Occupied:</span>
                    <span className="font-medium text-green-600">{occupied}</span>
                </div>
                <div className="flex justify-between">
                    <span className="text-gray-600">Vacant:</span>
                    <span className="font-medium text-red-600">{total - occupied}</span>
                </div>
            </div>
            <div className="mt-3 overflow-hidden h-2 rounded bg-gray-200">
                <div style={{ width: `${rate}%` }} className="h-full bg-blue-500 transition-all duration-300" />
            </div>
        </div>
    );
}

// Tenant List Component
function TenantList() {
    const [tenants, setTenants] = useState([]);
    const [buildings, setBuildings] = useState([]);
    const [selectedBuilding, setSelectedBuilding] = useState('all');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [editingTenant, setEditingTenant] = useState(null);

    useEffect(() => { loadData(); }, []);
    useEffect(() => { loadTenants(); }, [selectedBuilding]);

    async function loadData() {
        try {
            const buildingsData = await api.get('/api/buildings');
            setBuildings(buildingsData.buildings || []);
            await loadTenants();
        } catch (err) {
            setError(err.message);
        }
    }

    async function loadTenants() {
        try {
            setLoading(true);
            const endpoint = selectedBuilding === 'all' ? '/api/tenants' : `/api/tenants?building=${selectedBuilding}`;
            const data = await api.get(endpoint);
            setTenants(data.tenants || []);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    async function handleDelete(tenant) {
        if (!confirm(`Are you sure you want to remove ${tenant.first_name} ${tenant.last_name}?`)) return;
        try {
            await api.delete(`/api/tenants/${tenant.building_number}/${tenant.apartment_number}`);
            loadTenants();
        } catch (err) {
            alert(`Error: ${err.message}`);
        }
    }

    if (error) return <ErrorMessage message={error} />;

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-800">Tenants</h2>
                <select
                    value={selectedBuilding}
                    onChange={(e) => setSelectedBuilding(e.target.value)}
                    className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                    <option value="all">All Buildings</option>
                    {buildings.map(b => (
                        <option key={b.number} value={b.number}>Building {b.number}</option>
                    ))}
                </select>
            </div>
            {loading ? <LoadingSpinner /> : tenants.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">No tenants found</p>
                </div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Move-in</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {tenants.map((tenant, idx) => (
                                <tr key={idx} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className="font-medium">Bldg {tenant.building_number}</span>
                                        <span className="text-gray-500">, Apt {tenant.apartment_number}</span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">{tenant.first_name} {tenant.last_name}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">{tenant.phone}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 text-xs rounded-full ${tenant.is_owner ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`}>
                                            {tenant.is_owner ? 'Owner' : 'Renter'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-gray-500">{tenant.move_in_date || '-'}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                                        <button onClick={() => setEditingTenant(tenant)} className="text-blue-600 hover:text-blue-800 mr-3">Edit</button>
                                        <button onClick={() => handleDelete(tenant)} className="text-red-600 hover:text-red-800">Remove</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            {editingTenant && (
                <EditTenantModal tenant={editingTenant} onClose={() => setEditingTenant(null)} onSave={() => { setEditingTenant(null); loadTenants(); }} />
            )}
        </div>
    );
}

// Edit Tenant Modal
function EditTenantModal({ tenant, onClose, onSave }) {
    const [formData, setFormData] = useState({
        first_name: tenant.first_name,
        last_name: tenant.last_name,
        phone: tenant.phone,
        is_owner: tenant.is_owner,
        storage_number: tenant.storage_number || '',
        parking_slot_1: tenant.parking_slot_1 || '',
        parking_slot_2: tenant.parking_slot_2 || ''
    });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);

    async function handleSubmit(e) {
        e.preventDefault();
        setSaving(true);
        setError(null);
        try {
            await api.put(`/api/tenants/${tenant.building_number}/${tenant.apartment_number}`, formData);
            onSave();
        } catch (err) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
                <div className="p-4 border-b flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Edit Tenant</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">&times;</button>
                </div>
                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    {error && <ErrorMessage message={error} />}
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                            <input type="text" value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                            <input type="text" value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                        <input type="tel" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Storage #</label>
                            <input type="number" value={formData.storage_number} onChange={(e) => setFormData({...formData, storage_number: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Parking 1</label>
                            <input type="number" value={formData.parking_slot_1} onChange={(e) => setFormData({...formData, parking_slot_1: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Parking 2</label>
                            <input type="number" value={formData.parking_slot_2} onChange={(e) => setFormData({...formData, parking_slot_2: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" />
                        </div>
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                        <button type="button" onClick={onClose} className="px-4 py-2 border rounded-lg hover:bg-gray-50">Cancel</button>
                        <button type="submit" disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">{saving ? 'Saving...' : 'Save Changes'}</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Confirmation Modal for tenant replacement
function ConfirmationModal({ title, message, existingTenant, onConfirm, onCancel }) {
    return (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
                <div className="p-4 border-b">
                    <h3 className="text-lg font-semibold text-orange-600">{title}</h3>
                </div>
                <div className="p-4">
                    <p className="text-gray-700 mb-4">{message}</p>
                    {existingTenant && (
                        <div className="bg-gray-50 rounded-lg p-4 mb-4">
                            <h4 className="font-medium text-gray-800 mb-2">Current Tenant:</h4>
                            <p><span className="text-gray-600">Name:</span> {existingTenant.first_name} {existingTenant.last_name}</p>
                            <p><span className="text-gray-600">Phone:</span> {existingTenant.phone}</p>
                            <p><span className="text-gray-600">Move-in:</span> {existingTenant.move_in_date || 'N/A'}</p>
                        </div>
                    )}
                    <p className="text-sm text-gray-500">The existing tenant will be moved to history with their move-out date set to one day before the new tenant's move-in date.</p>
                </div>
                <div className="p-4 border-t flex justify-end space-x-3">
                    <button onClick={onCancel} className="px-4 py-2 border rounded-lg hover:bg-gray-50">Cancel</button>
                    <button onClick={onConfirm} className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">Replace Tenant</button>
                </div>
            </div>
        </div>
    );
}

// Field Error Display Component
function FieldError({ errors }) {
    if (!errors || errors.length === 0) return null;
    return (
        <div className="mt-1 text-sm text-red-600">
            {errors.map((error, idx) => (
                <div key={idx}>{error}</div>
            ))}
        </div>
    );
}

// Form Input with Error Support
function FormInput({ label, required, error, children }) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
                {label} {required && '*'}
            </label>
            {children}
            <FieldError errors={error} />
        </div>
    );
}

// Family Members List Component - NEW DESIGN with checkboxes
function FamilyMembersSection({ members, setMembers, mainTenant, validationConfig, errors }) {
    const [newMember, setNewMember] = useState({
        first_name: '',
        last_name: '',
        phone: '',
        whatsapp_enabled: false,
        palgate_enabled: false,
        vehicle_plate: ''
    });

    const familyConfig = validationConfig?.family_members || {
        max_whatsapp_members: 2,
        max_palgate_members: 4,
        main_tenant_always_included: true
    };

    // Count enabled members (excluding main tenant)
    const whatsappCount = members.filter(m => m.whatsapp_enabled).length;
    const palgateCount = members.filter(m => m.palgate_enabled).length;

    function addMember() {
        if (!newMember.first_name || !newMember.phone) return;
        setMembers([...members, { ...newMember }]);
        setNewMember({
            first_name: '',
            last_name: '',
            phone: '',
            whatsapp_enabled: false,
            palgate_enabled: false,
            vehicle_plate: ''
        });
    }

    function removeMember(index) {
        setMembers(members.filter((_, i) => i !== index));
    }

    function toggleWhatsapp(index) {
        const member = members[index];
        if (!member.whatsapp_enabled && whatsappCount >= familyConfig.max_whatsapp_members) {
            return; // Can't add more
        }
        const updated = [...members];
        updated[index] = { ...member, whatsapp_enabled: !member.whatsapp_enabled };
        setMembers(updated);
    }

    function togglePalgate(index) {
        const member = members[index];
        if (!member.palgate_enabled && palgateCount >= familyConfig.max_palgate_members) {
            return; // Can't add more
        }
        const updated = [...members];
        updated[index] = { ...member, palgate_enabled: !member.palgate_enabled };
        setMembers(updated);
    }

    function updateVehiclePlate(index, plate) {
        const updated = [...members];
        updated[index] = { ...updated[index], vehicle_plate: plate };
        setMembers(updated);
    }

    return (
        <div className="border rounded-lg p-4">
            <h4 className="font-medium text-gray-800 mb-2">Family Members</h4>
            <p className="text-sm text-gray-500 mb-4">
                Add family members for WhatsApp group and/or PalGate access.
                Main tenant is always included in both.
            </p>

            {/* Limits info */}
            <div className="bg-blue-50 rounded p-3 mb-4 text-sm">
                <div className="flex justify-between">
                    <span>WhatsApp group: {whatsappCount + 1}/{familyConfig.max_whatsapp_members + 1} members</span>
                    <span>PalGate access: {palgateCount + 1}/{familyConfig.max_palgate_members + 1} members</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">(+1 includes main tenant who is always enabled)</div>
            </div>

            {errors && <FieldError errors={errors} />}

            {/* Member list header */}
            <div className="bg-gray-100 rounded-t p-2 grid grid-cols-12 gap-2 text-xs font-medium text-gray-600 border-b">
                <div className="col-span-3">Name</div>
                <div className="col-span-2">Phone</div>
                <div className="col-span-2 text-center">WhatsApp</div>
                <div className="col-span-2 text-center">PalGate</div>
                <div className="col-span-2">Vehicle Plate</div>
                <div className="col-span-1"></div>
            </div>

            {/* Main tenant row (always first, always enabled) */}
            {mainTenant.first_name && (
                <div className="bg-green-50 border-l-4 border-green-500 p-2 grid grid-cols-12 gap-2 items-center text-sm">
                    <div className="col-span-3 font-medium">
                        {mainTenant.first_name} {mainTenant.last_name}
                        <span className="text-xs text-green-600 ml-1">(Main)</span>
                    </div>
                    <div className="col-span-2 text-gray-600">{mainTenant.phone}</div>
                    <div className="col-span-2 text-center">
                        <input type="checkbox" checked disabled className="w-4 h-4 text-blue-600 cursor-not-allowed" />
                    </div>
                    <div className="col-span-2 text-center">
                        <input type="checkbox" checked disabled className="w-4 h-4 text-blue-600 cursor-not-allowed" />
                    </div>
                    <div className="col-span-2 text-gray-400">-</div>
                    <div className="col-span-1"></div>
                </div>
            )}

            {/* Family member rows */}
            {members.map((member, idx) => (
                <div key={idx} className="border-b p-2 grid grid-cols-12 gap-2 items-center text-sm hover:bg-gray-50">
                    <div className="col-span-3">
                        {member.first_name} {member.last_name}
                    </div>
                    <div className="col-span-2 text-gray-600">{member.phone}</div>
                    <div className="col-span-2 text-center">
                        <input
                            type="checkbox"
                            checked={member.whatsapp_enabled}
                            onChange={() => toggleWhatsapp(idx)}
                            disabled={!member.whatsapp_enabled && whatsappCount >= familyConfig.max_whatsapp_members}
                            className="w-4 h-4 text-blue-600 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                        />
                    </div>
                    <div className="col-span-2 text-center">
                        <input
                            type="checkbox"
                            checked={member.palgate_enabled}
                            onChange={() => togglePalgate(idx)}
                            disabled={!member.palgate_enabled && palgateCount >= familyConfig.max_palgate_members}
                            className="w-4 h-4 text-blue-600 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50"
                        />
                    </div>
                    <div className="col-span-2">
                        {member.palgate_enabled ? (
                            <input
                                type="text"
                                value={member.vehicle_plate || ''}
                                onChange={(e) => updateVehiclePlate(idx, e.target.value)}
                                placeholder="Plate #"
                                className="w-full px-2 py-1 border rounded text-xs"
                            />
                        ) : (
                            <span className="text-gray-400">-</span>
                        )}
                    </div>
                    <div className="col-span-1 text-right">
                        <button
                            type="button"
                            onClick={() => removeMember(idx)}
                            className="text-red-500 hover:text-red-700 text-lg"
                        >
                            &times;
                        </button>
                    </div>
                </div>
            ))}

            {/* Add new member form */}
            <div className="mt-4 border-t pt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Add Family Member:</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    <input
                        type="text"
                        placeholder="First Name *"
                        value={newMember.first_name}
                        onChange={(e) => setNewMember({...newMember, first_name: e.target.value})}
                        className="px-3 py-2 border rounded-lg text-sm"
                    />
                    <input
                        type="text"
                        placeholder="Last Name"
                        value={newMember.last_name}
                        onChange={(e) => setNewMember({...newMember, last_name: e.target.value})}
                        className="px-3 py-2 border rounded-lg text-sm"
                    />
                    <input
                        type="tel"
                        placeholder="Phone *"
                        value={newMember.phone}
                        onChange={(e) => setNewMember({...newMember, phone: e.target.value})}
                        className="px-3 py-2 border rounded-lg text-sm"
                    />
                    <button
                        type="button"
                        onClick={addMember}
                        disabled={!newMember.first_name || !newMember.phone}
                        className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                    >
                        + Add Member
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                    After adding, use checkboxes to enable WhatsApp/PalGate access for each member.
                </p>
            </div>
        </div>
    );
}

// Tenant Registration Form
function TenantRegistration({ onSuccess }) {
    const validationConfig = useValidationConfig();
    const [buildings, setBuildings] = useState([]);
    const [formData, setFormData] = useState({
        building_number: '',
        apartment_number: '',
        first_name: '',
        last_name: '',
        phone: '',
        is_owner: true,
        owner_info: { first_name: '', last_name: '', phone: '' },
        move_in_date: new Date().toISOString().split('T')[0],
        storage_number: '',
        parking_slot_1: '',
        parking_slot_2: '',
        family_members: []
    });
    const [loading, setLoading] = useState(false);
    const [fieldErrors, setFieldErrors] = useState({});
    const [generalError, setGeneralError] = useState(null);
    const [success, setSuccess] = useState(false);
    const [confirmReplace, setConfirmReplace] = useState(null);

    useEffect(() => { loadBuildings(); }, []);

    async function loadBuildings() {
        try {
            const data = await api.get('/api/buildings');
            setBuildings(data.buildings || []);
            if (data.buildings?.length > 0) {
                setFormData(f => ({ ...f, building_number: data.buildings[0].number }));
            }
        } catch (err) {
            setGeneralError(err.message);
        }
    }

    // Client-side validation
    function validateForm() {
        const errors = {};
        const nameConfig = validationConfig?.name || { min_length: 2, max_length: 50 };
        const phoneConfig = validationConfig?.phone || { min_length: 9, max_length: 15 };
        const familyConfig = validationConfig?.family_members || { max_whatsapp_members: 2, max_palgate_members: 4 };

        // Validate tenant name
        if (formData.first_name.length < nameConfig.min_length) {
            errors.first_name = [`First name must be at least ${nameConfig.min_length} characters`];
        }
        if (formData.last_name.length < nameConfig.min_length) {
            errors.last_name = [`Last name must be at least ${nameConfig.min_length} characters`];
        }

        // Validate phone
        if (formData.phone.length < phoneConfig.min_length) {
            errors.phone = [`Phone must be at least ${phoneConfig.min_length} characters`];
        }

        // Validate owner info for renters
        if (!formData.is_owner) {
            if (!formData.owner_info.first_name || formData.owner_info.first_name.length < nameConfig.min_length) {
                errors.owner_first_name = [`Owner first name must be at least ${nameConfig.min_length} characters`];
            }
            if (!formData.owner_info.last_name || formData.owner_info.last_name.length < nameConfig.min_length) {
                errors.owner_last_name = [`Owner last name must be at least ${nameConfig.min_length} characters`];
            }
            if (!formData.owner_info.phone || formData.owner_info.phone.length < phoneConfig.min_length) {
                errors.owner_phone = [`Owner phone must be at least ${phoneConfig.min_length} characters`];
            }
        }

        // Validate family member limits
        const whatsappCount = formData.family_members.filter(m => m.whatsapp_enabled).length;
        const palgateCount = formData.family_members.filter(m => m.palgate_enabled).length;

        if (whatsappCount > familyConfig.max_whatsapp_members) {
            errors.family_members = errors.family_members || [];
            errors.family_members.push(`Maximum ${familyConfig.max_whatsapp_members} additional WhatsApp members allowed`);
        }
        if (palgateCount > familyConfig.max_palgate_members) {
            errors.family_members = errors.family_members || [];
            errors.family_members.push(`Maximum ${familyConfig.max_palgate_members} additional PalGate members allowed`);
        }

        return errors;
    }

    async function handleSubmit(e, replaceExisting = false) {
        if (e) e.preventDefault();

        // Client-side validation first
        const clientErrors = validateForm();
        if (Object.keys(clientErrors).length > 0) {
            setFieldErrors(clientErrors);
            return;
        }

        setLoading(true);
        setFieldErrors({});
        setGeneralError(null);
        setSuccess(false);

        try {
            const payload = {
                building_number: parseInt(formData.building_number),
                apartment_number: parseInt(formData.apartment_number),
                first_name: formData.first_name,
                last_name: formData.last_name,
                phone: formData.phone,
                is_owner: formData.is_owner,
                move_in_date: formData.move_in_date,
                storage_number: formData.storage_number ? parseInt(formData.storage_number) : null,
                parking_slot_1: formData.parking_slot_1 ? parseInt(formData.parking_slot_1) : null,
                parking_slot_2: formData.parking_slot_2 ? parseInt(formData.parking_slot_2) : null,
                family_members: formData.family_members,
                replace_existing: replaceExisting
            };

            // Add owner info if renter
            if (!formData.is_owner) {
                payload.owner_info = formData.owner_info;
            }

            const result = await api.post('/api/tenants', payload);

            // Check if confirmation is needed
            if (result.requires_confirmation) {
                setConfirmReplace(result);
                setLoading(false);
                return;
            }

            // Check for validation errors from server
            if (!result.success && result.validation_errors) {
                setFieldErrors(result.validation_errors);
                if (result.validation_errors._general) {
                    setGeneralError(result.validation_errors._general.join(', '));
                }
                setLoading(false);
                return;
            }

            if (result.success) {
                setSuccess(true);
                resetForm();
                if (onSuccess) onSuccess();
            }
        } catch (err) {
            setGeneralError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function resetForm() {
        setFormData({
            building_number: formData.building_number,
            apartment_number: '',
            first_name: '',
            last_name: '',
            phone: '',
            is_owner: true,
            owner_info: { first_name: '', last_name: '', phone: '' },
            move_in_date: new Date().toISOString().split('T')[0],
            storage_number: '',
            parking_slot_1: '',
            parking_slot_2: '',
            family_members: []
        });
        setFieldErrors({});
    }

    function handleConfirmReplace() {
        setConfirmReplace(null);
        handleSubmit(null, true);
    }

    const inputClass = (fieldName) => {
        const hasError = fieldErrors[fieldName];
        return `w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${hasError ? 'border-red-500 bg-red-50' : ''}`;
    };

    return (
        <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Register New Tenant</h2>

            <div className="bg-white rounded-lg shadow p-6">
                {generalError && <ErrorMessage message={generalError} />}
                {success && (
                    <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-lg">
                        Tenant registered successfully!
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Location Section */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Location</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Building *</label>
                                <select
                                    value={formData.building_number}
                                    onChange={(e) => setFormData({...formData, building_number: e.target.value})}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    required
                                >
                                    <option value="">Select Building</option>
                                    {buildings.map(b => (
                                        <option key={b.number} value={b.number}>Building {b.number}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Apartment Number *</label>
                                <input
                                    type="number"
                                    value={formData.apartment_number}
                                    onChange={(e) => setFormData({...formData, apartment_number: e.target.value})}
                                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                    required
                                    min="1"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Tenant Type Selection */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Tenant Type</h3>
                        <div className="flex items-center space-x-6">
                            <label className="flex items-center space-x-2 cursor-pointer">
                                <input
                                    type="radio"
                                    checked={formData.is_owner}
                                    onChange={() => setFormData({...formData, is_owner: true})}
                                    className="text-blue-600 w-4 h-4"
                                />
                                <span className="text-sm font-medium text-gray-700">Owner (lives in property)</span>
                            </label>
                            <label className="flex items-center space-x-2 cursor-pointer">
                                <input
                                    type="radio"
                                    checked={!formData.is_owner}
                                    onChange={() => setFormData({...formData, is_owner: false})}
                                    className="text-blue-600 w-4 h-4"
                                />
                                <span className="text-sm font-medium text-gray-700">Renter</span>
                            </label>
                        </div>
                    </div>

                    {/* Tenant Personal Info */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Tenant Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <FormInput label="First Name" required error={fieldErrors.first_name}>
                                <input
                                    type="text"
                                    value={formData.first_name}
                                    onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                                    className={inputClass('first_name')}
                                    required
                                />
                            </FormInput>
                            <FormInput label="Last Name" required error={fieldErrors.last_name}>
                                <input
                                    type="text"
                                    value={formData.last_name}
                                    onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                                    className={inputClass('last_name')}
                                    required
                                />
                            </FormInput>
                        </div>
                        <div className="mt-4">
                            <FormInput label="Phone" required error={fieldErrors.phone}>
                                <input
                                    type="tel"
                                    value={formData.phone}
                                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                                    className={inputClass('phone')}
                                    required
                                    placeholder="e.g., 050-1234567"
                                />
                            </FormInput>
                        </div>
                    </div>

                    {/* Owner Info (only for renters) */}
                    {!formData.is_owner && (
                        <div className="border-b pb-4 bg-yellow-50 -mx-6 px-6 py-4">
                            <h3 className="text-lg font-medium mb-4 text-yellow-800">Owner Information (Required for Renters)</h3>
                            {fieldErrors.owner_info && <FieldError errors={fieldErrors.owner_info} />}
                            <div className="grid grid-cols-2 gap-4">
                                <FormInput label="Owner First Name" required error={fieldErrors.owner_first_name}>
                                    <input
                                        type="text"
                                        value={formData.owner_info.first_name}
                                        onChange={(e) => setFormData({...formData, owner_info: {...formData.owner_info, first_name: e.target.value}})}
                                        className={inputClass('owner_first_name')}
                                        required
                                    />
                                </FormInput>
                                <FormInput label="Owner Last Name" required error={fieldErrors.owner_last_name}>
                                    <input
                                        type="text"
                                        value={formData.owner_info.last_name}
                                        onChange={(e) => setFormData({...formData, owner_info: {...formData.owner_info, last_name: e.target.value}})}
                                        className={inputClass('owner_last_name')}
                                        required
                                    />
                                </FormInput>
                            </div>
                            <div className="mt-4">
                                <FormInput label="Owner Phone" required error={fieldErrors.owner_phone}>
                                    <input
                                        type="tel"
                                        value={formData.owner_info.phone}
                                        onChange={(e) => setFormData({...formData, owner_info: {...formData.owner_info, phone: e.target.value}})}
                                        className={inputClass('owner_phone')}
                                        required
                                        placeholder="e.g., 050-1234567"
                                    />
                                </FormInput>
                            </div>
                        </div>
                    )}

                    {/* Move-in Date */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Move-in Details</h3>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Move-in Date *</label>
                            <input type="date" value={formData.move_in_date} onChange={(e) => setFormData({...formData, move_in_date: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" required />
                        </div>
                    </div>

                    {/* Assignments */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Assignments (Optional)</h3>
                        <div className="grid grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Storage Number</label>
                                <input type="number" value={formData.storage_number} onChange={(e) => setFormData({...formData, storage_number: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" min="1" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Parking Slot 1</label>
                                <input type="number" value={formData.parking_slot_1} onChange={(e) => setFormData({...formData, parking_slot_1: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" min="1" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Parking Slot 2</label>
                                <input type="number" value={formData.parking_slot_2} onChange={(e) => setFormData({...formData, parking_slot_2: e.target.value})} className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500" min="1" />
                            </div>
                        </div>
                    </div>

                    {/* Family Members - NEW DESIGN */}
                    <div className="border-b pb-4">
                        <h3 className="text-lg font-medium mb-4">Family Members</h3>
                        <FamilyMembersSection
                            members={formData.family_members}
                            setMembers={(m) => setFormData({...formData, family_members: m})}
                            mainTenant={{
                                first_name: formData.first_name,
                                last_name: formData.last_name,
                                phone: formData.phone
                            }}
                            validationConfig={validationConfig}
                            errors={fieldErrors.family_members}
                        />
                    </div>

                    {/* Submit */}
                    <div className="flex justify-end pt-4">
                        <button type="submit" disabled={loading} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium">
                            {loading ? 'Registering...' : 'Register Tenant'}
                        </button>
                    </div>
                </form>
            </div>

            {/* Confirmation Modal */}
            {confirmReplace && (
                <ConfirmationModal
                    title="Apartment Already Occupied"
                    message={confirmReplace.message}
                    existingTenant={confirmReplace.existing_tenant}
                    onConfirm={handleConfirmReplace}
                    onCancel={() => setConfirmReplace(null)}
                />
            )}
        </div>
    );
}

// Loading Spinner Component
function LoadingSpinner() {
    return (
        <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
    );
}

// Error Message Component
function ErrorMessage({ message }) {
    return (
        <div className="bg-red-100 text-red-700 px-4 py-3 rounded-lg mb-4">
            {message}
        </div>
    );
}

// Main App Component
function App() {
    const [currentView, setCurrentView] = useState('dashboard');
    const [validationConfig, setValidationConfig] = useState(null);

    // Fetch validation config on mount
    useEffect(() => {
        async function fetchConfig() {
            try {
                const config = await api.get('/api/config/validation');
                setValidationConfig(config);
            } catch (err) {
                console.error('Failed to load validation config:', err);
            }
        }
        fetchConfig();
    }, []);

    function renderView() {
        switch (currentView) {
            case 'dashboard': return <Dashboard />;
            case 'tenants': return <TenantList />;
            case 'register': return <TenantRegistration onSuccess={() => setCurrentView('tenants')} />;
            default: return <Dashboard />;
        }
    }

    return (
        <ValidationConfigContext.Provider value={validationConfig}>
            <div className="min-h-screen bg-gray-100">
                <Navigation currentView={currentView} setCurrentView={setCurrentView} />
                <main className="container mx-auto px-4 py-8">
                    {renderView()}
                </main>
                <footer className="bg-gray-800 text-white py-4 mt-8">
                    <div className="container mx-auto px-4 text-center text-sm">
                        Tenant Management System - Residential Complex Administration
                    </div>
                </footer>
            </div>
        </ValidationConfigContext.Provider>
    );
}

// Render the app
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
