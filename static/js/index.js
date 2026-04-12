import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { GamesMasterSuccessionPanel, SessionListPanel, MemberListPanel, GameListPanel } from "./panels.js";
import { GamesMasterCountChart, DaysSinceGamesMasterChart } from "./bar-charts.js";
import { SessionPieChart } from "./pie-charts.js"
import Api from "./api.js";

let panels = [
    new GamesMasterSuccessionPanel(),
    new GamesMasterCountChart(),
    new DaysSinceGamesMasterChart(),
    new SessionListPanel(),
    new MemberListPanel(),
    new GameListPanel(),
    new SessionPieChart()
];

let api = new Api()

let body = d3.select("body");

let panelsContainer = body.append("div")
    .attr("class", "panels-container");

for(let i=0;i<panels.length;i++) {
    let panelContainer = panelsContainer.append("div")
        .attr("class", "panel-container")
        .attr("id", "panel-"+i);
    panels[i].create(api, panelContainer);
}