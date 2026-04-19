const map = L.map("map").setView([37.7749, -122.4194], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const fields = {
  originName: document.getElementById("origin_name"),
  destinationName: document.getElementById("destination_name"),
  originLat: document.getElementById("origin_lat"),
  originLng: document.getElementById("origin_lng"),
  destinationLat: document.getElementById("destination_lat"),
  destinationLng: document.getElementById("destination_lng"),
};

const statusText = document.getElementById("selection-status");
const geocoder = L.Control.Geocoder.nominatim();

let originMarker = null;
let destinationMarker = null;
let routeLine = null;

function removeRouteLine() {
  if (routeLine) {
    map.removeLayer(routeLine);
    routeLine = null;
  }
}

function drawPlaceholderRoute() {
  if (!originMarker || !destinationMarker) {
    return;
  }

  removeRouteLine();

  const routePoints = buildPlaceholderRoutePoints(
    originMarker.getLatLng(),
    destinationMarker.getLatLng(),
  );

  routeLine = L.polyline(routePoints, {
    color: "#2f6fed",
    weight: 4,
    opacity: 0.9,
    dashArray: "6, 6",
  }).addTo(map);

  map.fitBounds(routeLine.getBounds(), { padding: [24, 24] });
}

async function drawRouteLine() {
  if (!originMarker || !destinationMarker) {
    return;
  }

  const originPoint = originMarker.getLatLng();
  const destinationPoint = destinationMarker.getLatLng();

  removeRouteLine();

  try {
    // This step adds real route geometry from a routing API (OSRM).
    // Travel-time recommendations in Flask are still mock logic for now.
    // Real traffic-aware duration logic will be added in a later step.
    const routePoints = await fetchRoadRoutePoints(originPoint, destinationPoint);
    routeLine = L.polyline(routePoints, {
      color: "#2f6fed",
      weight: 4,
      opacity: 0.9,
    }).addTo(map);
  } catch (error) {
    // Fallback: keep the app working with placeholder route points if API fails.
    drawPlaceholderRoute();
    return;
  }

  map.fitBounds(routeLine.getBounds(), { padding: [24, 24] });
}

async function fetchRoadRoutePoints(originPoint, destinationPoint) {
  const apiUrl =
    `https://router.project-osrm.org/route/v1/driving/` +
    `${originPoint.lng},${originPoint.lat};${destinationPoint.lng},${destinationPoint.lat}` +
    `?overview=full&geometries=geojson`;

  const response = await fetch(apiUrl);
  if (!response.ok) {
    throw new Error(`Routing request failed with status ${response.status}`);
  }

  const data = await response.json();
  if (!data.routes || data.routes.length === 0 || !data.routes[0].geometry) {
    throw new Error("Routing response did not include route geometry");
  }

  return data.routes[0].geometry.coordinates.map(([lng, lat]) => [lat, lng]);
}

function buildPlaceholderRoutePoints(originPoint, destinationPoint) {
  const latDelta = destinationPoint.lat - originPoint.lat;
  const lngDelta = destinationPoint.lng - originPoint.lng;
  const distance = Math.sqrt(latDelta * latDelta + lngDelta * lngDelta);

  if (distance === 0) {
    return [originPoint, destinationPoint];
  }

  const normalLat = -lngDelta / distance;
  const normalLng = latDelta / distance;
  const curveAmount = Math.min(distance * 0.25, 0.02);

  const firstMidpoint = {
    lat: originPoint.lat + latDelta * 0.33 + normalLat * curveAmount,
    lng: originPoint.lng + lngDelta * 0.33 + normalLng * curveAmount,
  };
  const secondMidpoint = {
    lat: originPoint.lat + latDelta * 0.66 - normalLat * curveAmount * 0.6,
    lng: originPoint.lng + lngDelta * 0.66 - normalLng * curveAmount * 0.6,
  };

  return [originPoint, firstMidpoint, secondMidpoint, destinationPoint];
}

function resetSelections() {
  if (originMarker) {
    map.removeLayer(originMarker);
    originMarker = null;
  }

  if (destinationMarker) {
    map.removeLayer(destinationMarker);
    destinationMarker = null;
  }

  removeRouteLine();

  fields.originLat.value = "";
  fields.originLng.value = "";
  fields.destinationLat.value = "";
  fields.destinationLng.value = "";
  fields.originName.value = "";
  fields.destinationName.value = "";

  statusText.textContent = "Origin: not set | Destination: not set";
}

function updateMarker(markerType, lat, lng) {
  if (markerType === "origin") {
    if (originMarker) {
      originMarker.setLatLng([lat, lng]);
    } else {
      originMarker = L.marker([lat, lng]).addTo(map).bindPopup("Origin");
    }

    fields.originLat.value = lat.toFixed(6);
    fields.originLng.value = lng.toFixed(6);
    return;
  }

  if (destinationMarker) {
    destinationMarker.setLatLng([lat, lng]);
  } else {
    destinationMarker = L.marker([lat, lng]).addTo(map).bindPopup("Destination");
  }

  fields.destinationLat.value = lat.toFixed(6);
  fields.destinationLng.value = lng.toFixed(6);
}

function geocodeInput(markerType) {
  const inputField = markerType === "origin" ? fields.originName : fields.destinationName;
  const query = inputField.value.trim();

  if (!query) {
    return;
  }

  geocoder.geocode(query, (results) => {
    if (!results || results.length === 0) {
      return;
    }

    const firstResult = results[0];
    const resultCenter = firstResult.center;

    inputField.value = firstResult.name || query;
    updateMarker(markerType, resultCenter.lat, resultCenter.lng);
    drawRouteLine();
    updateStatus();

    if (!routeLine) {
      map.setView([resultCenter.lat, resultCenter.lng], 13);
    }
  });
}

function addSearchListener(inputField, markerType) {
  inputField.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") {
      return;
    }

    event.preventDefault();
    geocodeInput(markerType);
  });

  inputField.addEventListener("change", () => {
    geocodeInput(markerType);
  });
}

addSearchListener(fields.originName, "origin");
addSearchListener(fields.destinationName, "destination");

function updateStatus() {
  const originValue = fields.originLat.value
    ? `${fields.originLat.value}, ${fields.originLng.value}`
    : "not set";
  const destinationValue = fields.destinationLat.value
    ? `${fields.destinationLat.value}, ${fields.destinationLng.value}`
    : "not set";

  statusText.textContent = `Origin: ${originValue} | Destination: ${destinationValue}`;
}

map.on("click", (event) => {
  const { lat, lng } = event.latlng;
  const latValue = lat.toFixed(6);
  const lngValue = lng.toFixed(6);

  if (!originMarker) {
    updateMarker("origin", lat, lng);
    fields.originName.value = `(${latValue}, ${lngValue})`;
    updateStatus();
    return;
  }

  if (!destinationMarker) {
    updateMarker("destination", lat, lng);
    fields.destinationName.value = `(${latValue}, ${lngValue})`;
    drawRouteLine();
    updateStatus();
    return;
  }

  resetSelections();

  updateMarker("origin", lat, lng);
  fields.originName.value = `(${latValue}, ${lngValue})`;
  updateStatus();
});
