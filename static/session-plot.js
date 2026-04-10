import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePlot, { formatText } from "./base-plot.js";

export class SessionPlot extends BasePlot{

    async create(api, parent) {
        super.create(parent, "SESSION");

        let session = await api.get("/api/v1/sessions/1/full");
        console.log(session);
        
        // create a line for each member
        // members is actually session_members

        let memberG = this.root.selectAll("g")
            .data(session.members)
            .join("g")

        memberG
            .append("text")
            .call(formatText)
            .attr('x', 100)
            .attr('y', 100)
            .text(function (d) { return d.name });


    }

}