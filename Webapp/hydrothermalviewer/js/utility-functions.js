var selectedFeature = {
  type: null,
  id: null,
  data: null,
};
// global variable to store the selected feature type and ID

function loadBasins(priorityBasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("basin-selector").innerHTML = this.responseText;
    }
  };

  xmlhttp.open("POST", "php/loadBasins.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("priorityBasinID=" + priorityBasinID);
}

function loadRivers(BasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("river-selector").innerHTML = this.responseText;
    }
  };

  xmlhttp.open("POST", "php/loadRivers.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
}

function loadReaches(BasinID, RiverID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("reach-selector").innerHTML = this.responseText;
    }
  };

  xmlhttp.open("POST", "php/loadReaches.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID + "&RiverID=" + RiverID);
}

function loadDams(BasinID, RiverID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      document.getElementById("dam-selector").innerHTML = this.responseText;
    }
  };

  xmlhttp.open("POST", "php/loadDams.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID + "&RiverID=" + RiverID);
}

function loadBasinGeom(BasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      var geoJSON = JSON.parse(this.responseText);
      var layer = L.geoJSON(geoJSON, { style: basinStyle }).addTo(map);
    }
  };
  xmlhttp.open("POST", "php/loadBasinGeom.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
}

function loadRiversGeom(BasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      var geoJSON = JSON.parse(this.responseText);
      var layer = L.geoJSON(geoJSON).addTo(map);
    }
  };
  xmlhttp.open("POST", "php/loadRiversGeom.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
}

function loadReachesGeom(BasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      // console.log(this.responseText);
      var geoJSON = JSON.parse(this.responseText);
      var layer = L.geoJSON(geoJSON).addTo(map);
    }
  };
  xmlhttp.open("POST", "php/loadReachesGeom.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
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
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        onHttpDone(xmlhttp);
      }
    };
    xmlhttp.open("POST", "php/loadReachesGeom.php", true);
    xmlhttp.setRequestHeader(
      "Content-type",
      "application/x-www-form-urlencoded"
    );
    xmlhttp.send(
      "BasinID=" + BasinID + "&offset=" + offset + "&row_count=" + row_count
    );
  }

  function onHttpDone(xmlhttp) {
    var _geoJSON = JSON.parse(xmlhttp.responseText);
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
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      var geoJSON = JSON.parse(this.responseText);
      damsLayer = L.geoJSON(geoJSON, {
        style: damStyle,
        onEachFeature: onEachDamFeature,
      }).addTo(map);
    }
  };
  xmlhttp.open("POST", "php/loadDamsGeom.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
}

var damsPointsLayer;

function loadDamsPoints(BasinID) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
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
      var geoJSON = JSON.parse(this.responseText);
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
                  id: e.target.feature.properties.ReachID,
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
    }
  };
  xmlhttp.open("POST", "php/loadDamsPoints.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("BasinID=" + BasinID);
}

// get bound of a reach or dam feature
function zoomToFeatureBounds(type, id, updateTitle = true) {
  var xmlhttp = new XMLHttpRequest();
  xmlhttp.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
      // console.log(this.responseText);
      var geoJSON = JSON.parse(this.responseText);
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
    }
  };

  xmlhttp.open("POST", "php/getFeatureBounds.php", true);
  xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xmlhttp.send("type=" + type + "&id=" + id);
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
    color: temperatureColorScale(feature.properties.Temperature),
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
    fillColor: temperatureColorScale(feature.properties.Temperature),
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
  damsLayer.resetStyle(e.target);
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
        (props.Reservoir ? props.Reservoir : props.Name) +
        "</b><br />" +
        "Latest estimate: " +
        "<br />(" +
        props.startDate +
        " - " +
        props.endDate +
        ")<br />" +
        props.Temperature +
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
    ? props.Reservoir
      ? props.Reservoir
      : props.Name
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
    selectedFeature.id == document.getElementById("dam-selector").value
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
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        // console.log(this.responseText)
        selectedFeature.data = JSON.parse(this.responseText);
        // console.log(selectedFeature.data)
        plotData();
      }
    };
    xmlhttp.open("POST", "php/reachPlotData.php", true);
    // xmlhttp.open("POST", "php/reachPlotData_newDB.php", true);
    xmlhttp.setRequestHeader(
      "Content-type",
      "application/x-www-form-urlencoded"
    );
    xmlhttp.send("ReachID=" + id);
  } else if (type == "dam") {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
      if (this.readyState == 4 && this.status == 200) {
        // console.log(JSON.parse(this.responseText));
        selectedFeature.data = JSON.parse(this.responseText);
        // console.log(selectedFeature.data)
        plotData();
      }
    };
    xmlhttp.open("POST", "php/damPlotData.php", true);
    xmlhttp.setRequestHeader(
      "Content-type",
      "application/x-www-form-urlencoded"
    );
    xmlhttp.send("DamID=" + id);
  }
}

// plot reach data
function plotData() {
  var timeScale = document.getElementById("semi-monthly-scale").checked
    ? "semi-monthly"
    : "monthly";

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

    switch (timeScale) {
      case "monthly":
        switch (plotType) {
          case "water-temperature":
            Plotly.purge("plotly-chart");
            var observedLandsatTrace = {
              x: selectedFeature.data.landsatTempMDates,
              y: selectedFeature.data.landsatTempMTemp,
              mode: "markers",
              name: "Observed Landsat Temperature",
              marker: { color: "rgb(255, 0, 0)", size: 8 },
            };

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempMDates,
              y: selectedFeature.data.estimatedTempM,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(0, 0, 255)", width: 2 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.estimatedTempMDates[0],
                    selectedFeature.data.estimatedTempMDates[
                      selectedFeature.data.estimatedTempMDates.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.estimatedLTMMMonth,
              y: selectedFeature.data.estimatedLTMM,
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
              automargin: true,
              xaxis: {
                autorange: true,
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
                // type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            Plotly.purge("plotly-chart");
            var deviation = {
              x: selectedFeature.data.deviationMDate,
              y: selectedFeature.data.deviationMDeviation,
              mode: "line",
            };

            data = [deviation];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.deviationMDate[0],
                    selectedFeature.data.deviationMDate[
                      selectedFeature.data.deviationMDate.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "semi-monthly":
        switch (plotType) {
          case "water-temperature":
            Plotly.purge("plotly-chart");
            var observedLandsatTrace = {
              x: selectedFeature.data.landsatTempSMDates,
              y: selectedFeature.data.landsatTempSMTemp,
              mode: "markers",
              name: "Observed Landsat Temperature",
              marker: { color: "rgb(255, 0, 0)", size: 8 },
            };

            var estimatedTempTrace = {
              x: selectedFeature.data.estimatedTempSMDates,
              y: selectedFeature.data.estimatedTempSM,
              mode: "lines",
              name: "Estimated Temperature",
              line: { color: "rgb(0, 0, 255)", width: 2 },
            };

            // data = [observedLandsatTrace, estimatedTempTrace];
            data = [estimatedTempTrace];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.estimatedTempSMDates[0],
                    selectedFeature.data.estimatedTempSMDates[
                      selectedFeature.data.estimatedTempSMDates.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");

            var longTermMeanTrace = {
              x: selectedFeature.data.estimatedLTMSMMonth,
              y: selectedFeature.data.estimatedLTMSM,
              // x: selectedFeature.data.landsatLTMSMMonth,
              // y: selectedFeature.data.landsatLTMSM,
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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMSMMonth[0],
                //   //   selectedFeature.data.landsatLTMSMMonth[
                //   //     selectedFeature.data.landsatLTMSMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                // type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "deviations":
            Plotly.purge("plotly-chart");
            var deviation = {
              x: selectedFeature.data.deviationSMDate,
              y: selectedFeature.data.deviationSMDeviation,
              mode: "line",
            };

            data = [deviation];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.deviationSMDate[0],
                    selectedFeature.data.deviationSMDate[
                      selectedFeature.data.deviationSMDate.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
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
    // document.getElementById("water-temperature-chart-radio").checked = true;
    // plotType = "water-temperature";
    // document
    //   .getElementById("long-term-mean-chart-radio")
    //   .removeAttribute("disabled");
    //   // .setAttribute("disabled", "disabled");
    // document
    //   .getElementById("deviations-chart-radio")
    //   .removeAttribute("disabled");
    //   // .setAttribute("disabled", "disabled");
    //

    switch (timeScale) {
      case "monthly":
        switch (plotType) {
          case "water-temperature":
            Plotly.purge("plotly-chart");
            var observedLandsatTrace = {
              x: selectedFeature.data.landsatTempMDates,
              y: selectedFeature.data.landsatTempMTemp,
              mode: "lines",
              name: "Observed Landsat Temperature",
              marker: { color: "rgb(0, 0, 255)", size: 8 },
            };

            data = [observedLandsatTrace];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.landsatTempMDates[0],
                    selectedFeature.data.landsatTempMDates[
                      selectedFeature.data.landsatTempMDates.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "long-term-mean":
            Plotly.purge("plotly-chart");
            var longTermMeanTrace = {
              x: selectedFeature.data.landsatLTMMMonth,
              y: selectedFeature.data.landsatLTMM,
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
              automargin: true,
              xaxis: {
                autorange: true,
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
                // type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);

            break;
          case "deviations":
            Plotly.purge("plotly-chart");
            var deviation = {
              x: selectedFeature.data.deviationMDate,
              y: selectedFeature.data.deviationMDeviation,
              mode: "line",
            };

            data = [deviation];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.deviationMDate[0],
                    selectedFeature.data.deviationMDate[
                      selectedFeature.data.deviationMDate.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
      case "semi-monthly":
        switch (plotType) {
          case "water-temperature":
            Plotly.purge("plotly-chart");
            var observedLandsatTrace = {
              x: selectedFeature.data.landsatTempSMDates,
              y: selectedFeature.data.landsatTempSMTemp,
              mode: "lines",
              name: "Observed Landsat Temperature",
              marker: { color: "rgb(0, 0, 255)", size: 8 },
            };

            data = [observedLandsatTrace];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.landsatTempSMDates[0],
                    selectedFeature.data.landsatTempSMDates[
                      selectedFeature.data.landsatTempSMDates.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;

          case "long-term-mean":
            Plotly.purge("plotly-chart");

            var longTermMeanTrace = {
              // x: selectedFeature.data.estimatedLTMSMMonth,
              // y: selectedFeature.data.estimatedLTMSM,
              x: selectedFeature.data.landsatLTMSMMonth,
              y: selectedFeature.data.landsatLTMSM,
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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                // rangeslider: {
                //   autorange: true,
                //   // range: [
                //   //   selectedFeature.data.landsatLTMSMMonth[0],
                //   //   selectedFeature.data.landsatLTMSMMonth[
                //   //     selectedFeature.data.landsatLTMSMMonth.length - 1
                //   //   ],
                //   // ],
                // },
                // type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
          case "deviations":
            Plotly.purge("plotly-chart");
            var deviation = {
              x: selectedFeature.data.deviationSMDate,
              y: selectedFeature.data.deviationSMDeviation,
              mode: "line",
            };

            data = [deviation];

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
              automargin: true,
              xaxis: {
                autorange: true,
                // rangeselector: xRangeSelector1,
                rangeslider: {
                  autorange: true,
                  range: [
                    selectedFeature.data.deviationSMDate[0],
                    selectedFeature.data.deviationSMDate[
                      selectedFeature.data.deviationSMDate.length - 1
                    ],
                  ],
                },
                type: "date",
              },
              yaxis: {
                autorange: true,
                type: "linear",
              },
            };
            var config = { responsive: true };
            Plotly.newPlot("plotly-chart", data, layout, config);
            break;
        }
        break;
    }
    // console.log(timeScale, plotType);
  }
  document.getElementById("plot-panel").classList.remove("d-none");

  // if (selectedFeature.id) {} else {
  //   document.getElementById("plot-panel").classList.add("d-none");
  // }
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
// console.log("one")
