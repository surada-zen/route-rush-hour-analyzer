const map = L.map("map").setView([37.7749, -122.4194], 12);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const fields = {
  originLat: document.getElementById("origin_lat"),
  originLng: document.getElementById("origin_lng"),
  destinationLat: document.getElementById("destination_lat"),
  destinationLng: document.getElementById("destination_lng"),
};

const statusText = document.getElementById("selection-status");

let originMarker = null;
let destinationMarker = null;

function resetSelections() {
  if (originMarker) {
    map.removeLayer(originMarker);
    originMarker = null;
  }

  if (destinationMarker) {
    map.removeLayer(destinationMarker);
    destinationMarker = null;
  }

  fields.originLat.value = "";
  fields.originLng.value = "";
  fields.destinationLat.value = "";
  fields.destinationLng.value = "";

  statusText.textContent = "Origin: not set | Destination: not set";
}

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
    originMarker = L.marker([lat, lng]).addTo(map).bindPopup("Origin");
    fields.originLat.value = latValue;
    fields.originLng.value = lngValue;
    updateStatus();
    return;
  }

  if (!destinationMarker) {
    destinationMarker = L.marker([lat, lng]).addTo(map).bindPopup("Destination");
    fields.destinationLat.value = latValue;
    fields.destinationLng.value = lngValue;
    updateStatus();
    return;
  }

  resetSelections();

  originMarker = L.marker([lat, lng]).addTo(map).bindPopup("Origin");
  fields.originLat.value = latValue;
  fields.originLng.value = lngValue;
  updateStatus();
});

// Route path display will be added next in a future update.
