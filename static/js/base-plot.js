import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePanel from "./base-panel.js"

export function formatText(selection) {
    selection
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .attr('font-size', '15')
}

export default class BasePlot extends BasePanel {
    create(parent, title, plotWidth = 1000, plotHeight = 500) {
        this.plotWidth = plotWidth;
        this.plotHeight = plotHeight;

        this.svg = parent.append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", "0 0 "+this.plotWidth+" "+this.plotHeight);

        this.root = this.svg            
            .append("g");

        this.root
            .append("text")
            .attr('font-size', '15')
            .attr("x", 10)
            .attr("y", 20)
            .text(title)

        this.plot = this.root
            .append("g")
            .attr("transform", "translate(0, 30)");
    }

    getPlotWidth() {
        return this.plotWidth;
    }
    getPlotHeight() {
        return this.plotHeight;
    }
}