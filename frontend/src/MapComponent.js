import { useState, useEffect, useRef } from "react";

// Load Leaflet CSS and JS
const loadLeafletResources = () => {
  return new Promise((resolve) => {
    if (window.L) {
      resolve();
      return;
    }
    const cssLink = document.createElement('link');
    cssLink.rel = 'stylesheet';
    cssLink.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    cssLink.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    cssLink.crossOrigin = '';
    document.head.appendChild(cssLink);

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    script.crossOrigin = '';
    script.onload = () => {
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

const MapComponent = ({ translocations, filteredTranslocations }) => {
  const mapRef = useRef(null);
  
  useEffect(() => {
    const initializeMap = async () => {
      await loadLeafletResources();
      
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }

      // Create map centered on South Africa with enhanced zoom controls
      mapRef.current = window.L.map('map', {
        zoomControl: true,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        boxZoom: true,
        keyboard: true,
        dragging: true,
        touchZoom: true,
        zoomSnap: 0.5,
        zoomDelta: 0.5,
        wheelPxPerZoomLevel: 60,
        maxZoom: 18,
        minZoom: 2
      }).setView([-25, 28], 5);

      // Add enhanced zoom control with additional buttons
      const zoomControl = window.L.control.zoom({
        position: 'topright',
        zoomInTitle: 'Zoom In',
        zoomOutTitle: 'Zoom Out'
      });
      mapRef.current.addControl(zoomControl);

      // Add custom zoom to Africa button
      const zoomToAfricaControl = window.L.Control.extend({
        onAdd: function(map) {
          const container = window.L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
          container.style.backgroundColor = 'white';
          container.style.width = '80px';
          container.style.height = '30px';
          container.style.cursor = 'pointer';
          container.style.display = 'flex';
          container.style.alignItems = 'center';
          container.style.justifyContent = 'center';
          container.style.fontSize = '12px';
          container.style.fontWeight = 'bold';
          container.style.border = '1px solid #ccc';
          container.innerHTML = 'Reset View';
          container.title = 'Zoom to Africa';
          
          container.onclick = function() {
            map.setView([-15, 25], 4);
          };
          
          return container;
        }
      });
      
      mapRef.current.addControl(new zoomToAfricaControl({ position: 'topright' }));

      // English tile providers with better reliability
      const tileLayerOptions = [
        {
          url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          attribution: '© OpenStreetMap contributors',
          maxZoom: 19,
          language: 'en'
        },
        {
          url: 'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
          attribution: '© CartoDB, © OpenStreetMap contributors',
          maxZoom: 19
        },
        {
          url: 'https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.png',
          attribution: '© Stadia Maps, © OpenStreetMap contributors',
          maxZoom: 19
        },
        {
          url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
          attribution: '© Esri, © OpenStreetMap contributors',
          maxZoom: 19
        },
        {
          url: 'https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}',
          attribution: '© Google Maps',
          maxZoom: 19
        }
      ];

      const loadTileLayer = (index = 0) => {
        if (index >= tileLayerOptions.length) {
          console.warn('All tile providers failed, using enhanced geographic background');
          const canvas = document.createElement('canvas');
          canvas.width = 256;
          canvas.height = 256;
          const ctx = canvas.getContext('2d');
          
          // Create a detailed geographic background
          const gradient = ctx.createLinearGradient(0, 0, 0, 256);
          gradient.addColorStop(0, '#E6F3FF'); // Light blue (ocean)
          gradient.addColorStop(0.3, '#B8E6B8'); // Light green (coast)
          gradient.addColorStop(0.7, '#90EE90'); // Green (land)
          gradient.addColorStop(1, '#228B22'); // Dark green (mountains)
          
          ctx.fillStyle = gradient;
          ctx.fillRect(0, 0, 256, 256);
          
          // Add coordinate grid lines
          ctx.strokeStyle = '#DDD';
          ctx.lineWidth = 0.5;
          for (let i = 0; i <= 256; i += 32) {
            ctx.beginPath();
            ctx.moveTo(i, 0);
            ctx.lineTo(i, 256);
            ctx.moveTo(0, i);
            ctx.lineTo(256, i);
            ctx.stroke();
          }
          
          // Add "AFRICA" text for context
          ctx.font = '16px Arial';
          ctx.fillStyle = '#2F4F2F';
          ctx.textAlign = 'center';
          ctx.fillText('AFRICA', 128, 128);
          
          const dataUrl = canvas.toDataURL();
          window.L.tileLayer(dataUrl, {
            attribution: 'Basic Geographic Background - Africa Region',
            maxZoom: 19,
            tileSize: 256
          }).addTo(mapRef.current);
          return;
        }

        const tileLayer = window.L.tileLayer(tileLayerOptions[index].url, {
          attribution: tileLayerOptions[index].attribution,
          maxZoom: tileLayerOptions[index].maxZoom,
          crossOrigin: true
        });

        tileLayer.on('tileerror', () => {
          console.warn(`Tile provider ${index} failed, trying next...`);
          tileLayer.remove();
          loadTileLayer(index + 1);
        });

        tileLayer.on('tileload', () => {
          console.log(`Successfully loaded tiles from provider ${index}`);
        });

        tileLayer.addTo(mapRef.current);
      };

      loadTileLayer();
    };
    
    initializeMap();
    
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);
  
  // Update markers when filtered data changes
  useEffect(() => {
    if (!mapRef.current) return;
    
    // Clear existing markers and layers
    mapRef.current.eachLayer(layer => {
      if (layer instanceof window.L.Marker || 
          layer instanceof window.L.Polyline || 
          layer instanceof window.L.CircleMarker) {
        if (!layer.options.permanent) { // Don't remove tile layers
          mapRef.current.removeLayer(layer);
        }
      }
    });
    
    // Species colors for simplified categorization - GREEN CONSERVATION THEME
    const speciesColors = {
      'Elephant': '#228B22',           // Forest Green
      'Black Rhino': '#006400',       // Dark Green  
      'White Rhino': '#90EE90',       // Light Green
      'Plains Game Species': '#32CD32', // Lime Green
      'Lion': '#8FBC8F',              // Dark Sea Green
      'Buffalo': '#9ACD32',           // Yellow Green
      'Hippo': '#6B8E23',             // Olive Drab
      'Giraffe': '#228B22',           // Forest Green
      'Zebra': '#32CD32',             // Lime Green
      'Kudu': '#8FBC8F',              // Dark Sea Green
      'Sable': '#006400',             // Dark Green
      'Impala': '#90EE90',            // Light Green
      'Waterbuck': '#9ACD32',         // Yellow Green
      'Unknown': '#696969'            // Dim Gray
    };

    const getSpeciesColor = (species) => {
      return speciesColors[species] || '#228B22'; // Default to Forest Green
    };

    // Transport mode icons
    const getTransportIcon = (mode) => {
      return mode === 'Air' ? 'Air' : 'Road';
    };

    const bounds = [];

    filteredTranslocations.forEach((translocation) => {
      // Parse coordinates - ENHANCED for Google Maps format with proper validation
      const parseCoordinates = (coordString) => {
        if (!coordString || coordString === "" || coordString === "0, 0") return [0, 0];
        try {
          // Handle Google Maps format: "-27.808400634565363, 32.34692072433984"
          const cleanCoords = coordString.replace(/[°'"]/g, "").trim();
          const coords = cleanCoords.split(",");
          
          if (coords.length >= 2) {
            const lat = parseFloat(coords[0].trim());
            const lng = parseFloat(coords[1].trim());
            
            console.log(`Map parsing: "${coordString}" → lat: ${lat}, lng: ${lng}`);
            
            // Validate coordinates are within valid global ranges
            // Latitude: -90 to 90, Longitude: -180 to 180
            if (!isNaN(lat) && !isNaN(lng) && 
                lat >= -90 && lat <= 90 && 
                lng >= -180 && lng <= 180) {
              console.log(`✅ Valid coordinates for map: [${lat}, ${lng}]`);
              return [lat, lng];
            } else {
              console.warn(`❌ Invalid coordinates for map: lat=${lat}, lng=${lng} from "${coordString}"`);
              return [0, 0];
            }
          }
        } catch (error) {
          console.error('❌ Error parsing coordinates for map:', coordString, error);
        }
        return [0, 0];
      };

      const [sourceLat, sourceLng] = parseCoordinates(translocation.source_area.coordinates);
      const [destLat, destLng] = parseCoordinates(translocation.recipient_area.coordinates);

      // IMMEDIATE DEBUG - Log what we're actually plotting
      console.log(`🗺️ PLOTTING: ${translocation.project_title}`);
      console.log(`   Source: ${translocation.source_area.name} at [${sourceLat}, ${sourceLng}]`);
      console.log(`   Destination: ${translocation.recipient_area.name} at [${destLat}, ${destLng}]`);

      // Skip if coordinates are invalid (0,0)
      if ((sourceLat === 0 && sourceLng === 0) || (destLat === 0 && destLng === 0)) {
        console.warn(`⚠️ Skipping ${translocation.project_title} - invalid coordinates`);
        return;
      }

      // Skip invalid coordinates
      if (sourceLat === 0 && sourceLng === 0 && destLat === 0 && destLng === 0) {
        return;
      }

      const speciesColor = getSpeciesColor(translocation.species);

      // Source marker (larger, white border)
      const sourceMarker = window.L.circleMarker([sourceLat, sourceLng], {
        radius: 10,
        fillColor: speciesColor,
        color: '#ffffff',
        weight: 3,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(mapRef.current);
      
      sourceMarker.bindTooltip(`Source: ${translocation.source_area.name}`);

      // Destination marker (smaller, black border)
      const destMarker = window.L.circleMarker([destLat, destLng], {
        radius: 7,
        fillColor: speciesColor,
        color: '#000000',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
      }).addTo(mapRef.current);
      
      destMarker.bindTooltip(`Destination: ${translocation.recipient_area.name}`);

      // Connection line with proper styling and detailed popup
      const polyline = window.L.polyline([[sourceLat, sourceLng], [destLat, destLng]], {
        color: speciesColor,
        weight: 4,
        opacity: 0.8,
        dashArray: translocation.transport === 'Air' ? '10, 5' : null
      }).addTo(mapRef.current);

      // Enhanced line popup with complete translocation details
      const linePopupContent = `
        <div style="padding: 15px; min-width: 280px; max-width: 350px;">
          <h3 style="font-weight: bold; font-size: 18px; margin-bottom: 12px; color: ${speciesColor}; border-bottom: 2px solid ${speciesColor}; padding-bottom: 5px;">
            ${translocation.project_title}
          </h3>
          
          <div style="margin-bottom: 12px;">
            <p style="margin: 4px 0;"><strong>Species:</strong> ${translocation.species}</p>
            <p style="margin: 4px 0;"><strong>Number of Animals:</strong> ${translocation.number_of_animals}</p>
            <p style="margin: 4px 0;"><strong>Year:</strong> ${translocation.year}</p>
            <p style="margin: 4px 0;"><strong>Transport:</strong> ${getTransportIcon(translocation.transport)} ${translocation.transport}</p>
          </div>

          <div style="margin-bottom: 12px;">
            <h4 style="font-weight: bold; color: #2F5F3F; margin: 8px 0 4px 0;">Source Location:</h4>
            <p style="margin: 2px 0; color: #444;">📍 ${translocation.source_area.name}</p>
            <p style="margin: 2px 0; color: #666; font-size: 12px;">🌍 ${translocation.source_area.country}</p>
            <p style="margin: 2px 0; color: #666; font-size: 11px;">📌 ${translocation.source_area.coordinates}</p>
          </div>

          <div style="margin-bottom: 12px;">
            <h4 style="font-weight: bold; color: #2F5F3F; margin: 8px 0 4px 0;">Destination Location:</h4>
            <p style="margin: 2px 0; color: #444;">📍 ${translocation.recipient_area.name}</p>
            <p style="margin: 2px 0; color: #666; font-size: 12px;">🌍 ${translocation.recipient_area.country}</p>
            <p style="margin: 2px 0; color: #666; font-size: 11px;">📌 ${translocation.recipient_area.coordinates}</p>
          </div>

          ${translocation.special_project ? `
          <div style="margin-bottom: 8px;">
            <p style="margin: 4px 0;"><strong>Special Project:</strong> <span style="color: ${speciesColor};">${translocation.special_project}</span></p>
          </div>
          ` : ''}

          ${translocation.additional_info ? `
          <div style="margin-bottom: 8px; border-top: 1px solid #eee; padding-top: 8px;">
            <h4 style="font-weight: bold; color: #2F5F3F; margin: 4px 0;">Additional Information:</h4>
            <p style="margin: 4px 0; color: #555; font-style: italic;">${translocation.additional_info}</p>
          </div>
          ` : ''}

          <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #eee; font-size: 11px; color: #888;">
            <p>Click markers for location-specific details</p>
          </div>
        </div>
      `;

      polyline.bindPopup(linePopupContent);
      polyline.bindTooltip(`${translocation.project_title}: ${translocation.number_of_animals} ${translocation.species}`);

      // Popups
      const sourcePopupContent = `
        <div style="padding: 10px; min-width: 220px;">
          <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: ${speciesColor};">${translocation.source_area.name}</h3>
          <p><strong>Project:</strong> ${translocation.project_title}</p>
          <p><strong>Species:</strong> ${translocation.species}</p>
          <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
          <p><strong>Year:</strong> ${translocation.year}</p>
          <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport)} ${translocation.transport}</p>
          <p><strong>Role:</strong> Source Location</p>
          ${translocation.special_project ? `<p><strong>Special Project:</strong> ${translocation.special_project}</p>` : ''}
          ${translocation.additional_info ? `<p><strong>Notes:</strong> ${translocation.additional_info}</p>` : ''}
        </div>
      `;

      const destPopupContent = `
        <div style="padding: 10px; min-width: 220px;">
          <h3 style="font-weight: bold; font-size: 16px; margin-bottom: 8px; color: ${speciesColor};">${translocation.recipient_area.name}</h3>
          <p><strong>Project:</strong> ${translocation.project_title}</p>
          <p><strong>Species:</strong> ${translocation.species}</p>
          <p><strong>Animals:</strong> ${translocation.number_of_animals}</p>
          <p><strong>Year:</strong> ${translocation.year}</p>
          <p><strong>Transport:</strong> ${getTransportIcon(translocation.transport)} ${translocation.transport}</p>
          <p><strong>Role:</strong> Destination Location</p>
          ${translocation.special_project ? `<p><strong>Special Project:</strong> ${translocation.special_project}</p>` : ''}
          ${translocation.additional_info ? `<p><strong>Notes:</strong> ${translocation.additional_info}</p>` : ''}
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
        mapRef.current.setView([-15, 25], 4);
      }
    }
  }, [filteredTranslocations]);

  return <div id="map" className="w-full h-[32rem] rounded-lg shadow-lg"></div>;
};

export default MapComponent;