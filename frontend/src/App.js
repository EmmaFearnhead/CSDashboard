import { useState, useEffect, useRef } from "react";
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
  const mapRef = useRef(null);
  
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
        
        // Create a static background for the map
        const staticBackground = document.createElement('div');
        staticBackground.style.width = '100%';
        staticBackground.style.height = '100%';
        staticBackground.style.backgroundColor = '#a0c8f0';
        staticBackground.style.position = 'absolute';
        staticBackground.style.top = '0';
        staticBackground.style.left = '0';
        staticBackground.style.zIndex = '0';
        mapContainer.appendChild(staticBackground);
        
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
        
        // Add a static background layer to the map
        window.L.rectangle([[-90, -180], [90, 180]], {
          color: "#a0c8f0",
          weight: 1,
          fillColor: "#a0c8f0",
          fillOpacity: 1
        }).addTo(map);
        
        // Try to add OpenStreetMap tiles, but don't worry if it fails
        try {
          window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
          }).addTo(map);
        } catch (error) {
          console.error('Failed to load OpenStreetMap tiles:', error);
          // We already have a static background, so no need for a fallback
        }
        
        // Add markers and polylines
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
        if (layer instanceof window.L.Marker || 
            (layer instanceof window.L.Polyline && !(layer instanceof window.L.Rectangle))) {
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

      // Create marker icon function - using simple circle markers instead of divIcons
      const createMarker = (latlng, color, isSource = true) => {
        return window.L.circleMarker(latlng, {
          radius: 8,
          fillColor: color,
          color: isSource ? '#ffffff' : '#000000',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.8
        });
      };

      const bounds = [];

      filteredTranslocations.forEach((translocation) => {
        const sourceLat = translocation.source_reserve.latitude;
        const sourceLng = translocation.source_reserve.longitude;
        const destLat = translocation.recipient_reserve.latitude;
        const destLng = translocation.recipient_reserve.longitude;

        // Source marker
        const sourceMarker = createMarker(
          [sourceLat, sourceLng], 
          speciesColors[translocation.species], 
          true
        ).addTo(mapRef.current);
        
        sourceMarker.bindTooltip(`Source: ${translocation.source_reserve.name}`);

        // Destination marker
        const destMarker = createMarker(
          [destLat, destLng], 
          speciesColors[translocation.species], 
          false
        ).addTo(mapRef.current);
        
        destMarker.bindTooltip(`Destination: ${translocation.recipient_reserve.name}`);

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
        try {
          mapRef.current.fitBounds(bounds, { padding: [20, 20] });
        } catch (error) {
          console.error('Error fitting bounds:', error);
          // If fitting bounds fails, just set the view to Africa
          mapRef.current.setView([-15, 25], 4);
        }
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
    if (!mapRef.current) return;
    
    try {
      // Clear existing markers and layers
      mapRef.current.eachLayer(layer => {
        if (layer instanceof window.L.Marker || 
            (layer instanceof window.L.Polyline && !(layer instanceof window.L.Rectangle))) {
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

      // Create marker icon function - using simple circle markers instead of divIcons
      const createMarker = (latlng, color, isSource = true) => {
        return window.L.circleMarker(latlng, {
          radius: 8,
          fillColor: color,
          color: isSource ? '#ffffff' : '#000000',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.8
        });
      };

      const bounds = [];

      filteredTranslocations.forEach((translocation) => {
        const sourceLat = translocation.source_reserve.latitude;
        const sourceLng = translocation.source_reserve.longitude;
        const destLat = translocation.recipient_reserve.latitude;
        const destLng = translocation.recipient_reserve.longitude;

        // Source marker
        const sourceMarker = createMarker(
          [sourceLat, sourceLng], 
          speciesColors[translocation.species], 
          true
        ).addTo(mapRef.current);
        
        sourceMarker.bindTooltip(`Source: ${translocation.source_reserve.name}`);

        // Destination marker
        const destMarker = createMarker(
          [destLat, destLng], 
          speciesColors[translocation.species], 
          false
        ).addTo(mapRef.current);
        
        destMarker.bindTooltip(`Destination: ${translocation.recipient_reserve.name}`);

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
        try {
          mapRef.current.fitBounds(bounds, { padding: [20, 20] });
        } catch (error) {
          console.error('Error fitting bounds:', error);
          // If fitting bounds fails, just set the view to Africa
          mapRef.current.setView([-15, 25], 4);
        }
      }
    } catch (error) {
      console.error('Error updating map markers:', error);
    }
  }, [filteredTranslocations]);

  return <div id="map" className="w-full h-96 rounded-lg shadow-lg"></div>;
};

const TranslocationForm = ({ onSubmit, editingTranslocation, onCancel }) => {
  const [formData, setFormData] = useState({
    project_title: '',
    year: '',
    species: 'Elephant',
    number_of_animals: '',
    source_area: {
      name: '',
      coordinates: '',
      country: ''
    },
    recipient_area: {
      name: '',
      coordinates: '',
      country: ''
    },
    transport: 'Road',
    special_project: '',
    additional_info: ''
  });

  useEffect(() => {
    if (editingTranslocation) {
      setFormData(editingTranslocation);
    }
  }, [editingTranslocation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const submitData = {
      ...formData,
      number_of_animals: parseInt(formData.number_of_animals),
      year: parseInt(formData.year)
    };
    onSubmit(submitData);
    if (!editingTranslocation) {
      setFormData({
        project_title: '',
        year: '',
        species: 'Elephant',
        number_of_animals: '',
        source_area: { name: '', coordinates: '', country: '' },
        recipient_area: { name: '', coordinates: '', country: '' },
        transport: 'Road',
        special_project: '',
        additional_info: ''
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg space-y-4 border-l-4 border-nature-green">
      <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
        <span className="text-2xl mr-2">🌿</span>
        {editingTranslocation ? 'Edit Conservation Record' : 'Add New Conservation Record'}
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Project Title *</label>
          <input
            type="text"
            value={formData.project_title}
            onChange={(e) => setFormData({...formData, project_title: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
            placeholder="e.g., 500 Elephants, Rhino Relocation"
          />
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

        <div>
          <label className="block text-sm font-medium mb-1">Species *</label>
          <select
            value={formData.species}
            onChange={(e) => setFormData({...formData, species: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          >
            <option value="Elephant">🐘 Elephant</option>
            <option value="Black Rhino">🦏 Black Rhino</option>
            <option value="White Rhino">🦏 White Rhino</option>
            <option value="Lion">🦁 Lion</option>
            <option value="Buffalo">🐃 Buffalo</option>
            <option value="Impala">🦌 Impala</option>
            <option value="Sable">🦌 Sable</option>
            <option value="Kudu">🦌 Kudu</option>
            <option value="Warthog">🐗 Warthog</option>
            <option value="Waterbuck">🦌 Waterbuck</option>
            <option value="Eland">🦌 Eland</option>
            <option value="Zebra">🦓 Zebra</option>
            <option value="Other">🦌 Other</option>
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
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h4 className="font-medium text-lg">Source Area</h4>
          <input
            type="text"
            placeholder="Source Area Name *"
            value={formData.source_area.name}
            onChange={(e) => setFormData({...formData, source_area: {...formData.source_area, name: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="text"
            placeholder="Coordinates (lat, lng)"
            value={formData.source_area.coordinates}
            onChange={(e) => setFormData({...formData, source_area: {...formData.source_area, coordinates: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.source_area.country}
            onChange={(e) => setFormData({...formData, source_area: {...formData.source_area, country: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
        </div>

        <div className="space-y-3">
          <h4 className="font-medium text-lg">Recipient Area</h4>
          <input
            type="text"
            placeholder="Recipient Area Name *"
            value={formData.recipient_area.name}
            onChange={(e) => setFormData({...formData, recipient_area: {...formData.recipient_area, name: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
          <input
            type="text"
            placeholder="Coordinates (lat, lng)"
            value={formData.recipient_area.coordinates}
            onChange={(e) => setFormData({...formData, recipient_area: {...formData.recipient_area, coordinates: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
          />
          <input
            type="text"
            placeholder="Country *"
            value={formData.recipient_area.country}
            onChange={(e) => setFormData({...formData, recipient_area: {...formData.recipient_area, country: e.target.value}})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Transport *</label>
          <select
            value={formData.transport}
            onChange={(e) => setFormData({...formData, transport: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
            required
          >
            <option value="Road">Road 🚛</option>
            <option value="Air">Air ✈️</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Special Project</label>
          <select
            value={formData.special_project}
            onChange={(e) => setFormData({...formData, special_project: e.target.value})}
            className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
          >
            <option value="">None</option>
            <option value="Peace Parks">Peace Parks</option>
            <option value="African Parks">African Parks</option>
            <option value="Rhino Rewild">Rhino Rewild</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Additional Information</label>
        <textarea
          value={formData.additional_info}
          onChange={(e) => setFormData({...formData, additional_info: e.target.value})}
          className="w-full border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
          rows="3"
          placeholder="Optional additional information..."
        />
      </div>

      <div className="flex gap-2">
        <button
          type="submit"
          className="flex-1 bg-nature-green text-white py-3 px-4 rounded-md hover:bg-forest-green transition-colors shadow-lg font-semibold"
        >
          🌿 {editingTranslocation ? 'Update' : 'Add'} Conservation Record
        </button>
        {editingTranslocation && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-3 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
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
    transport: '',
    special_project: ''
  });
  const [showForm, setShowForm] = useState(false);
  const [showDataTable, setShowDataTable] = useState(false);
  const [editingTranslocation, setEditingTranslocation] = useState(null);
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

  const importHistoricalData = async () => {
    try {
      await axios.post(`${API}/translocations/import-historical`);
      fetchTranslocations();
      fetchStats();
    } catch (error) {
      console.error('Error importing historical data:', error);
    }
  };

  const addTranslocation = async (translocationData) => {
    try {
      if (editingTranslocation) {
        await axios.put(`${API}/translocations/${editingTranslocation.id}`, translocationData);
        setEditingTranslocation(null);
      } else {
        await axios.post(`${API}/translocations`, translocationData);
      }
      fetchTranslocations();
      fetchStats();
      setShowForm(false);
    } catch (error) {
      console.error('Error saving translocation:', error);
      alert('Error saving translocation. Please check all fields.');
    }
  };

  const deleteTranslocation = async (translocationId) => {
    if (window.confirm('Are you sure you want to delete this translocation record?')) {
      try {
        await axios.delete(`${API}/translocations/${translocationId}`);
        fetchTranslocations();
        fetchStats();
      } catch (error) {
        console.error('Error deleting translocation:', error);
      }
    }
  };

  const editTranslocation = (translocation) => {
    setEditingTranslocation(translocation);
    setShowForm(true);
    setShowDataTable(false);
  };

  const cancelEdit = () => {
    setEditingTranslocation(null);
    setShowForm(false);
  };

  const applyFilters = () => {
    let filtered = translocations;
    
    if (filters.species) {
      filtered = filtered.filter(t => t.species === filters.species);
    }
    if (filters.year) {
      filtered = filtered.filter(t => t.year === parseInt(filters.year));
    }
    if (filters.transport) {
      filtered = filtered.filter(t => t.transport === filters.transport);
    }
    if (filters.special_project) {
      filtered = filtered.filter(t => t.special_project === filters.special_project);
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
                  onClick={importHistoricalData}
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
                        onClick={importHistoricalData}
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