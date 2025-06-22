import { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Load Leaflet CSS and JS
const loadLeafletResources = () => {
  return new Promise((resolve) => {
    // Check if Leaflet is already loaded
    if (window.L) {
      resolve();
      return;
    }

    // Load CSS first
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    cssLink.crossOrigin = '';
    document.head.appendChild(cssLink);

    // Load JS
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = () => {
      // Fix for default markers in Leaflet
      delete window.L.Icon.Default.prototype._getIconUrl;
      window.L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
        iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      });
      resolve();
    };
    document.head.appendChild(script);
  });
};

const Map = ({ translocations, filteredTranslocations }) => {
  // Use a ref to store the map instance
  const mapRef = React.useRef(null);
  
  // Initialize map only once
  useEffect(() => {
    let map = null;
    
    const initMap = async () => {
      try {
        // Load Leaflet resources first
        await loadLeafletResources();
        
        // Clear existing map if it exists
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;
        
        // If we already have a map instance, clean it up
        if (mapRef.current) {
          mapRef.current.remove();
          mapRef.current = null;
        }
        
        // Initialize map centered on Africa
        map = window.L.map('map', {
          attributionControl: true,
          zoomControl: true,
          doubleClickZoom: true,
          scrollWheelZoom: true,
          dragging: true,
          zoom: 4
        }).setView([-15, 25], 4);
        
        // Store the map instance in the ref
        mapRef.current = map;
        
        // Add OpenStreetMap tiles with fallback
        try {
          window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
          }).addTo(map);
        } catch (error) {
          console.error('Failed to load OpenStreetMap tiles:', error);
          
          // Try alternative tile provider as fallback
          try {
            window.L.tileLayer('https://tile.openstreetmap.de/{z}/{x}/{y}.png', {
              attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
              maxZoom: 18,
            }).addTo(map);
          } catch (fallbackError) {
            console.error('Failed to load fallback tiles:', fallbackError);
            
            // Last resort - use a static color background
            window.L.rectangle([[-90, -180], [90, 180]], {
              color: "#a0c8f0",
              weight: 1,
              fillColor: "#f0f0f0",
              fillOpacity: 1
            }).addTo(map);
          }
        }
        
        updateMapMarkers();
      } catch (error) {
        console.error('Error initializing map:', error);
      }
    };
    
    // Function to update markers based on filtered data
    const updateMapMarkers = () => {
      if (!mapRef.current) return;
      
      // Clear existing markers and layers
      mapRef.current.eachLayer(layer => {
        if (layer instanceof window.L.Marker || layer instanceof window.L.Polyline) {
          mapRef.current.removeLayer(layer);
        }
      });
      
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

      // Create marker icon function
      const createMarkerIcon = (color, isSource = true) => {
        return window.L.divIcon({
          html: `<div style="
            background-color: ${color};
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: ${isSource ? '2px solid #ffffff' : '2px solid #000000'};
            opacity: ${isSource ? '0.8' : '1'};
          "></div>`,
          className: 'custom-div-icon',
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });
      };

      const bounds = [];

      filteredTranslocations.forEach((translocation) => {
        const sourceLat = translocation.source_reserve.latitude;
        const sourceLng = translocation.source_reserve.longitude;
        const destLat = translocation.recipient_reserve.latitude;
        const destLng = translocation.recipient_reserve.longitude;

        // Source marker
        const sourceMarker = window.L.marker([sourceLat, sourceLng], {
          icon: createMarkerIcon(speciesColors[translocation.species], true),
          title: `Source: ${translocation.source_reserve.name}`
        }).addTo(mapRef.current);

        // Destination marker
        const destMarker = window.L.marker([destLat, destLng], {
          icon: createMarkerIcon(speciesColors[translocation.species], false),
          title: `Destination: ${translocation.recipient_reserve.name}`
        }).addTo(mapRef.current);

        // Connection line
        const polyline = window.L.polyline([[sourceLat, sourceLng], [destLat, destLng]], {
          color: speciesColors[translocation.species],
          weight: 3,
          opacity: 0.6
        }).addTo(mapRef.current);

        // Info popups
        const sourcePopupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">${translocation.source_reserve.name}</h3>
            <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
            <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
            <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
            <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
            <p><strong>Role:</strong> Source Location</p>
            ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
          </div>
        `;

        const destPopupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">${translocation.recipient_reserve.name}</h3>
            <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
            <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
            <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
            <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
            <p><strong>Role:</strong> Destination Location</p>
            ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
          </div>
        `;

        sourceMarker.bindPopup(sourcePopupContent);
        destMarker.bindPopup(destPopupContent);

        bounds.push([sourceLat, sourceLng]);
        bounds.push([destLat, destLng]);
      });

      // Fit map to show all markers
      if (bounds.length > 0) {
        mapRef.current.fitBounds(bounds, { padding: [20, 20] });
      }
    };
    
    // Initialize the map
    initMap();
    
    // Cleanup function
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []); // Empty dependency array means this effect runs once on mount
  
  // Update markers when filtered data changes
  useEffect(() => {
    if (mapRef.current) {
      // Clear existing markers and layers
      mapRef.current.eachLayer(layer => {
        if (layer instanceof window.L.Marker || layer instanceof window.L.Polyline) {
          mapRef.current.removeLayer(layer);
        }
      });
      
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

      // Create marker icon function
      const createMarkerIcon = (color, isSource = true) => {
        return window.L.divIcon({
          html: `<div style="
            background-color: ${color};
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: ${isSource ? '2px solid #ffffff' : '2px solid #000000'};
            opacity: ${isSource ? '0.8' : '1'};
          "></div>`,
          className: 'custom-div-icon',
          iconSize: [16, 16],
          iconAnchor: [8, 8]
        });
      };

      const bounds = [];

      filteredTranslocations.forEach((translocation) => {
        const sourceLat = translocation.source_reserve.latitude;
        const sourceLng = translocation.source_reserve.longitude;
        const destLat = translocation.recipient_reserve.latitude;
        const destLng = translocation.recipient_reserve.longitude;

        // Source marker
        const sourceMarker = window.L.marker([sourceLat, sourceLng], {
          icon: createMarkerIcon(speciesColors[translocation.species], true),
          title: `Source: ${translocation.source_reserve.name}`
        }).addTo(mapRef.current);

        // Destination marker
        const destMarker = window.L.marker([destLat, destLng], {
          icon: createMarkerIcon(speciesColors[translocation.species], false),
          title: `Destination: ${translocation.recipient_reserve.name}`
        }).addTo(mapRef.current);

        // Connection line
        const polyline = window.L.polyline([[sourceLat, sourceLng], [destLat, destLng]], {
          color: speciesColors[translocation.species],
          weight: 3,
          opacity: 0.6
        }).addTo(mapRef.current);

        // Info popups
        const sourcePopupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">${translocation.source_reserve.name}</h3>
            <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
            <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
            <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
            <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
            <p><strong>Role:</strong> Source Location</p>
            ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
          </div>
        `;

        const destPopupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px;">${translocation.recipient_reserve.name}</h3>
            <p><strong>Species:</strong> ${translocation.species.charAt(0).toUpperCase() + translocation.species.slice(1)}</p>
            <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
            <p><strong>Date:</strong> ${translocation.month}/${translocation.year}</p>
            <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport_mode)} ${translocation.transport_mode.charAt(0).toUpperCase() + translocation.transport_mode.slice(1)}</p>
            <p><strong>Role:</strong> Destination Location</p>
            ${translocation.additional_notes ? `<p><strong>Notes:</strong> ${translocation.additional_notes}</p>` : ''}
          </div>
        `;

        sourceMarker.bindPopup(sourcePopupContent);
        destMarker.bindPopup(destPopupContent);

        bounds.push([sourceLat, sourceLng]);
        bounds.push([destLat, destLng]);
      });

      // Fit map to show all markers
      if (bounds.length > 0) {
        mapRef.current.fitBounds(bounds, { padding: [20, 20] });
      }
    }
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
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg space-y-4 border-l-4 border-nature-green">
      <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
        <span className="text-2xl mr-2">🌿</span>
        Add New Conservation Record
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Species *</label>
          <select
            value={formData.species}
            onChange={(e) => setFormData({...formData, species: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
            min="1"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Month *</label>
          <select
            value={formData.month}
            onChange={(e) => setFormData({...formData, month: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.source_reserve.country}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, country: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Latitude *"
            value={formData.source_reserve.latitude}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, latitude: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Longitude *"
            value={formData.source_reserve.longitude}
            onChange={(e) => setFormData({...formData, source_reserve: {...formData.source_reserve, longitude: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.recipient_reserve.country}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, country: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Latitude *"
            value={formData.recipient_reserve.latitude}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, latitude: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="number"
            step="any"
            placeholder="Longitude *"
            value={formData.recipient_reserve.longitude}
            onChange={(e) => setFormData({...formData, recipient_reserve: {...formData.recipient_reserve, longitude: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Transport Mode *</label>
        <select
          value={formData.transport_mode}
          onChange={(e) => setFormData({...formData, transport_mode: e.target.value})}
          className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
          className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
          rows="3"
          placeholder="Optional additional information..."
        />
      </div>

      <button
        type="submit"
        className="w-full bg-nature-green text-white py-3 px-4 rounded-md hover:bg-forest-green transition-colors shadow-lg font-semibold"
      >
        🌿 Add Conservation Record
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
    <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-forest-green">
      <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
        <span className="text-2xl mr-2">🌍</span>
        Conservation Impact
      </h3>
      <div className="space-y-3">
        {Object.entries(stats).map(([species, data]) => (
          <div key={species} className="stats-item flex justify-between items-center p-3 rounded-md">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{speciesEmojis[species] || '🦌'}</span>
              <span className="font-medium capitalize text-forest-dark">{species}</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-nature-green">{data.total_animals}</div>
              <div className="text-sm text-nature-brown">{data.total_translocations} translocations</div>
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
      <div className="min-h-screen conservation-loading flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🌿</div>
          <div className="text-xl font-semibold text-forest-dark">Loading Conservation Dashboard...</div>
          <div className="text-sm text-nature-brown mt-2">Preparing wildlife translocation data</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-nature-light">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-forest-dark mb-2">Wildlife Conservation Dashboard</h1>
          <p className="text-xl text-nature-brown">Tracking Wildlife Translocations Across Africa</p>
        </div>

        {/* Controls */}
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6 border-l-4 border-forest-green">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
            <div className="flex flex-wrap gap-4">
              <select
                value={filters.species}
                onChange={(e) => setFilters({...filters, species: e.target.value})}
                className="border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
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
                className="border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
              >
                <option value="">All Years</option>
                {[...new Set(translocations.map(t => t.year))].sort().map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>

              <select
                value={filters.transport_mode}
                onChange={(e) => setFilters({...filters, transport_mode: e.target.value})}
                className="border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
              >
                <option value="">All Transport</option>
                <option value="road">🚛 Road</option>
                <option value="air">✈️ Air</option>
              </select>

              <button
                onClick={() => setFilters({species: '', year: '', transport_mode: ''})}
                className="bg-nature-brown text-white px-4 py-2 rounded-md hover:bg-earth-brown transition-colors shadow-md"
              >
                Clear Filters
              </button>
            </div>

            <div className="flex gap-2">
              {translocations.length === 0 && (
                <button
                  onClick={createSampleData}
                  className="bg-forest-green text-white px-4 py-2 rounded-md hover:bg-forest-dark transition-colors shadow-md"
                >
                  Load Sample Data
                </button>
              )}
              <button
                onClick={() => setShowForm(!showForm)}
                className="bg-nature-green text-white px-4 py-2 rounded-md hover:bg-forest-green transition-colors shadow-md"
              >
                {showForm ? 'Hide Form' : '🌿 Add Translocation'}
              </button>
            </div>
          </div>

          <div className="text-sm text-nature-brown">
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
            <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-nature-green">
              <h2 className="text-2xl font-bold mb-4 text-forest-dark flex items-center">
                <span className="text-3xl mr-3">🗺️</span>
                Wildlife Translocation Map
              </h2>
              {filteredTranslocations.length > 0 ? (
                <Map translocations={translocations} filteredTranslocations={filteredTranslocations} />
              ) : (
                <div className="w-full h-96 bg-nature-light rounded-lg flex items-center justify-center border-2 border-sage-green">
                  <div className="text-center">
                    <div className="text-6xl mb-4">🌿</div>
                    <div className="text-nature-brown text-lg font-medium mb-2">No translocations to display</div>
                    <div className="text-nature-brown text-sm mb-4">Load sample data to see conservation efforts across Africa</div>
                    {translocations.length === 0 && (
                      <button
                        onClick={createSampleData}
                        className="bg-forest-green text-white px-6 py-3 rounded-md hover:bg-forest-dark transition-colors shadow-md"
                      >
                        🌍 Load Sample Data
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
            <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-sage-green">
              <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
                <span className="text-2xl mr-2">🗺️</span>
                Map Legend
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 rounded-full border-2 border-white opacity-80" style={{backgroundColor: '#8B4513'}}></div>
                  <span className="text-forest-dark">Source Location</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 rounded-full border-2 border-black" style={{backgroundColor: '#8B4513'}}></div>
                  <span className="text-forest-dark">Destination Location</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-1 opacity-60" style={{backgroundColor: '#8B4513'}}></div>
                  <span className="text-forest-dark">Translocation Route</span>
                </div>
                <div className="mt-4 text-xs text-nature-brown bg-nature-light p-2 rounded">
                  💡 Click map markers for detailed information about each translocation
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