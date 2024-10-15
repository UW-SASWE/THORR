var map = L.map("map", { maxZoom: 30 }).setView([46, -119], 6);
const apiKey =
  "AAPK229cfc7dca79439eb54c8254d040ad87zKPnxtgMrhMyWJxWoy2R-aE-hw-a8e9qTXhWBe91aI0ljMQoHb6IxAiJ_5Lu2ri7";
// const apiKey = esriApiKey;

function getV2Basemap(style) {
  return L.esri.Vector.vectorBasemapLayer(style, {
    apikey: apiKey,
    version: 2,
  });
}

const basemapLayers = {
  "Navigation": getV2Basemap("arcgis/navigation").addTo(map),
  "Satellite": getV2Basemap("arcgis/imagery"),
  "Street Map": getV2Basemap("arcgis/streets"),
  "Streets-Relief": getV2Basemap("arcgis/streets-relief"),

  // "arcgis/outdoor": getV2Basemap("arcgis/outdoor"),
  // "arcgis/community": getV2Basemap("arcgis/community"),
  // "arcgis/oceans": getV2Basemap("arcgis/oceans"),
  // "arcgis/topographic": getV2Basemap("arcgis/topographic"),
  // "arcgis/light-gray": getV2Basemap("arcgis/light-gray"),
  // "arcgis/dark-gray": getV2Basemap("arcgis/dark-gray"),
  // "arcgis/human-geography": getV2Basemap("arcgis/human-geography"),
  // "arcgis/charted-territory": getV2Basemap("arcgis/charted-territory"),
  // "arcgis/nova": getV2Basemap("arcgis/nova"),
  // "osm/standard": getV2Basemap("osm/standard"),
  // "osm/navigation": getV2Basemap("osm/navigation"),
  // "osm/streets": getV2Basemap("osm/streets"),
  // "osm/blueprint": getV2Basemap("osm/blueprint"),
};


L.control.layers(basemapLayers, null, { position: 'topleft' }).addTo(map);

info.addTo(map);

var preferredBasinID = "1";

document.addEventListener("DOMContentLoaded", (event) => {
  const myModal = new bootstrap.Modal("#howToNavigate");
  myModal.show();

  // if (
  //   localStorage.getItem("showHowToOnStart") == null ||
  //   localStorage.getItem("showHowToOnStart") == "true"
  // ) {
  //   document.getElementById("showHowToOnStartSwitch").checked = true;
  //   myModal.show();
  //   localStorage.setItem("showHowToOnStart", "true");
  // } else {
  //   document.getElementById("showHowToOnStartSwitch").checked = false;
  //   myModal.hide();
  //   localStorage.setItem("showHowToOnStart", "false");
  //   // console.log("hidden");
  // }
  // // console.log(localStorage.getItem("showHowToOnStart"));
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
