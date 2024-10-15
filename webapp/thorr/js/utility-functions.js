var selectedFeature = {
  type: null,
  id: null,
  data: null,
};
// global variable to store the selected feature type and ID

function loadBasins(priorityBasinID) {
  var formData = new FormData();
  formData.append("priorityBasinID", priorityBasinID);

  fetch("php/loadBasins.php", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((responseText) => {
      document.getElementById("basin-selector").innerHTML = responseText;
    })
    .catch((error) => console.error("Error:", error));
}

function loadRivers(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadRivers.php", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((responseText) => {
      document.getElementById("river-selector").innerHTML = responseText;
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     document.getElementById("river-selector").innerHTML = this.responseText;
  //   }
  // };

  // xmlhttp.open("POST", "php/loadRivers.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID);
}

function loadReaches(BasinID, RiverID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);
  formData.append("RiverID", RiverID);

  fetch("php/loadReaches.php", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((responseText) => {
      document.getElementById("reach-selector").innerHTML = responseText;
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     document.getElementById("reach-selector").innerHTML = this.responseText;
  //   }
  // };

  // xmlhttp.open("POST", "php/loadReaches.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID + "&RiverID=" + RiverID);
}

function loadDams(BasinID, RiverID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadDams.php", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.text())
    .then((responseText) => {
      document.getElementById("dam-selector").innerHTML = responseText;
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     document.getElementById("dam-selector").innerHTML = this.responseText;
  //   }
  // };

  // xmlhttp.open("POST", "php/loadDams.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID + "&RiverID=" + RiverID);
}

function loadBasinGeom(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadBasinGeom.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var geoJSON = JSON.parse(responseText);
      var layer = L.geoJSON(geoJSON, { style: basinStyle }).addTo(map);
    })
    .catch((error) => console.error("Error:", error));
}

function loadRiversGeom(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadRiversGeom.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var geoJSON = JSON.parse(responseText);
      var layer = L.geoJSON(geoJSON).addTo(map);
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     var geoJSON = JSON.parse(this.responseText);
  //     var layer = L.geoJSON(geoJSON).addTo(map);
  //   }
  // };
  // xmlhttp.open("POST", "php/loadRiversGeom.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID);
}

function loadReachesGeom(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadReachesGeom.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var geoJSON = JSON.parse(responseText);
      var layer = L.geoJSON(geoJSON).addTo(map);
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     // console.log(this.responseText);
  //     var geoJSON = JSON.parse(this.responseText);
  //     var layer = L.geoJSON(geoJSON).addTo(map);
  //   }
  // };
  // xmlhttp.open("POST", "php/loadReachesGeom.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID);
}

// function to load the reaches geometry in chunks
function loadReachesGeomChunk(BasinID, row_count) {
  var geoJSON = {
    type: "FeatureCollection",
    features: [],
  };

  offset = 0;
  info.showLoading();

  function http(BasinID, offset, row_count) {
    var formData = new FormData();
    formData.append("BasinID", BasinID);
    formData.append("offset", offset);
    formData.append("row_count", row_count);

    fetch("php/loadReachesGeom.php", {
      method: "POST",
      body: formData,
    })
      // .then((response) => response.text())
      .then((response) => response.text())
      .then((responseText) => {
        onHttpDone(responseText);
      })
      .catch((error) => console.error("Error:", error));
  }

  function onHttpDone(responseText) {
    var _geoJSON = JSON.parse(responseText);
    geoJSON.features = geoJSON.features.concat(_geoJSON.features);

    if (_geoJSON.features.length == 0) {
      reachesLayer = L.geoJSON(geoJSON, {
        style: reachStyle,
        onEachFeature: onEachReachFeature,
      }).addTo(map);
      info.update();
      return;
    } else {
      // console.log(_geoJSON.features.length);
      offset += row_count;
      http(BasinID, offset, row_count);
    }
  }

  http(BasinID, offset, row_count);
}

function loadDamsGeom(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadDamsGeom.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var geoJSON = JSON.parse(responseText);
      damsLayer = L.geoJSON(geoJSON, {
        style: damStyle,
        onEachFeature: onEachDamFeature,
      }).addTo(map);
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     var geoJSON = JSON.parse(this.responseText);
  //     damsLayer = L.geoJSON(geoJSON, {
  //       style: damStyle,
  //       onEachFeature: onEachDamFeature,
  //     }).addTo(map);
  //   }
  // };
  // xmlhttp.open("POST", "php/loadDamsGeom.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("BasinID=" + BasinID);
}

var damsPointsLayer;

function loadDamsPoints(BasinID) {
  var formData = new FormData();
  formData.append("BasinID", BasinID);

  fetch("php/loadDamsPoints.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var LeafIcon = L.Icon.extend({
        options: {},
      });

      var markercluster = L.markerClusterGroup({
        showCoverageOnHover: false,
        maxClusterRadius: 50,
        iconCreateFunction: function (cluster) {
          return new LeafIcon({
            iconUrl: "resources/dam_icon.png",
          });
        },
      });

      var geoJSON = JSON.parse(responseText);
      // console.log(geoJSON);
      damsPointsLayer = L.geoJSON(geoJSON, {
        // convert the onEachFeature function into a proper function
        onEachFeature: function (feature, layer) {
          layer.on({
            // convert the mouseover event into a proper function
            mouseover: function (e) {
              var layer = e.target;
              info.update(layer.feature.properties);
            },
            mouseout: resetDamHighlight,
            // convert the click event into a proper function
            click: function (e) {
              // update the selected feature
              if (
                selectedFeature.type == "dam" &&
                selectedFeature.id == e.target.feature.properties.DamID
              ) {
                return;
              } else {
                selectedFeature = {
                  type: "dam",
                  id: e.target.feature.properties.DamID,
                  data: fetchFeaturePlotData(
                    "dam",
                    e.target.feature.properties.DamID
                  ),
                };
              }

              // map.fitBounds(e.target.getBounds().pad(0.25));
              updateInfoPanelTitle(e.target.feature.properties);
              var mapHeight = document.getElementById("map").style.height;
              setTimeout(function () {
                if (mapHeight == "100vh") {
                  document.getElementById("map").style.height = "60vh";
                }
                document.getElementById("info-panel").classList.add("show");
                window.map.invalidateSize();
                window.dispatchEvent(new Event("resize"));
              }, 400);
            },
          });
        },
        pointToLayer: function (feature, latlng) {
          return L.marker(latlng, {
            icon: new LeafIcon({
              iconUrl: "resources/dam_icon.png",
            }),
          });
          // .bindPopup(feature.properties.Name + " dam");
        },
      });
      markercluster.addLayer(damsPointsLayer);
      markercluster.addTo(map);
    })
    .catch((error) => console.error("Error:", error));
}

// get bound of a reach or dam feature
function zoomToFeatureBounds(type, id, updateTitle = true) {
  var formData = new FormData();
  formData.append("type", type);
  formData.append("id", id);

  fetch("php/getFeatureBounds.php", {
    method: "POST",
    body: formData,
  })
    // .then((response) => response.text())
    .then((response) => response.text())
    .then((responseText) => {
      var geoJSON = JSON.parse(responseText);
      // var l = L.geoJSON(geoJSON);
      window.map.fitBounds(L.geoJSON(geoJSON).getBounds().pad(0.25));

      if (updateTitle) {
        updateInfoPanelTitle(geoJSON.features[0].properties);
      }
      var mapHeight = document.getElementById("map").style.height;
      setTimeout(function () {
        if (mapHeight == "100vh") {
          document.getElementById("map").style.height = "60vh";
        }
        document.getElementById("info-panel").classList.add("show");
        window.map.invalidateSize();
        window.dispatchEvent(new Event("resize"));
      }, 400);
    })
    .catch((error) => console.error("Error:", error));

  // var xmlhttp = new XMLHttpRequest();
  // xmlhttp.onreadystatechange = function () {
  //   if (this.readyState == 4 && this.status == 200) {
  //     // console.log(this.responseText);
  //     var geoJSON = JSON.parse(this.responseText);
  //     // var l = L.geoJSON(geoJSON);
  //     window.map.fitBounds(L.geoJSON(geoJSON).getBounds().pad(0.25));

  //     if (updateTitle) {
  //       updateInfoPanelTitle(geoJSON.features[0].properties);
  //     }
  //     var mapHeight = document.getElementById("map").style.height;
  //     setTimeout(function () {
  //       if (mapHeight == "100vh") {
  //         document.getElementById("map").style.height = "60vh";
  //       }
  //       document.getElementById("info-panel").classList.add("show");
  //       window.map.invalidateSize();
  //       window.dispatchEvent(new Event("resize"));
  //     }, 400);
  //   }
  // };

  // xmlhttp.open("POST", "php/getFeatureBounds.php", true);
  // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  // xmlhttp.send("type=" + type + "&id=" + id);
}

// leaflet style functions
function temperatureColorScale(temp) {
  return temp > 30
    ? "#d73027"
    : temp > 25
    ? "#fc8d59"
    : temp > 20
    ? "#fee090"
    : temp > 15
    ? "#ffffbf"
    : temp > 10
    ? "#e0f3f8"
    : temp > 5
    ? "#91bfdb"
    : "#4575b4  ";
}

function reachStyle(feature) {
  return {
    // color: temperatureColorScale(feature.properties.Temperature),
    color: temperatureColorScale(feature.properties.EstTempC),
    weight: 3.5,
    opacity: 0.75,
  };
}

function basinStyle(feature) {
  return {
    color: "#0000ff",
    weight: 2,
    opacity: 0.3,
    fillOpacity: 0.15,
  };
}

function damStyle(feature) {
  return {
    color: "#87cefa",
    weight: 1,
    opacity: 0.3,
    // fillColor: temperatureColorScale(feature.properties.Temperature),
    fillColor: temperatureColorScale(feature.properties.EstTempC),
    fillOpacity: 0.75,
  };
}

// Leaflet map interaction functions

// Interaction functions for the reaches layer
var reachesLayer;

function highlightReachFeature(e) {
  var layer = e.target;

  layer.setStyle({
    weight: 10,
    fillOpacity: 0.9,
  });

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    layer.bringToFront();
  }
  info.update(layer.feature.properties);
}

function resetReacheHighlight(e) {
  reachesLayer.resetStyle(e.target);
  info.update();
}

function clickReachFeature(e) {
  // update the selected feature
  if (
    selectedFeature.type == "reach" &&
    selectedFeature.id == e.target.feature.properties.ReachID
  ) {
    return;
  } else {
    selectedFeature = {
      type: "reach",
      id: e.target.feature.properties.ReachID,
      data: fetchFeaturePlotData("reach", e.target.feature.properties.ReachID),
    };
  }

  map.fitBounds(e.target.getBounds().pad(0.5));
  updateInfoPanelTitle(e.target.feature.properties);
  var mapHeight = document.getElementById("map").style.height;
  setTimeout(function () {
    if (mapHeight == "100vh") {
      document.getElementById("map").style.height = "60vh";
    }
    document.getElementById("info-panel").classList.add("show");
    window.map.invalidateSize();
    window.dispatchEvent(new Event("resize"));
  }, 400);
}

function onEachReachFeature(feature, layer) {
  layer.on({
    mouseover: highlightReachFeature,
    mouseout: resetReacheHighlight,
    click: clickReachFeature,
  });
}

// Interaction functions for the dams layer
var damsLayer;

function highlightDamFeature(e) {
  var layer = e.target;

  layer.setStyle({
    weight: 3,
    color: "#00008b",
    fillOpacity: 0.85,
  });

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    layer.bringToFront();
  }
  info.update(layer.feature.properties);
}

function resetDamHighlight(e) {
  // damsLayer.resetStyle(e.target);
  info.update();
}

function clickDamFeature(e) {
  // update the selected feature
  if (
    selectedFeature.type == "dam" &&
    selectedFeature.id == e.target.feature.properties.DamID
  ) {
    return;
  } else {
    selectedFeature = {
      type: "dam",
      id: e.target.feature.properties.ReachID,
      data: fetchFeaturePlotData("dam", e.target.feature.properties.DamID),
    };
  }

  map.fitBounds(e.target.getBounds().pad(0.25));
  updateInfoPanelTitle(e.target.feature.properties);
  var mapHeight = document.getElementById("map").style.height;
  setTimeout(function () {
    if (mapHeight == "100vh") {
      document.getElementById("map").style.height = "60vh";
    }
    document.getElementById("info-panel").classList.add("show");
    window.map.invalidateSize();
    window.dispatchEvent(new Event("resize"));
  }, 400);
}

function onEachDamFeature(feature, layer) {
  layer.on({
    mouseover: highlightDamFeature,
    mouseout: resetDamHighlight,
    click: clickDamFeature,
  });
}

// control that shows state info on hover
var info = L.control();

info.onAdd = function (map) {
  this._div = L.DomUtil.create("div", "info");
  this.update();
  return this._div;
};

info.update = function (props) {
  this._div.innerHTML =
    "<h4>Water Temperature</h4>" +
    (props
      ? "<b>" +
        (props.DamID
          ? props.Name
          : props.Name +
            " (RKm: " +
            props.RKm +
            " - " +
            (Number(props.RKm) + 10) +
            ")") +
        "</b><br />" +
        "Latest estimate (" +
        // "<br />(" +
        // props.startDate +
        props.Date +
        // " - " +
        // props.endDate +
        "):<br />" +
        // props.Temperature +
        (props.DamID ? props.WaterTempC : props.EstTempC) +
        " &deg;C"
      : "Hover over a reach or dam");
};

// method to show the loading in the info control
info.showLoading = function () {
  this._div.innerHTML =
    "<h4>Water Temperature</h4>" +
    '<div class="d-flex align-items-center"><div class="spinner-border spinner-border-sm text-secondary p-2" role="status"><span class="visually-hidden">Loading...</span></div><span class="p-2 align-self-center">Loading Latest Estimates</span><br />';
};

// Information panel functions
function updateInfoPanelTitle(props) {
  var title = document.getElementById("info-panel-title");
  title.innerHTML = props
    ? props.DamID
      ? props.Name
      : props.Name +
        " (RKm: " +
        props.RKm +
        " - " +
        (Number(props.RKm) + 10) +
        ")"
    : "Click on a reach or dam";
}

function toggleMapHeight() {
  var map = document.getElementById("map");
  var mapHeight = map.style.height;
  setTimeout(function () {
    if (mapHeight == "100vh") {
      map.style.height = "60vh";
    } else {
      map.style.height = "100vh";
    }
    window.map.invalidateSize();
    window.dispatchEvent(new Event("resize"));
  }, 400);
}

// invalidate the map size to fix the map not showing up
function invalidateMapSize() {
  // var map = document.getElementById("map");
  setTimeout(function () {
    window.map.invalidateSize();
    window.dispatchEvent(new Event("resize"));
  }, 400);
}

// when the basin option is selected
function onBasinSelectorChange() {
  var selectedBasin = document.getElementById("basin-selector").value;

  loadRivers(selectedBasin);
  loadReaches(selectedBasin, "");
  loadDams(selectedBasin, "");
  loadDamsPoints(selectedBasin, "");

  zoomToFeatureBounds("basin", selectedBasin, false);
}

// when the river option is selelcted
function onRiverSelectorChange() {
  var selectedBasin = document.getElementById("basin-selector").value;
  var selectedRiver = document.getElementById("river-selector").value;

  loadReaches(selectedBasin, selectedRiver);
  loadDams(selectedBasin, selectedRiver);

  zoomToFeatureBounds("river", selectedRiver, false);
}

// when reaches or dam options are selected, update the map
function onReachSelectorChange() {
  var damSelector = document.getElementById("dam-selector");
  damSelector.value = "";

  if (
    selectedFeature.type == "reach" &&
    selectedFeature.id == document.getElementById("reach-selector").value
  ) {
    return;
  } else {
    selectedFeature = {
      type: "reach",
      id: document.getElementById("reach-selector").value,
      data: fetchFeaturePlotData(
        "reach",
        document.getElementById("reach-selector").value
      ),
    };
    zoomToFeatureBounds(selectedFeature.type, selectedFeature.id);
  }
}

function onDamSelectorChange() {
  var reachSelector = document.getElementById("reach-selector");
  reachSelector.value = "";

  // update the selected feature
  if (
    selectedFeature.type == "dam" &&
    selectedFeature.id == document.getElementById("dam-selector").value
  ) {
    return;
  } else {
    selectedFeature = {
      type: "dam",
      id: document.getElementById("dam-selector").value,
      data: fetchFeaturePlotData(
        "dam",
        document.getElementById("dam-selector").value
      ),
    };
    zoomToFeatureBounds(selectedFeature.type, selectedFeature.id);
  }
}

// fetch plotting data from the database
function fetchFeaturePlotData(type, id) {
  if (type == "reach") {
    var formData = new FormData();
    formData.append("ReachID", id);

    fetch("php/reachPlotData.php", {
      method: "POST",
      body: formData,
    })
      // .then((response) => response.text())
      .then((response) => response.text())
      .then((responseText) => {
        selectedFeature.data = JSON.parse(responseText);
        plotData();
      })
      .catch((error) => console.error("Error:", error));

    // var xmlhttp = new XMLHttpRequest();
    // xmlhttp.onreadystatechange = function () {
    //   if (this.readyState == 4 && this.status == 200) {
    //     // console.log(this.responseText)
    //     selectedFeature.data = JSON.parse(this.responseText);
    //     // console.log(selectedFeature.data)
    //     plotData();
    //   }
    // };
    // xmlhttp.open("POST", "php/reachPlotData.php", true);
    // // xmlhttp.open("POST", "php/reachPlotData_newDB.php", true);
    // xmlhttp.setRequestHeader(
    //   "Content-type",
    //   "application/x-www-form-urlencoded"
    // );
    // xmlhttp.send("ReachID=" + id);
  } else if (type == "dam") {
    var formData = new FormData();
    formData.append("DamID", id);

    fetch("php/damPlotData.php", {
      method: "POST",
      body: formData,
    })
      // .then((response) => response.text())
      .then((response) => response.text())
      .then((responseText) => {
        selectedFeature.data = JSON.parse(responseText);
        plotData();
      })
      .catch((error) => console.error("Error:", error));

    // var xmlhttp = new XMLHttpRequest();
    // xmlhttp.onreadystatechange = function () {
    //   if (this.readyState == 4 && this.status == 200) {
    //     // console.log(JSON.parse(this.responseText));
    //     selectedFeature.data = JSON.parse(this.responseText);
    //     // console.log(selectedFeature.data)
    //     plotData();
    //   }
    // };
    // xmlhttp.open("POST", "php/damPlotData.php", true);
    // xmlhttp.setRequestHeader(
    //   "Content-type",
    //   "application/x-www-form-urlencoded"
    // );
    // xmlhttp.send("DamID=" + id);
  }
}

// plot reach data
function plotData() {
  var timeScale = document.getElementById("irregular-scale").checked
    ? "irregular"
    : document.getElementById("weekly-scale").checked
    ? "weekly"
    : document.getElementById("bi-weekly-scale").checked
    ? "bi-weekly"
    : // : document.getElementById("semi-monthly-scale").checked
      // ? "semi-monthly"
      "monthly";

  var plotType = document.getElementById("water-temperature-chart-radio")
    .checked
    ? "water-temperature"
    : document.getElementById("long-term-mean-chart-radio").checked
    ? "long-term-mean"
    : document.getElementById("deviations-chart-radio").checked
    ? "deviations"
    : "";

  document.getElementById("plot-header-buttons").classList.remove("d-none");

  // var xRangeSelector1 = {
  //   buttons: [
  //     {
  //       count: 6,
  //       label: "6m",
  //       step: "month",
  //       stepmode: "backward",
  //     },
  //     {
  //       count: 12,
  //       label: "1y",
  //       step: "month",
  //       stepmode: "backward",
  //     },
  //     { step: "all" },
  //   ],
  // };

  if (selectedFeature.type == "reach") {
    // // do this while the dam's long-term mean and deviations are not available
    // document
    //   .getElementById("long-term-mean-chart-radio")
    //   .removeAttribute("disabled");
    // document
    //   .getElementById("deviations-chart-radio")
    //   .removeAttribute("disabled");
    // //

    var twoYearsAgo = new Date(
      selectedFeature.data.estimatedTempDates[
        selectedFeature.data.estimatedTempDates.length - 1
      ]
    );

    twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
    const year = twoYearsAgo.getUTCFullYear("default", {
      year: "numeric",
    });
    const month = twoYearsAgo.getUTCMonth("default", {
      month: "2-digit",
    });
    const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

    switch (timeScale) {
      case "irregular":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempDates,
              y: selectedFeature.data.estimatedTemp,
              mode: "markers",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.estimatedTempDates[
                    selectedFeature.data.estimatedTempDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMDates,
              y: selectedFeature.data.LTM,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.deviationDates,
              y: selectedFeature.data.deviation,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationDates[
                    selectedFeature.data.deviationDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "monthly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempMDates,
              y: selectedFeature.data.estimatedTempM,
              mode: "markers",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.estimatedTempMDates[
                    selectedFeature.data.estimatedTempMDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMMDates,
              y: selectedFeature.data.LTMM,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.deviationMDates,
              y: selectedFeature.data.deviationM,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationMDates[
                    selectedFeature.data.deviationMDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "weekly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempWDates[
            //     selectedFeature.data.estimatedTempWDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempWDates,
              y: selectedFeature.data.estimatedTempW,
              mode: "markers",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.estimatedTempWDates[
                    selectedFeature.data.estimatedTempWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMWDates,
              y: selectedFeature.data.LTMW,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.deviationWDates,
              y: selectedFeature.data.deviationW,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationWDates[
                    selectedFeature.data.deviationWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "bi-weekly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempBWDates[
            //     selectedFeature.data.estimatedTempBWDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempBWDates,
              y: selectedFeature.data.estimatedTempBW,
              mode: "markers",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.estimatedTempBWDates[
                    selectedFeature.data.estimatedTempBWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMBWDates,
              y: selectedFeature.data.LTMBW,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.estimatedTempMDates[
            //     selectedFeature.data.estimatedTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var estimatedTempTrace = {
              x: selectedFeature.data.deviationBWDates,
              y: selectedFeature.data.deviationBW,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationBWDates[
                    selectedFeature.data.deviationBWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
    }
  } else if (selectedFeature.type == "dam") {
    // // do this while the dam's long-term mean and deviations are not available
    // document
    //   .getElementById("long-term-mean-chart-radio")
    //   .removeAttribute("disabled");
    // document
    //   .getElementById("deviations-chart-radio")
    //   .removeAttribute("disabled");
    // //

    var twoYearsAgo = new Date(
      selectedFeature.data.waterTempDates[
        selectedFeature.data.waterTempDates.length - 1
      ]
    );

    twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
    const year = twoYearsAgo.getUTCFullYear("default", {
      year: "numeric",
    });
    const month = twoYearsAgo.getUTCMonth("default", {
      month: "2-digit",
    });
    const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

    switch (timeScale) {
      case "irregular":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.waterTempDates,
              y: selectedFeature.data.waterTemp,
              mode: "markers",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.waterTempDates[
                    selectedFeature.data.waterTempDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMDates,
              y: selectedFeature.data.LTM,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.deviationDates,
              y: selectedFeature.data.deviation,
              mode: "lines",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationDates[
                    selectedFeature.data.deviationDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "monthly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.waterTempMDates,
              y: selectedFeature.data.waterTempM,
              mode: "markers",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.waterTempMDates[
                    selectedFeature.data.waterTempMDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMMDates,
              y: selectedFeature.data.LTMM,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.deviationMDates,
              y: selectedFeature.data.deviationM,
              mode: "lines",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationMDates[
                    selectedFeature.data.deviationMDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "weekly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempWDates[
            //     selectedFeature.data.waterTempWDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.waterTempWDates,
              y: selectedFeature.data.waterTempW,
              mode: "markers",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.waterTempWDates[
                    selectedFeature.data.waterTempWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMWDates,
              y: selectedFeature.data.LTMW,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.deviationWDates,
              y: selectedFeature.data.deviationW,
              mode: "lines",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationWDates[
                    selectedFeature.data.deviationWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "bi-weekly":
        switch (plotType) {
          case "water-temperature":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempBWDates[
            //     selectedFeature.data.waterTempBWDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.waterTempBWDates,
              y: selectedFeature.data.waterTempBW,
              mode: "markers",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.waterTempBWDates[
                    selectedFeature.data.waterTempBWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.LTMBWDates,
              y: selectedFeature.data.LTMBW,
              // x: selectedFeature.data.landsatLTMMMonth,
              // y: selectedFeature.data.landsatLTMM,
              mode: "lines",
            };

            data = [longTermMeanTrace];

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // title: "Month-Day",
                // autorange: true,
                tickformat: "%b-%d",
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMMMonth[0],
                //   //   selectedFeature.data.landsatLTMMMonth[
                //   //     selectedFeature.data.landsatLTMMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            // Plotly.purge("plotly-chart");
            // var observedLandsatTrace = {
            //   x: selectedFeature.data.landsatTempMDates,
            //   y: selectedFeature.data.landsatTempMTemp,
            //   mode: "markers",
            //   name: "Observed Landsat Temperature",
            //   marker: { color: "rgb(255, 0, 0)", size: 8 },
            // };
            // var twoYearsAgo = new Date(
            //   selectedFeature.data.waterTempMDates[
            //     selectedFeature.data.waterTempMDates.length - 1
            //   ]
            // );
            // twoYearsAgo.setDate(twoYearsAgo.getDate() - 365 * 3);
            // const year = twoYearsAgo.getUTCFullYear("default", {
            //   year: "numeric",
            // });
            // const month = twoYearsAgo.getUTCMonth("default", {
            //   month: "2-digit",
            // });
            // const day = twoYearsAgo.getUTCDate("default", { day: "2-digit" });

            var waterTempTrace = {
              x: selectedFeature.data.deviationBWDates,
              y: selectedFeature.data.deviationBW,
              mode: "lines",
              name: "water Temperature",
              line: { color: "rgb(255, 0, 255)", size: 8 },
            };

            // data = [observedLandsatTrace, waterTempTrace];
            data = [waterTempTrace];

            var selectorOptions = {
              buttons: [
                {
                  step: "month",
                  stepmode: "backward",
                  count: 6,
                  label: "6m",
                },
                // {
                //   step: "year",
                //   stepmode: "todate",
                //   count: 1,
                //   label: "YTD",
                // },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 1,
                  label: "1y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 2,
                  label: "2y",
                },
                {
                  step: "year",
                  stepmode: "backward",
                  count: 5,
                  label: "5y",
                },
                {
                  step: "all",
                },
              ],
            };

            var layout = {
              height:
                Math.max(
                  document.documentElement.clientHeight || 0,
                  window.innerHeight || 0
                ) * 0.29,
              margin: {
                l: 80,
                r: 80,
                b: 20,
                t: 20,
              },
              // automargin: true,
              xaxis: {
                // autorange: true,
                rangeselector: selectorOptions,
                rangeslider: {},
                range: [
                  [year, month, day].join("-"),
                  selectedFeature.data.deviationBWDates[
                    selectedFeature.data.deviationBWDates.length - 1
                  ],
                ],
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
                title: "Temperature (&deg;C)",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
    }
  }
  document.getElementById("plot-panel").classList.remove("d-none");

  // if (selectedFeature.id) {} else {
  //   document.getElementById("plot-panel").classList.add("d-none");
  // }
}

function downloadData() {
  var datatype = document.getElementById("water-temperature-chart-radio")
    .checked
    ? "water-temperature"
    : document.getElementById("long-term-mean-chart-radio").checked
    ? "long-term-mean"
    : document.getElementById("deviations-chart-radio").checked
    ? "deviations"
    : "";

  var timeScale = document.getElementById("irregular-scale").checked
    ? "irregular"
    : document.getElementById("weekly-scale").checked
    ? "weekly"
    : document.getElementById("bi-weekly-scale").checked
    ? "bi-weekly"
    : // : document.getElementById("semi-monthly-scale").checked
      // ? "semi-monthly"
      "monthly";

  var featureType = selectedFeature.type;
  var id = selectedFeature.id;

  switch (featureType) {
    case "dam":
      // Prepare the data to be sent in the POST request
      var formData = new FormData();
      formData.append("DamID", id);
      formData.append("DataType", datatype);
      formData.append("TimeScale", timeScale);

      // Use fetch API to send a POST request to 'download.php'
      fetch("php/damDataDownload.php", {
        method: "POST",
        body: formData,
        // headers: {
        //   "Content-Type": "application/json",
        // },
      })
        .then((response) => response.blob())
        .then((blob) => {
          // Create a new URL for the blob
          const url = window.URL.createObjectURL(blob);
          // Create a link and set the URL as the href
          const a = document.createElement("a");
          a.href = url;

          var download_fname = "dam_" + id + "_" + timeScale + ".csv";
          a.download = download_fname;
          // Append the link to the body
          document.body.appendChild(a);
          // Trigger the download
          a.click();
          // Clean up by revoking the Object URL
          window.URL.revokeObjectURL(url);
        })
        .catch((error) => console.error("Error:", error));
      break;
    case "reach":
      // Prepare the data to be sent in the POST request
      var formData = new FormData();
      formData.append("ReachID", id);
      formData.append("DataType", datatype);
      formData.append("TimeScale", timeScale);

      // Use fetch API to send a POST request to 'download.php'
      fetch("php/reachDataDownload.php", {
        method: "POST",
        body: formData,
        // headers: {
        //   "Content-Type": "application/json",
        // },
      })
        .then((response) => response.blob())
        .then((blob) => {
          // Create a new URL for the blob
          const url = window.URL.createObjectURL(blob);
          // Create a link and set the URL as the href
          const a = document.createElement("a");
          a.href = url;
          var download_fname = "reach_" + id + "_" + timeScale + ".csv";
          a.download = download_fname;
          // Append the link to the body
          document.body.appendChild(a);
          // Trigger the download
          a.click();
          // Clean up by revoking the Object URL
          window.URL.revokeObjectURL(url);
        })
        .catch((error) => console.error("Error:", error));
      break;
  }
}

function gisDownload() {
  var basinID = document.getElementById("basin-selector").value;
  var reachID = document.getElementById("reach-selector").value;
  var riverID = document.getElementById("river-selector").value;

  const t = new Date(); // Get the current date and time
  const z = t.getTimezoneOffset() * 60 * 1000; // Convert the local time zone offset from minutes to milliseconds
  const tLocal = new Date(t - z); // Subtract the offset from the original date
  const todayIso = tLocal.toISOString().split("T")[0]; // Convert to ISO format and remove the time

  const monthAgo = new Date(tLocal);
  monthAgo.setDate(monthAgo.getDate() - 30);
  const monthAgoIso = monthAgo.toISOString().split("T")[0];

  if (basinID == "") {
    var basinID = "1";
  }

  if (document.getElementById("start-date").value == "") {
    var startDate = monthAgoIso;
  } else {
    var startDate = document.getElementById("start-date").value;
  }

  if (document.getElementById("end-date").value == "") {
    var endDate = todayIso;
  } else {
    var endDate = document.getElementById("end-date").value;
  }

  var formData = new FormData();
  formData.append("BasinID", basinID);
  formData.append("ReachID", reachID);
  formData.append("RiverID", riverID);
  formData.append("StartDate", startDate);
  formData.append("EndDate", endDate);

  fetch("php/gisDownload.php", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.blob())
    .then((blob) => {
      // Create a new URL for the blob
      const url = window.URL.createObjectURL(blob);
      // Create a link and set the URL as the href
      const a = document.createElement("a");
      a.href = url;

      var download_fname =
        "Ba_" +
        basinID +
        "_Re_" +
        reachID +
        "_Ri_" +
        riverID +
        "_" +
        startDate +
        "_" +
        endDate +
        ".geojson";
      a.download = download_fname;
      // Append the link to the body
      document.body.appendChild(a);
      // Trigger the download
      a.click();
      // Clean up by revoking the Object URL
      window.URL.revokeObjectURL(url);
    })
    .catch((error) => console.error("Error:", error));
}

// fire window resize event to fix the map not showing up
function fireResizeEvent() {
  window.dispatchEvent(new Event("resize"));
}

function toggleShowHowToOnStart() {
  localStorage.getItem("showHowToOnStart") == "true" ||
  localStorage.getItem("showHowToOnStart") == null
    ? localStorage.setItem("showHowToOnStart", "false")
    : localStorage.setItem("showHowToOnStart", "true");
}

// load esri apiKey
var esriAPIKey;
function getEsriAPIKey() {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      // console.log(this.responseText);
      // console.log("two")
    }
  };

  xmlhttp.open("GET", "php/esriAPIkey.php", true);
  xmlhttp.send();
}

// getEsriAPIKey();
// console.log("one");
