import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const GOOGLE_MAPS_API_KEY = "AIzaSyDW2kVAelPvl8EZORFSagOaJNQZSvSSTQM";

// Add Google Maps script
const loadGoogleMapsScript = () => {
  return new Promise((resolve) => {
    if (window.google && window.google.maps) {
      resolve();
      return;
    }
    
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&libraries=geometry`;
    script.async = true;
    script.defer = true;
    script.onload = resolve;
    document.head.appendChild(script);
  });
};

const Map = ({ translocations, filteredTranslocations }) => {
  useEffect(() => {
    loadGoogleMapsScript().then(() => {
      const map = new window.google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: { lat: -15, lng: 25 }, // Center on Africa
        mapTypeId: 'terrain'
      });

      const bounds = new window.google.maps.LatLngBounds();

      // Species colors
      const speciesColors = {
        elephant: '#FF6B6B',
        rhino: '#4ECDC4',
        lion: '#45B7D1',
        cheetah: '#96CEB4',
        buffalo: '#FECA57',
        giraffe: '#FF9FF3',
        zebra: '#A55A3C',
        other: '#95A5A6'
      };

      // Transport mode icons
      const getTransportIcon = (mode) => {
        return mode === 'air' ? '✈️' : '🚛';
      };

      filteredTranslocations.forEach((translocation) => {
        const sourceLatLng = new window.google.maps.LatLng(
          translocation.source_reserve.latitude,
          translocation.source_reserve.longitude
        );
        const destLatLng = new window.google.maps.LatLng(
          translocation.recipient_reserve.latitude,
          translocation.recipient_reserve.longitude
        );

        // Source marker
        const sourceMarker = new window.google.maps.Marker({
          position: sourceLatLng,
          map: map,
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: speciesColors[translocation.species],
            fillOpacity: 0.8,
            strokeColor: '#ffffff',
            strokeWeight: 2
          },
          title: `Source: ${translocation.source_reserve.name}`
        });

        // Destination marker
        const destMarker = new window.google.maps.Marker({
          position: destLatLng,
          map: map,
          icon: {
            path: window.google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: speciesColors[translocation.species],
            fillOpacity: 1,
            strokeColor: '#000000',
            strokeWeight: 2
          },
          title: `Destination: ${translocation.recipient_reserve.name}`
        });

        // Connection line
        const flightPath = new window.google.maps.Polyline({
          path: [sourceLatLng, destLatLng],
          geodesic: true,
          strokeColor: speciesColors[translocation.species],
          strokeOpacity: 0.6,
          strokeWeight: 3
        });

        flightPath.setMap(map);

        // Info windows
        const sourceInfoWindow = new window.google.maps.InfoWindow({
          content: `
            <div class="p-3">
              <h3 class="font-bold text-lg">${translocation.source_reserve.name}</h3>
              <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
              <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
              <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
              <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
              <p><strong>Role:</strong> Source Location</p>
              ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
            </div>
          `
        });

        const destInfoWindow = new window.google.maps.InfoWindow({
          content: `
            <div class="p-3">
              <h3 class="font-bold text-lg">${translocation.recipient_reserve.name}</h3>
              <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
              <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
              <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
              <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
              <p><strong>Role:</strong> Destination Location</p>
              ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
            </div>
          `
        });

        sourceMarker.addListener('click', () => {
          sourceInfoWindow.open(map, sourceMarker);
        });

        destMarker.addListener('click', () => {
          destInfoWindow.open(map, destMarker);
        });

        bounds.extend(sourceLatLng);
        bounds.extend(destLatLng);
      });

      if (filteredTranslocations.length > 0) {
        map.fitBounds(bounds);
      }
    });
  }, [filteredTranslocations]);

  return <div id="map" className="w-full h-96 rounded-lg shadow-lg"></div>;
};

const TranslocationForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    species: 'elephant',
    number_of_animals: '',
    month: '',
    year: '',
    source_reserve: {
      name: '',
      country: '',
      latitude: '',
      longitude: ''
    },
    recipient_reserve: {
      name: '',
      country: '',
      latitude: '',
      longitude: ''
    },
    transport_mode: 'road',
    additional_notes: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      number_of_animals: parseInt(formData.number_of_animals),
      month: parseInt(formData.month),
      year: parseInt(formData.year),
      source_reserve: {
        ...formData.source_reserve,
        latitude: parseFloat(formData.source_reserve.latitude),
        longitude: parseFloat(formData.source_reserve.longitude)
      },
      recipient_reserve: {
        ...formData.recipient_reserve,
        latitude: parseFloat(formData.recipient_reserve.latitude),
        longitude: parseFloat(formData.recipient_reserve.longitude)
      }
    };
    onSubmit(submitData);
    setFormData({
      species: 'elephant',
      number_of_animals: '',
      month: '',
      year: '',
      source_reserve: { name: '', country: '', latitude: '', longitude: '' },
      recipient_reserve: { name: '', country: '', latitude: '', longitude: '' },
      transport_mode: 'road',
      additional_notes: ''
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg space-y-4">
      <h3 className="text-xl font-bold mb-4">Add New Translocation</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Species *</label>
          <select
            value={formData.species}
            onChange={(e) => setFormData({...formData, species: e.target.value})}
            className="w-full border rounded-md px-3 py-2"
            required
          >
            <option value="elephant">Elephant</option>
            <option value="rhino">Rhino</option>
            <option value="lion">Lion</option>
            <option value="cheetah">Cheetah</option>
            <option value="buffalo">Buffalo</option>
            <option value="giraffe">Giraffe</option>
            <option value="zebra">Zebra</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Number of Animals *</label>
          <input
            type="number"
            value={formData.number_of_animals}
            onChange={(e) => setFormData({...formData, number_of_animals: e.target.value})}
            className="w-full border rounded-md px-3 py-2"
            required
            min="1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Month *</label>
          <select
            value={formData.month}
            onChange={(e) => setFormData({...formData, month: e.target.value})}
            className="w-full border rounded-md px-3 py-2"
            required
          >
            <option value="">Select Month</option>
            {Array.from({length: 12}, (_, i) => (
              <option key={i+1} value={i+1}>{new Date(2000, i).toLocaleString('default', { month: 'long' })}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Year *</label>
          <input
            type="number"
            value={formData.year}
            onChange={(e) => setFormData({...formData, year: e.target.value})}
            className="w-full border rounded-md px-3 py-2"
            required
            min="2000"
            max="2030"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h4 className="font-medium text-lg">Source Reserve</h4>
          <input
            type="text"
            placeholder="Reserve Name *"
            value={formData.source_reserve.name}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, name: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.source_reserve.country}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, country: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Latitude *"
            value={formData.source_reserve.latitude}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, latitude: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Longitude *"
            value={formData.source_reserve.longitude}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, longitude: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
        </div>

        <div className="space-y-3">
          <h4 className="font-medium text-lg">Recipient Reserve</h4>
          <input
            type="text"
            placeholder="Reserve Name *"
            value={formData.recipient_reserve.name}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, name: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.recipient_reserve.country}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, country: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Latitude *"
            value={formData.recipient_reserve.latitude}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, latitude: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Longitude *"
            value={formData.recipient_reserve.longitude}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, longitude: e.target.value}})}
            className="w-full border rounded-md px-3 py-2"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Transport Mode *</label>
        <select
          value={formData.transport_mode}
          onChange={(e) => setFormData({...formData, transport_mode: e.target.value})}
          className="w-full border rounded-md px-3 py-2"
          required
        >
          <option value="road">Road (Truck) 🚛</option>
          <option value="air">Air (Plane) ✈️</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Additional Notes</label>
        <textarea
          value={formData.additional_notes}
          onChange={(e) => setFormData({...formData, additional_notes: e.target.value})}
          className="w-full border rounded-md px-3 py-2"
          rows="3"
          placeholder="Optional additional information..."
        />
      </div>

      <button
        type="submit"
        className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
      >
        Add Translocation
      </button>
    </form>
  );
};

const StatsPanel = ({ stats }) => {
  const speciesEmojis = {
    elephant: '🐘',
    rhino: '🦏',
    lion: '🦁',
    cheetah: '🐆',
    buffalo: '🐃',
    giraffe: '🦒',
    zebra: '🦓',
    other: '🦌'
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold mb-4">Conservation Impact</h3>
      <div className="space-y-3">
        {Object.entries(stats).map(([species, data]) => (
          <div key={species} className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">{speciesEmojis[species] || '🦌'}</span>
              <span className="font-medium capitalize">{species}</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-green-600">{data.total_animals}</div>
              <div className="text-sm text-gray-500">{data.total_translocations} translocations</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

function App() {
  const [translocations, setTranslocations] = useState([]);
  const [filteredTranslocations, setFilteredTranslocations] = useState([]);
  const [stats, setStats] = useState({});
  const [filters, setFilters] = useState({
    species: '',
    year: '',
    transport_mode: ''
  });
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchTranslocations = async () => {
    try {
      const response = await axios.get(`${API}/translocations`);
      setTranslocations(response.data);
      setFilteredTranslocations(response.data);
    } catch (error) {
      console.error('Error fetching translocations:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/translocations/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const createSampleData = async () => {
    try {
      await axios.post(`${API}/translocations/sample-data`);
      fetchTranslocations();
      fetchStats();
    } catch (error) {
      console.error('Error creating sample data:', error);
    }
  };

  const addTranslocation = async (translocationData) => {
    try {
      await axios.post(`${API}/translocations`, translocationData);
      fetchTranslocations();
      fetchStats();
      setShowForm(false);
    } catch (error) {
      console.error('Error adding translocation:', error);
      alert('Error adding translocation. Please check all fields.');
    }
  };

  const applyFilters = () => {
    let filtered = translocations;
    
    if (filters.species) {
      filtered = filtered.filter(t => t.species === filters.species);
    }
    if (filters.year) {
      filtered = filtered.filter(t => t.year === parseInt(filters.year));
    }
    if (filters.transport_mode) {
      filtered = filtered.filter(t => t.transport_mode === filters.transport_mode);
    }
    
    setFilteredTranslocations(filtered);
  };

  useEffect(() => {
    const initializeData = async () => {
      setLoading(true);
      await fetchTranslocations();
      await fetchStats();
      setLoading(false);
    };
    initializeData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, translocations]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🐘</div>
          <div className="text-xl font-semibold">Loading Conservation Dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">🌍 Wildlife Conservation Dashboard</h1>
          <p className="text-xl text-gray-600">Tracking Wildlife Translocations Across Africa</p>
        </div>

        {/* Controls */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div className="flex flex-wrap gap-4">
              <select
                value={filters.species}
                onChange={(e) => setFilters({...filters, species: e.target.value})}
                className="border rounded-md px-3 py-2"
              >
                <option value="">All Species</option>
                <option value="elephant">🐘 Elephant</option>
                <option value="rhino">🦏 Rhino</option>
                <option value="lion">🦁 Lion</option>
                <option value="cheetah">🐆 Cheetah</option>
                <option value="buffalo">🐃 Buffalo</option>
                <option value="giraffe">🦒 Giraffe</option>
                <option value="zebra">🦓 Zebra</option>
                <option value="other">🦌 Other</option>
              </select>

              <select
                value={filters.year}
                onChange={(e) => setFilters({...filters, year: e.target.value})}
                className="border rounded-md px-3 py-2"
              >
                <option value="">All Years</option>
                {[...new Set(translocations.map(t => t.year))].sort().map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>

              <select
                value={filters.transport_mode}
                onChange={(e) => setFilters({...filters, transport_mode: e.target.value})}
                className="border rounded-md px-3 py-2"
              >
                <option value="">All Transport</option>
                <option value="road">🚛 Road</option>
                <option value="air">✈️ Air</option>
              </select>

              <button
                onClick={() => setFilters({species: '', year: '', transport_mode: ''})}
                className="bg-gray-500 text-white px-4 py-2 rounded-md hover:bg-gray-600"
              >
                Clear Filters
              </button>
            </div>

            <div className="flex gap-2">
              {translocations.length === 0 && (
                <button
                  onClick={createSampleData}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Load Sample Data
                </button>
              )}
              <button
                onClick={() => setShowForm(!showForm)}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                {showForm ? 'Hide Form' : 'Add Translocation'}
              </button>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            Showing {filteredTranslocations.length} of {translocations.length} translocations
          </div>
        </div>

        {/* Add Form */}
        {showForm && (
          <div className="mb-6">
            <TranslocationForm onSubmit={addTranslocation} />
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Translocation Map</h2>
              {filteredTranslocations.length > 0 ? (
                <Map translocations={translocations} filteredTranslocations={filteredTranslocations} />
              ) : (
                <div className="w-full h-96 bg-gray-200 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-4xl mb-2">📍</div>
                    <div className="text-gray-600">No translocations to display</div>
                    {translocations.length === 0 && (
                      <button
                        onClick={createSampleData}
                        className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                      >
                        Load Sample Data
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Stats Panel */}
          <div className="space-y-6">
            <StatsPanel stats={stats} />
            
            {/* Legend */}
            <div className="bg-white p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Map Legend</h3>
              <div className="space-y-2 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-red-400 border-2 border-white"></div>
                  <span>Source Location</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-red-600 border-2 border-black"></div>
                  <span>Destination Location</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-1 bg-red-400"></div>
                  <span>Translocation Route</span>
                </div>
                <div className="mt-3 text-xs text-gray-500">
                  Click markers for detailed information
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;