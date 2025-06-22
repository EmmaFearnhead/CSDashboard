import { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";
import MapComponent from "./MapComponent";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Map component is now handled by MapComponent.js

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
            <option value="Elephant">Elephant</option>
            <option value="White Rhino">White Rhino</option>
            <option value="Black Rhino">Black Rhino</option>
            <option value="Plains Game Species">Plains Game Species</option>
            <option value="Lion">Lion</option>
            <option value="Buffalo">Buffalo</option>
            <option value="Hippo">Hippo</option>
            <option value="Giraffe">Giraffe</option>
            <option value="Zebra">Zebra</option>
            <option value="Kudu">Kudu</option>
            <option value="Sable">Sable</option>
            <option value="Impala">Impala</option>
            <option value="Waterbuck">Waterbuck</option>
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
            <option value="Road">Road</option>
            <option value="Air">Air</option>
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
          {editingTranslocation ? 'Update' : 'Add'} Conservation Record
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
  // Sort species by total animals count (most to least)
  const sortedStats = Object.entries(stats).sort((a, b) => b[1].total_animals - a[1].total_animals);
  
  return (
    <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-forest-green">
      <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
        Conservation Impact
      </h3>
      <div className="space-y-3">
        {sortedStats.map(([species, data]) => (
          <div key={species} className="stats-item flex justify-between items-center p-3 rounded-md">
            <div className="flex items-center space-x-3">
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
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [editingTranslocation, setEditingTranslocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);

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
      await axios.post(`${API}/translocations/import-simplified-data`);
      fetchTranslocations();
      fetchStats();
    } catch (error) {
      console.error('Error importing historical data:', error);
    }
  };

  const importExcelFile = async (file) => {
    try {
      console.log('Starting file upload:', file.name, file.type, file.size);
      setUploadLoading(true);
      const formData = new FormData();
      formData.append('file', file);
      
      console.log('Making API request to:', `${API}/translocations/import-excel-file`);
      const response = await axios.post(`${API}/translocations/import-excel-file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      console.log('Upload response:', response.data);
      alert(`Successfully imported ${response.data.successful_imports} records from ${response.data.total_rows_processed} rows!`);
      
      // Refresh data
      await fetchTranslocations();
      await fetchStats();
      setShowFileUpload(false);
      
    } catch (error) {
      console.error('Error uploading file:', error);
      console.error('Error details:', error.response?.data);
      alert(`Error uploading file: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploadLoading(false);
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
    
    console.log('Filtering results:', {
      originalCount: translocations.length,
      filteredCount: filtered.length,
      filters: filters,
      sampleFiltered: filtered.slice(0, 3).map(t => ({ species: t.species, project: t.project_title, country: t.recipient_area.country }))
    });
    
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
          <h1 className="text-4xl font-bold text-forest-dark mb-2">Conservation Solutions Translocation Dashboard</h1>
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
                <option value="Elephant">Elephant</option>
                <option value="White Rhino">White Rhino</option>
                <option value="Black Rhino">Black Rhino</option>
                <option value="Plains Game Species">Plains Game Species</option>
                <option value="Lion">Lion</option>
                <option value="Buffalo">Buffalo</option>
                <option value="Hippo">Hippo</option>
                <option value="Giraffe">Giraffe</option>
                <option value="Zebra">Zebra</option>
                <option value="Kudu">Kudu</option>
                <option value="Sable">Sable</option>
                <option value="Impala">Impala</option>
                <option value="Waterbuck">Waterbuck</option>
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
                value={filters.transport}
                onChange={(e) => setFilters({...filters, transport: e.target.value})}
                className="border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
              >
                <option value="">All Transport</option>
                <option value="Road">Road</option>
                <option value="Air">Air</option>
              </select>

              <select
                value={filters.special_project}
                onChange={(e) => setFilters({...filters, special_project: e.target.value})}
                className="border-2 border-sage-green rounded-md px-3 py-2 focus:border-forest-green focus:ring-2 focus:ring-forest-light"
              >
                <option value="">All Projects</option>
                <option value="Peace Parks">Peace Parks</option>
                <option value="African Parks">African Parks</option>
                <option value="Rhino Rewild">Rhino Rewild</option>
              </select>

              <button
                onClick={() => setFilters({species: '', year: '', transport: '', special_project: ''})}
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
                  Import Historical Data
                </button>
              )}
              <button
                onClick={() => setShowFileUpload(!showFileUpload)}
                className="bg-nature-green text-white px-4 py-2 rounded-md hover:bg-forest-green transition-colors shadow-md"
              >
                {showFileUpload ? 'Hide Upload' : 'Upload Excel File'}
              </button>
              <button
                onClick={() => {setShowForm(!showForm); setEditingTranslocation(null);}}
                className="bg-nature-green text-white px-4 py-2 rounded-md hover:bg-forest-green transition-colors shadow-md"
              >
                {showForm ? 'Hide Form' : 'Add New Record'}
              </button>
              <button
                onClick={() => setShowDataTable(!showDataTable)}
                className="bg-forest-green text-white px-4 py-2 rounded-md hover:bg-forest-dark transition-colors shadow-md"
              >
                {showDataTable ? 'Hide Table' : 'View/Edit Records'}
              </button>
            </div>
          </div>

          <div className="text-sm text-nature-brown">
            Showing {filteredTranslocations.length} of {translocations.length} translocations
          </div>
        </div>

        {/* File Upload Section - More Prominent */}
        {showFileUpload && (
          <div className="mb-6">
            <FileUploadComponent 
              onFileUpload={importExcelFile}
              loading={uploadLoading}
              onCancel={() => setShowFileUpload(false)}
            />
          </div>
        )}

        {/* Data Table */}
        {showDataTable && (
          <div className="mb-6">
            <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-forest-green">
              <h3 className="text-xl font-bold mb-4 text-forest-dark flex items-center">
                Conservation Records ({filteredTranslocations.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-nature-light border-b-2 border-sage-green">
                      <th className="text-left p-2">Project</th>
                      <th className="text-left p-2">Year</th>
                      <th className="text-left p-2">Species</th>
                      <th className="text-left p-2">Animals</th>
                      <th className="text-left p-2">From → To</th>
                      <th className="text-left p-2">Transport</th>
                      <th className="text-left p-2">Special Project</th>
                      <th className="text-left p-2">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTranslocations.map((translocation) => (
                      <tr key={translocation.id} className="border-b hover:bg-nature-light">
                        <td className="p-2 font-medium">{translocation.project_title}</td>
                        <td className="p-2">{translocation.year}</td>
                        <td className="p-2">{translocation.species}</td>
                        <td className="p-2 text-center font-bold text-nature-green">{translocation.number_of_animals}</td>
                        <td className="p-2">
                          <div className="text-xs">
                            <div className="font-medium">{translocation.source_area.name}</div>
                            <div className="text-nature-brown">↓</div>
                            <div className="font-medium">{translocation.recipient_area.name}</div>
                          </div>
                        </td>
                        <td className="p-2">
                          {translocation.transport}
                        </td>
                        <td className="p-2">
                          {translocation.special_project && (
                            <span className="bg-forest-light text-forest-dark px-2 py-1 rounded text-xs">
                              {translocation.special_project}
                            </span>
                          )}
                        </td>
                        <td className="p-2">
                          <div className="flex gap-1">
                            <button
                              onClick={() => editTranslocation(translocation)}
                              className="bg-nature-green text-white px-2 py-1 rounded text-xs hover:bg-forest-green"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => deleteTranslocation(translocation.id)}
                              className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Add Form */}
        {showForm && (
          <div className="mb-6">
            <TranslocationForm 
              onSubmit={addTranslocation} 
              editingTranslocation={editingTranslocation}
              onCancel={cancelEdit}
            />
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Map */}
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg nature-shadow-lg border-l-4 border-nature-green">
              <h2 className="text-2xl font-bold mb-4 text-forest-dark flex items-center">
                Wildlife Translocation Map
              </h2>
              {filteredTranslocations.length > 0 ? (
                <MapComponent translocations={translocations} filteredTranslocations={filteredTranslocations} />
              ) : (
                <div className="w-full h-[32rem] bg-nature-light rounded-lg flex items-center justify-center border-2 border-sage-green">
                  <div className="text-center">
                    <div className="text-nature-brown text-lg font-medium mb-2">No translocations to display</div>
                    <div className="text-nature-brown text-sm mb-4">Load historical data to see conservation efforts across Africa</div>
                    {translocations.length === 0 && (
                      <button
                        onClick={importHistoricalData}
                        className="bg-forest-green text-white px-6 py-3 rounded-md hover:bg-forest-dark transition-colors shadow-md"
                      >
                        Load Historical Data
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
                Map Legend
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 rounded-full border-2 border-white opacity-80" style={{backgroundColor: '#228B22'}}></div>
                  <span className="text-forest-dark">Source Location</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-4 h-4 rounded-full border-2 border-black" style={{backgroundColor: '#228B22'}}></div>
                  <span className="text-forest-dark">Destination Location</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-1 opacity-60" style={{backgroundColor: '#228B22'}}></div>
                  <span className="text-forest-dark">Translocation Route</span>
                </div>
                <div className="mt-4 p-2 bg-nature-light rounded">
                  <div className="text-xs text-nature-brown mb-2">Species Color Legend:</div>
                  <div className="grid grid-cols-1 gap-1 text-xs">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#228B22'}}></div>
                      <span>Elephant</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#006400'}}></div>
                      <span>Black Rhino</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#90EE90'}}></div>
                      <span>White Rhino</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#32CD32'}}></div>
                      <span>Plains Game Species</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#8FBC8F'}}></div>
                      <span>Other Species</span>
                    </div>
                  </div>
                </div>
                <div className="mt-4 text-xs text-nature-brown bg-nature-light p-2 rounded">
                  Click map markers for detailed information about each translocation
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const FileUploadComponent = ({ onFileUpload, loading, onCancel }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragOver(false);
    const file = event.dataTransfer.files[0];
    setSelectedFile(file);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragOver(false);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onFileUpload(selectedFile);
    }
  };

  const isValidFile = selectedFile && (
    selectedFile.name.toLowerCase().endsWith('.xlsx') || 
    selectedFile.name.toLowerCase().endsWith('.xls') || 
    selectedFile.name.toLowerCase().endsWith('.csv') ||
    selectedFile.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
    selectedFile.type === 'application/vnd.ms-excel' ||
    selectedFile.type === 'text/csv'
  );

  // Debug logging
  console.log('FileUpload Debug:', {
    selectedFile: selectedFile ? {
      name: selectedFile.name,
      type: selectedFile.type,
      size: selectedFile.size
    } : 'None',
    isValidFile,
    loading
  });

  return (
    <div className="bg-white p-8 rounded-lg shadow-xl border-l-4 border-nature-green">
      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold text-forest-dark mb-2">Upload Your Excel Data</h3>
        <p className="text-nature-brown">Import your corrected conservation data with updated locations and coordinates</p>
      </div>
      
      <div 
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-all duration-300 ${
          dragOver 
            ? 'border-nature-green bg-nature-light transform scale-105' 
            : selectedFile
            ? 'border-forest-green bg-green-50'
            : 'border-sage-green hover:border-nature-green hover:bg-nature-light'
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {selectedFile ? (
          <div className="space-y-4">
            <div className="text-xl font-bold text-forest-dark">File Selected Successfully!</div>
            <div className="bg-white p-4 rounded-lg shadow-sm border border-green-200">
              <div className="text-lg font-semibold text-forest-dark">{selectedFile.name}</div>
              <div className="text-sm text-nature-brown mt-1">
                Size: {(selectedFile.size / 1024).toFixed(1)} KB | Type: {selectedFile.type || 'Excel/CSV'}
              </div>
            </div>
            {!isValidFile && (
              <div className="bg-red-100 border border-red-300 text-red-700 px-4 py-3 rounded-lg">
                <div className="flex items-center">
                  <div>
                    <strong>Invalid File Type</strong>
                    <p className="text-sm">Please select an Excel (.xlsx, .xls) or CSV (.csv) file</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <div className="text-xl font-bold text-forest-dark mb-2">
                Drag & Drop Your Excel File Here
              </div>
              <div className="text-nature-brown mb-4">
                or click below to browse and select your file
              </div>
              <div className="text-sm text-sage-green">
                Supports: Excel (.xlsx, .xls) and CSV (.csv) files up to 10MB
              </div>
            </div>
          </div>
        )}
        
        <input
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
        />
        
        {!selectedFile && (
          <label
            htmlFor="file-upload"
            className="inline-block mt-6 bg-gradient-to-r from-nature-green to-forest-green text-white px-8 py-4 rounded-lg hover:from-forest-green hover:to-forest-dark transition-all duration-300 cursor-pointer shadow-lg transform hover:scale-105 font-semibold"
          >
            Choose Your Excel File
          </label>
        )}
      </div>

      <div className="mt-8 space-y-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">Expected Column Structure:</h4>
          <div className="text-sm text-blue-700 space-y-1">
            <div><strong>Required:</strong> Project Title, Year, Species, Number</div>
            <div><strong>Location Data:</strong> Source Area: Name, Source Area: Co-Ordinates, Source Area: Country</div>
            <div><strong>Destination:</strong> Recipient Area: Name, Recipient Area: Co-Ordinates, Recipient Area: Country</div>
            <div><strong>Additional:</strong> Transport, Special Project, Additional Info</div>
          </div>
        </div>
        
        <div className="flex gap-4">
          <button
            onClick={handleUpload}
            disabled={!isValidFile || loading}
            className={`flex-1 py-4 px-6 rounded-lg font-bold text-lg transition-all duration-300 shadow-lg ${
              isValidFile && !loading
                ? 'bg-gradient-to-r from-nature-green to-forest-green text-white hover:from-forest-green hover:to-forest-dark transform hover:scale-105'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Processing...
              </div>
            ) : (
              'Import Data'
            )}
          </button>
          
          <button
            onClick={onCancel}
            className="px-8 py-4 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors font-semibold"
          >
            Cancel
          </button>
        </div>
        
        {selectedFile && !loading && (
          <div className="text-center">
            <button
              onClick={() => setSelectedFile(null)}
              className="text-nature-brown hover:text-forest-dark transition-colors underline"
            >
              Choose a different file
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;