function initAdminMap() {

  const mapDiv = document.getElementById("admin-map");
  const latField = document.getElementById("id_latitude");
  const lngField = document.getElementById("id_longitude");

  if (!mapDiv || !latField || !lngField) return;
  if (!window.google || !google.maps) return;

  // ⭐⭐⭐⭐⭐ FIX CRÍTICO ADMIN ⭐⭐⭐⭐⭐
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

    const location = { lat, lng };

    const map = new google.maps.Map(mapDiv, {
      center: location,
      zoom: latField.value ? 15 : 14,
      mapTypeId: "roadmap",

      // ⭐ FORÇAR RASTER → evita UNINITIALIZED ⭐
      ...(google.maps.RenderingType && {
        renderingType: google.maps.RenderingType.RASTER
      })
    });

    const marker = new google.maps.Marker({
      position: location,
      map: map,
      draggable: true,
      title: "Local selecionado",
    });

    marker.addListener("dragend", (event) => {
      latField.value = event.latLng.lat().toFixed(6);
      lngField.value = event.latLng.lng().toFixed(6);
    });

    map.addListener("click", (event) => {
      marker.setPosition(event.latLng);
      latField.value = event.latLng.lat().toFixed(6);
      lngField.value = event.latLng.lng().toFixed(6);
    });

    // ⭐ FIX FINAL ⭐
    requestAnimationFrame(() => {
      google.maps.event.trigger(map, "resize");
      map.setCenter(location);
    });
  };

  waitForLayout();
}

// ⭐ Melhor trigger no Admin ⭐
window.addEventListener("load", () => {
  setTimeout(initAdminMap, 500);
});
