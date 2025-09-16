var map = L.map("map", { maxZoom: 30 }).setView([46, -119], 6);

const basemapLayers = {
  "Street Map": L.tileLayer(
    "https://mt0.google.com/vt/lyrs=m&x={x}&y={y}&z={z}&hl=en",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }
  ).addTo(map),
  Satellite: L.tileLayer(
    "https://mt0.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&hl=en"
  ),
  Terrain: L.tileLayer(
    "https://mt0.google.com/vt/lyrs=p&x={x}&y={y}&z={z}&hl=en"
  ),
};

L.control.layers(basemapLayers, null, { position: "topleft" }).addTo(map);

info.addTo(map);

var preferredBasinID = "1";

document.addEventListener("DOMContentLoaded", (event) => {
  const myModal = new bootstrap.Modal("#howToNavigate");
  myModal.show();
});

window.onload = function () {
  loadBasins(preferredBasinID);
  var selectedBasin = document.getElementById("basin-selector").value;
  var selectedRiver = document.getElementById("river-selector").value;

  const t = new Date(); // Get the current date and time
  const z = t.getTimezoneOffset() * 60 * 1000; // Convert the local time zone offset from minutes to milliseconds
  const tLocal = new Date(t - z); // Subtract the offset from the original date
  const todayIso = tLocal.toISOString().split("T")[0]; // Convert to ISO format and remove the time

  // set the max of start and end dates to today
  document.getElementById("start-date").max = todayIso;
  document.getElementById("end-date").max = todayIso;

  if (preferredBasinID) {
    loadBasinGeom(preferredBasinID);
    loadReachesGeomChunk(preferredBasinID, 750);
    loadRivers(preferredBasinID);
    loadReaches(preferredBasinID, selectedRiver);
    loadDams(preferredBasinID, selectedRiver);
    // loadDamsGeom(preferredBasinID);
    loadDamsPoints(preferredBasinID);

    var legend = L.control({ position: "topright" });

    legend.onAdd = function (map) {
      var div = L.DomUtil.create("div", "info legend");
      var grades = [0, 5, 10, 15, 20, 25, 30];
      var labels = ["<strong>Temperature (&deg;C)</strong>"];
      var from, to;

      for (var i = 0; i < grades.length; i++) {
        from = grades[i];
        to = grades[i + 1];

        labels.push(
          '<i style="background:' +
            temperatureColorScale(from + 1) +
            '"></i> ' +
            from +
            (to ? "&ndash;" + to : "+")
        );
      }

      div.innerHTML = labels.join("<br>");
      return div;
    };

    legend.addTo(map);
  } else {
    loadRivers(selectedBasin);
    loadReaches(selectedBasin, selectedRiver);
    loadDams(selectedBasin, selectedRiver);
  }
};
