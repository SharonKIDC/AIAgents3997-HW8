// Tenant Management System - React Frontend

const { useState, useEffect } = React;

// API Base URL
const API_BASE = '';

// SVG Building Icon Component
function BuildingIcon({ size = 40, floors = 5, occupancyRate = 0, className = '' }) {
    const litWindows = Math.round((occupancyRate / 100) * (floors * 2));
    const windows = [];
    for (let f = 0; f < floors; f++) {
        for (let w = 0; w < 2; w++) {
            const idx = f * 2 + w;
            windows.push({ floor: f, window: w, lit: idx < litWindows });
        }
    }

    const height = 20 + floors * 12;
    const yOffset = 60 - height;

    return (
        <svg width={size} height={size} viewBox="0 0 60 60" className={className}>
            {/* Building shadow */}
            <ellipse cx="32" cy="58" rx="18" ry="3" fill="rgba(0,0,0,0.1)" />

            {/* Building body */}
            <rect x="12" y={yOffset} width="28" height={height} rx="2" fill="#374151" />

            {/* Roof detail */}
            <rect x="10" y={yOffset - 3} width="32" height="5" rx="1" fill="#4b5563" />
            <rect x="22" y={yOffset - 10} width="8" height="8" rx="1" fill="#6b7280" />

            {/* Windows */}
            {windows.map((w, i) => (
                <rect
                    key={i}
                    x={16 + w.window * 14}
                    y={yOffset + 6 + (floors - 1 - w.floor) * 12}
                    width="6"
                    height="8"
                    rx="1"
                    fill={w.lit ? "#fef08a" : "#1f2937"}
                    style={w.lit ? { filter: 'drop-shadow(0 0 2px rgba(253, 224, 71, 0.6))' } : {}}
                />
            ))}

            {/* Door */}
            <rect x="20" y={yOffset + height - 12} width="12" height="12" rx="1" fill="#1f2937" />
            <circle cx="29" cy={yOffset + height - 6} r="1" fill="#9ca3af" />
        </svg>
    );
}

// SVG Stats Icons
function StatsIcon({ type, className = '' }) {
    const icons = {
        buildings: (
            <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
                <path d="M12 2L2 7v15h20V7L12 2zm0 2.3L18.5 7 12 9.7 5.5 7 12 4.3zM4 8.6l7 3.1v9.3H4V8.6zm9 12.4v-9.3l7-3.1v12.4h-7z"/>
            </svg>
        ),
        apartments: (
            <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14H8v-4h4v4zm0-6H8V7h4v4zm6 6h-4v-4h4v4zm0-6h-4V7h4v4z"/>
            </svg>
        ),
        occupied: (
            <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
        ),
        vacant: (
            <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-7-2h2v-4h4v-2h-4V7h-2v4H8v2h4z" transform="rotate(45 12 12)"/>
            </svg>
        )
    };
    return icons[type] || null;
}

// Residential Complex Logo
function ComplexLogo({ className = '' }) {
    return (
        <svg viewBox="0 0 48 48" className={className} fill="currentColor">
            {/* Three buildings */}
            <rect x="4" y="24" width="10" height="22" rx="1" fill="currentColor" opacity="0.7"/>
            <rect x="19" y="12" width="10" height="34" rx="1" fill="currentColor"/>
            <rect x="34" y="20" width="10" height="26" rx="1" fill="currentColor" opacity="0.7"/>

            {/* Windows on center building */}
            <rect x="21" y="16" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="25" y="16" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="21" y="22" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="25" y="22" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="21" y="28" width="2" height="3" fill="white" opacity="0.5"/>
            <rect x="25" y="28" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="21" y="34" width="2" height="3" fill="white" opacity="0.8"/>
            <rect x="25" y="34" width="2" height="3" fill="white" opacity="0.5"/>

            {/* Roof details */}
            <rect x="22" y="6" width="4" height="6" rx="0.5" fill="currentColor"/>
        </svg>
    );
}

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
        { id: 'dashboard', label: 'Dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
        { id: 'tenants', label: 'Tenants', icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
        { id: 'register', label: 'Register', icon: 'M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z' },
        { id: 'query', label: 'AI Query', icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z' }
    ];

    return (
        <nav className="nav-gradient text-white shadow-xl">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo and Title */}
                    <div className="logo-container cursor-pointer" onClick={() => setCurrentView('dashboard')}>
                        <ComplexLogo className="w-10 h-10 text-white" />
                        <div>
                            <h1 className="text-lg font-bold leading-tight">Residential Complex</h1>
                            <p className="text-xs text-blue-200 leading-tight">Tenant Management</p>
                        </div>
                    </div>

                    {/* Navigation Items */}
                    <div className="flex space-x-1">
                        {navItems.map(item => (
                            <button
                                key={item.id}
                                onClick={() => setCurrentView(item.id)}
                                className={`nav-item px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                                    currentView === item.id
                                        ? 'bg-white/20 active'
                                        : 'hover:bg-white/10'
                                }`}
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d={item.icon} />
                                </svg>
                                <span className="hidden md:inline">{item.label}</span>
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
    const [selectedBuilding, setSelectedBuilding] = useState(null);

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

    function handleBuildingClick(buildingNumber) {
        setSelectedBuilding(buildingNumber);
    }

    if (loading) return <LoadingSpinner />;
    if (error) return <ErrorMessage message={error} />;

    const totalApartments = buildings.reduce((sum, b) => sum + b.total_apartments, 0);
    const totalOccupied = buildings.reduce((sum, b) => sum + (b.occupied || 0), 0);
    const totalVacant = totalApartments - totalOccupied;
    const occupancyRate = totalApartments > 0 ? ((totalOccupied / totalApartments) * 100).toFixed(1) : 0;

    return (
        <div className="space-y-6">
            {/* Dashboard Header */}
            <div className="dashboard-header text-center px-6">
                <div className="flex items-center justify-center gap-3 mb-2">
                    <ComplexLogo className="w-12 h-12 text-blue-600" />
                    <div>
                        <h2 className="text-3xl font-bold text-gray-800">Dashboard</h2>
                        <p className="text-sm text-gray-500">Residential Complex Overview</p>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                <StatCard title="Total Buildings" value={buildings.length} color="blue" />
                <StatCard title="Total Apartments" value={totalApartments} color="green" />
                <StatCard title="Occupied" value={totalOccupied} color="yellow" />
                <StatCard title="Vacant" value={totalVacant} color="red" />
            </div>

            {/* Overall Occupancy */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800">Overall Occupancy Rate</h3>
                        <p className="text-sm text-gray-500">Across all buildings</p>
                    </div>
                    <div className="text-right">
                        <span className={`text-4xl font-bold ${
                            occupancyRate >= 80 ? 'text-green-500' :
                            occupancyRate >= 50 ? 'text-yellow-500' :
                            'text-red-500'
                        }`}>{occupancyRate}%</span>
                    </div>
                </div>
                <div className="relative">
                    <div className="overflow-hidden h-4 rounded-full bg-gray-200">
                        <div
                            style={{ width: `${occupancyRate}%` }}
                            className={`occupancy-bar h-full rounded-full ${
                                occupancyRate >= 80 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                                occupancyRate >= 50 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                                'bg-gradient-to-r from-red-400 to-red-600'
                            }`}
                        />
                    </div>
                    {/* Tick marks */}
                    <div className="flex justify-between mt-1 text-xs text-gray-400">
                        <span>0%</span>
                        <span>25%</span>
                        <span>50%</span>
                        <span>75%</span>
                        <span>100%</span>
                    </div>
                </div>
            </div>

            {/* Buildings Grid */}
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                <div className="p-5 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-100 rounded-lg">
                            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                            </svg>
                        </div>
                        <div>
                            <h3 className="text-lg font-semibold text-gray-800">Buildings Overview</h3>
                            <p className="text-sm text-gray-500">Click on a building to view detailed floor map</p>
                        </div>
                    </div>
                </div>
                <div className="p-5">
                    {buildings.length === 0 ? (
                        <div className="text-center py-12">
                            <BuildingIcon size={80} floors={5} occupancyRate={0} className="mx-auto mb-4 opacity-30" />
                            <p className="text-gray-500">No buildings found</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                            {buildings.map(building => (
                                <BuildingCard
                                    key={building.number}
                                    building={building}
                                    onClick={handleBuildingClick}
                                />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Building Map Modal */}
            {selectedBuilding && (
                <BuildingMap
                    buildingNumber={selectedBuilding}
                    onClose={() => setSelectedBuilding(null)}
                />
            )}
        </div>
    );
}

function StatCard({ title, value, color, icon }) {
    const colorClasses = {
        blue: 'stat-card-blue',
        green: 'stat-card-green',
        yellow: 'stat-card-yellow',
        red: 'stat-card-red'
    };
    const iconTypes = {
        blue: 'buildings',
        green: 'apartments',
        yellow: 'occupied',
        red: 'vacant'
    };
    return (
        <div className={`${colorClasses[color]} rounded-xl shadow-lg p-6 text-white relative overflow-hidden`}>
            {/* Background decoration */}
            <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-8 -mt-8"></div>
            <div className="absolute bottom-0 left-0 w-16 h-16 bg-white/5 rounded-full -ml-6 -mb-6"></div>

            <div className="relative flex items-start justify-between">
                <div>
                    <h3 className="text-sm font-medium text-white/80">{title}</h3>
                    <p className="text-4xl font-bold mt-2">{value}</p>
                </div>
                <div className="stat-icon">
                    <StatsIcon type={iconTypes[color] || icon} className="w-6 h-6" />
                </div>
            </div>
        </div>
    );
}

function BuildingCard({ building, onClick }) {
    const occupied = building.occupied || 0;
    const total = building.total_apartments;
    const rate = total > 0 ? ((occupied / total) * 100).toFixed(0) : 0;
    const vacant = total - occupied;

    // Determine building size/floors based on apartment count
    const floors = Math.min(9, Math.ceil(total / 3));

    return (
        <div
            className="building-card bg-white p-5 cursor-pointer shadow-md"
            onClick={() => onClick && onClick(building.number)}
        >
            {/* Header with building number and icon */}
            <div className="flex items-start justify-between mb-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <span className="text-2xl font-bold text-gray-800">#{building.number}</span>
                        <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${
                            rate >= 80 ? 'bg-green-100 text-green-700' :
                            rate >= 50 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                        }`}>
                            {rate}%
                        </span>
                    </div>
                    <p className="text-sm text-gray-500">{total} apartments</p>
                </div>

                {/* Dynamic building icon showing occupancy */}
                <BuildingIcon size={60} floors={floors} occupancyRate={parseInt(rate)} />
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-green-50 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-green-600">{occupied}</p>
                    <p className="text-xs text-green-600/70">Occupied</p>
                </div>
                <div className="bg-gray-100 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-gray-500">{vacant}</p>
                    <p className="text-xs text-gray-500">Vacant</p>
                </div>
            </div>

            {/* Occupancy bar */}
            <div className="relative">
                <div className="overflow-hidden h-3 rounded-full bg-gray-200">
                    <div
                        style={{ width: `${rate}%` }}
                        className={`occupancy-bar h-full rounded-full transition-all duration-500 ${
                            rate >= 80 ? 'bg-gradient-to-r from-green-400 to-green-500' :
                            rate >= 50 ? 'bg-gradient-to-r from-yellow-400 to-yellow-500' :
                            'bg-gradient-to-r from-red-400 to-red-500'
                        }`}
                    />
                </div>
            </div>

            {/* Click hint */}
            <div className="mt-4 flex items-center justify-center gap-1 text-xs text-blue-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                View Floor Map
            </div>
        </div>
    );
}

// Building Floor Map Modal Component
function BuildingMap({ buildingNumber, onClose }) {
    const [floorData, setFloorData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [hoveredApartment, setHoveredApartment] = useState(null);

    useEffect(() => {
        loadFloorMap();
    }, [buildingNumber]);

    async function loadFloorMap() {
        try {
            setLoading(true);
            const data = await api.get(`/api/buildings/${buildingNumber}/floor-map`);
            setFloorData(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return (
            <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50">
                <div className="bg-white rounded-lg shadow-xl p-8">
                    <LoadingSpinner />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50">
                <div className="bg-white rounded-lg shadow-xl p-6 max-w-md">
                    <ErrorMessage message={error} />
                    <button onClick={onClose} className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg">Close</button>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
                {/* Header */}
                <div className="p-4 border-b flex items-center justify-between bg-blue-600 text-white">
                    <h3 className="text-xl font-semibold">Building {buildingNumber} - Floor Map</h3>
                    <button onClick={onClose} className="text-white hover:text-gray-200 text-2xl">&times;</button>
                </div>

                {/* Stats bar */}
                <div className="p-3 bg-gray-100 border-b flex items-center justify-around text-sm">
                    <span>Total Apartments: <strong>{floorData.total_apartments}</strong></span>
                    <span>Floors: <strong>{floorData.total_floors}</strong></span>
                    <span className="text-green-600">Occupied: <strong>{floorData.floors.reduce((sum, f) => sum + f.apartments.filter(a => a.tenant).length, 0)}</strong></span>
                    <span className="text-red-600">Vacant: <strong>{floorData.floors.reduce((sum, f) => sum + f.apartments.filter(a => !a.tenant).length, 0)}</strong></span>
                </div>

                {/* Floor visualization */}
                <div className="flex-1 overflow-y-auto p-4">
                    <div className="flex flex-col gap-2">
                        {floorData.floors.map(floor => (
                            <div key={floor.level} className="flex items-stretch border rounded-lg overflow-hidden">
                                {/* Floor label */}
                                <div className="w-20 bg-gray-700 text-white flex items-center justify-center font-bold shrink-0">
                                    {floor.level === 0 ? 'Ground' : `Floor ${floor.level}`}
                                </div>

                                {/* Apartments on this floor */}
                                <div className="flex-1 flex gap-2 p-2 bg-gray-50">
                                    {floor.apartments.map(apt => (
                                        <div
                                            key={apt.apartment_number}
                                            className={`relative flex-1 min-w-[100px] p-3 rounded-lg border-2 transition-all cursor-pointer ${
                                                apt.tenant
                                                    ? 'bg-green-100 border-green-400 hover:border-green-600'
                                                    : 'bg-gray-200 border-gray-300 hover:border-gray-400'
                                            }`}
                                            onMouseEnter={() => setHoveredApartment(apt)}
                                            onMouseLeave={() => setHoveredApartment(null)}
                                        >
                                            <div className="text-center">
                                                <div className="font-bold text-lg">#{apt.apartment_number}</div>
                                                {apt.tenant ? (
                                                    <div className="text-sm mt-1 truncate font-medium text-green-800">
                                                        {apt.tenant.last_name}
                                                    </div>
                                                ) : (
                                                    <div className="text-sm mt-1 text-gray-500">Vacant</div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Hover details panel */}
                <div className="p-4 border-t bg-gray-50 min-h-[120px]">
                    {hoveredApartment ? (
                        hoveredApartment.tenant ? (
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div>
                                    <span className="text-xs text-gray-500">Apartment</span>
                                    <p className="font-semibold">#{hoveredApartment.apartment_number}</p>
                                </div>
                                <div>
                                    <span className="text-xs text-gray-500">Tenant Name</span>
                                    <p className="font-semibold">{hoveredApartment.tenant.first_name} {hoveredApartment.tenant.last_name}</p>
                                </div>
                                <div>
                                    <span className="text-xs text-gray-500">Phone</span>
                                    <p className="font-semibold">{hoveredApartment.tenant.phone}</p>
                                </div>
                                <div>
                                    <span className="text-xs text-gray-500">Status</span>
                                    <p className={`font-semibold ${hoveredApartment.tenant.is_owner ? 'text-green-600' : 'text-blue-600'}`}>
                                        {hoveredApartment.tenant.is_owner ? 'Owner' : 'Renter'}
                                    </p>
                                </div>
                                <div>
                                    <span className="text-xs text-gray-500">Move-in Date</span>
                                    <p className="font-semibold">{hoveredApartment.tenant.move_in_date || 'N/A'}</p>
                                </div>
                                {hoveredApartment.tenant.storage_number && (
                                    <div>
                                        <span className="text-xs text-gray-500">Storage</span>
                                        <p className="font-semibold">#{hoveredApartment.tenant.storage_number}</p>
                                    </div>
                                )}
                                {(hoveredApartment.tenant.parking_slot_1 || hoveredApartment.tenant.parking_slot_2) && (
                                    <div>
                                        <span className="text-xs text-gray-500">Parking</span>
                                        <p className="font-semibold">
                                            {[hoveredApartment.tenant.parking_slot_1, hoveredApartment.tenant.parking_slot_2]
                                                .filter(Boolean)
                                                .map(p => `#${p}`)
                                                .join(', ')}
                                        </p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center text-gray-500">
                                <p className="font-semibold">Apartment #{hoveredApartment.apartment_number}</p>
                                <p>This apartment is vacant</p>
                            </div>
                        )
                    ) : (
                        <div className="text-center text-gray-400">
                            Hover over an apartment to see details
                        </div>
                    )}
                </div>

                {/* Legend */}
                <div className="p-3 border-t bg-white flex items-center justify-center gap-6 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-green-100 border-2 border-green-400 rounded"></div>
                        <span>Occupied</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-gray-200 border-2 border-gray-300 rounded"></div>
                        <span>Vacant</span>
                    </div>
                </div>
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
                            <FormInput label="Building" required error={fieldErrors.building_number}>
                                <select
                                    value={formData.building_number}
                                    onChange={(e) => setFormData({...formData, building_number: e.target.value})}
                                    className={inputClass('building_number')}
                                    required
                                >
                                    <option value="">Select Building</option>
                                    {buildings.map(b => (
                                        <option key={b.number} value={b.number}>Building {b.number}</option>
                                    ))}
                                </select>
                            </FormInput>
                            <FormInput label="Apartment Number" required error={fieldErrors.apartment_number}>
                                <input
                                    type="number"
                                    value={formData.apartment_number}
                                    onChange={(e) => setFormData({...formData, apartment_number: e.target.value})}
                                    className={inputClass('apartment_number')}
                                    required
                                    min="1"
                                />
                            </FormInput>
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

// AI Query Component
function AIQuery() {
    const [query, setQuery] = useState('');
    const [building, setBuilding] = useState('');
    const [buildings, setBuildings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        loadBuildings();
    }, []);

    async function loadBuildings() {
        try {
            const data = await api.get('/api/buildings');
            setBuildings(data.buildings || []);
        } catch (err) {
            console.error('Failed to load buildings:', err);
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setError(null);
        setResponse(null);

        try {
            const result = await api.post('/api/query', {
                query: query.trim(),
                building: building ? parseInt(building) : null
            });

            if (result.success) {
                setResponse(result.response);
                // Add to history
                setHistory(prev => [{
                    query: query.trim(),
                    response: result.response,
                    building: building || 'All',
                    timestamp: new Date().toLocaleTimeString()
                }, ...prev.slice(0, 9)]); // Keep last 10
            } else {
                setError(result.error || 'Failed to process query');
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    function handleExampleQuery(exampleQuery) {
        setQuery(exampleQuery);
    }

    const exampleQueries = [
        "How many tenants are currently registered?",
        "List all renters (non-owners)",
        "Show vacant apartments",
        "Which tenants moved in this year?",
        "Generate a contact list for all tenants"
    ];

    return (
        <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">AI-Powered Query</h2>

            {/* Query Form */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Ask a question about tenants
                        </label>
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="e.g., Show me all tenants who moved in during 2024"
                            className="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                            rows={3}
                            disabled={loading}
                        />
                    </div>

                    <div className="flex items-center gap-4 mb-4">
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Filter by Building (optional)
                            </label>
                            <select
                                value={building}
                                onChange={(e) => setBuilding(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                                disabled={loading}
                            >
                                <option value="">All Buildings</option>
                                {buildings.map(b => (
                                    <option key={b.number} value={b.number}>Building {b.number}</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex-shrink-0 pt-6">
                            <button
                                type="submit"
                                disabled={loading || !query.trim()}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                            >
                                {loading ? (
                                    <span className="flex items-center">
                                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Processing...
                                    </span>
                                ) : 'Ask AI'}
                            </button>
                        </div>
                    </div>

                    {/* Example queries */}
                    <div className="border-t pt-4">
                        <p className="text-sm text-gray-500 mb-2">Try these example queries:</p>
                        <div className="flex flex-wrap gap-2">
                            {exampleQueries.map((eq, idx) => (
                                <button
                                    key={idx}
                                    type="button"
                                    onClick={() => handleExampleQuery(eq)}
                                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition"
                                >
                                    {eq}
                                </button>
                            ))}
                        </div>
                    </div>
                </form>
            </div>

            {/* Error Display */}
            {error && (
                <div className="bg-red-100 text-red-700 px-4 py-3 rounded-lg mb-6">
                    <strong>Error:</strong> {error}
                </div>
            )}

            {/* Response Display */}
            {response && (
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-gray-800">AI Response</h3>
                        <button
                            onClick={() => navigator.clipboard.writeText(response)}
                            className="text-sm text-blue-600 hover:text-blue-800"
                        >
                            Copy to clipboard
                        </button>
                    </div>
                    <div className="prose max-w-none">
                        <div className="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap font-mono text-sm">
                            {response}
                        </div>
                    </div>
                </div>
            )}

            {/* Query History */}
            {history.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Queries</h3>
                    <div className="space-y-3">
                        {history.map((item, idx) => (
                            <div key={idx} className="border-b pb-3 last:border-0">
                                <div className="flex items-center justify-between text-sm text-gray-500 mb-1">
                                    <span>Building: {item.building}</span>
                                    <span>{item.timestamp}</span>
                                </div>
                                <p className="text-gray-800 font-medium">{item.query}</p>
                                <button
                                    onClick={() => {
                                        setQuery(item.query);
                                        setBuilding(item.building === 'All' ? '' : item.building);
                                    }}
                                    className="text-sm text-blue-600 hover:text-blue-800 mt-1"
                                >
                                    Re-run this query
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Info Box */}
            <div className="mt-6 bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-800 mb-2">About AI Query</h4>
                <p className="text-sm text-blue-700">
                    This feature uses AI to answer questions about your tenant data. You can ask
                    questions in natural language, and the system will analyze the current tenant
                    database to provide relevant answers. The AI has access to tenant names, contact
                    information, move-in dates, and building assignments.
                </p>
            </div>
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
            case 'query': return <AIQuery />;
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
                <footer className="footer-skyline bg-gray-800 text-white mt-8">
                    <div className="container mx-auto px-4 py-6">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <div className="flex items-center gap-3">
                                <ComplexLogo className="w-8 h-8 text-gray-400" />
                                <div>
                                    <p className="font-medium">Residential Complex</p>
                                    <p className="text-xs text-gray-400">Tenant Management System</p>
                                </div>
                            </div>
                            <div className="text-center text-sm text-gray-400">
                                Buildings 11, 13, 15, 17 - 82 Apartments
                            </div>
                            <div className="text-xs text-gray-500">
                                Powered by MCP Server
                            </div>
                        </div>
                    </div>
                </footer>
            </div>
        </ValidationConfigContext.Provider>
    );
}

// Render the app
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
