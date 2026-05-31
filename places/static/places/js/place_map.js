function initAdminMap() {
  const mapDiv = document.getElementById("admin-map");
  const latField = document.getElementById("id_latitude");
  const lngField = document.getElementById("id_longitude");

  if (!mapDiv || !latField || !lngField) return;
  if (!window.L) return;

  const waitForLayout = () => {
    const rect = mapDiv.getBoundingClientRect();

    if (rect.width === 0 || rect.height === 0) {
      requestAnimationFrame(waitForLayout);
      return;
    }

    if (mapDiv.dataset.loaded) return;
    mapDiv.dataset.loaded = "true";

    const parseCoordinate = (value) => {
      if (!value) return NaN;
      return parseFloat(String(value).trim().replace(",", "."));
    };

    let lat = parseCoordinate(latField.value);
    let lng = parseCoordinate(lngField.value);

    if (isNaN(lat)) lat = 41.705098;
    if (isNaN(lng)) lng = -8.791817;

    const location = [lat, lng];

    const map = L.map(mapDiv).setView(location, latField.value ? 15 : 14);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
      maxZoom: 19,
      subdomains: "abcd",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(map);

    const marker = L.marker(location, {
      draggable: true,
      title: "Local selecionado",
    }).addTo(map);

    const setFields = (newLocation) => {
      latField.value = newLocation.lat.toFixed(6);
      lngField.value = newLocation.lng.toFixed(6);
    };

    marker.on("dragend", (event) => {
      setFields(event.target.getLatLng());
    });

    map.on("click", (event) => {
      marker.setLatLng(event.latlng);
      setFields(event.latlng);
    });

    requestAnimationFrame(() => {
      map.invalidateSize();
      map.setView(location);
    });
  };

  waitForLayout();
}

window.addEventListener("load", () => {
  setTimeout(initAdminMap, 500);
});
