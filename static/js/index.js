import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import GamesMasterSuccessionPanel from "./panels.js";
import { GamesMasterCountChart, DaysSinceGamesMasterChart } from "./bar-charts.js";
import Api from "./api.js";

let panels = [
    new GamesMasterSuccessionPanel(),
    new GamesMasterCountChart(),
    new DaysSinceGamesMasterChart(),
];

let api = new Api()

let body = d3.select("body");
for(let i=0;i<panels.length;i++) {
    let panelContainer = body.append("div")
        .attr("class", "panel-container")
        .attr("id", "panel_"+i);
    panels[i].create(api, panelContainer);
}