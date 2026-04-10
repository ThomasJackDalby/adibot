import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePanel from "./base-panel.js"

export function formatText(selection) {
    selection
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .attr('font-size', '15')
}

export default class BasePlot extends BasePanel {
    create(parent, title) {
        this.plotWidth = 1000;
        this.plotHeight = 500;

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
    }

    getPlotWidth() {
        return this.plotWidth;
    }
    getPlotHeight() {
        return this.plotHeight;
    }
}