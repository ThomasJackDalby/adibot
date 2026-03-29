import "./style.css";
import * as d3 from './d3-modules.js'
import { GamesMasterCountChart, DaysSinceGamesMasterChart, TotalAttendanceCount as TotalAttendanceCountChart } from './bar-charts.js'
import { SessionPlot } from './session.plot.js'
// import SessionGamesChart from './session-games.js'
import Api from './api.js'
let api = new Api()

let body = d3.select("body");
    // .style("display", "grid ")
    // .style("grid-template-columns", "1fr 1fr")
    // .style("grid-template-rows", "1fr")
    // .style("column-gap", "10px")
    // .style("row-gap", "10px");

body.append("h1")
    .style("text-align", "center")
    // .style("grid-column-start", 1)
    // .style("grid-column-end", 3)
    .text("ADIBOT - DASHBOARD");

let data = await api.get("/api/v1/games-master-succession")
console.log(data)

body.append("p")
    .style("font-size", "30px")
    .text("NEXT GM IS: "+data[0].member_name.toUpperCase());
body.append("p")
    .style("font-size", "20px")
    .text("BACKUPS ARE: "+data[1].member_name.toUpperCase());

let charts = [
    // new SessionPlot(),
    // new GamesMasterCountChart(),
    // new DaysSinceGamesMasterChart(),
    // new TotalAttendanceCountChart(),
]

for(let i=0;i<charts.length;i++) {
    charts[i].create(body.append("div")
        .attr("class", "plot-container")
        .attr("id", "plot_"+i));
    await charts[i].update(api);
}