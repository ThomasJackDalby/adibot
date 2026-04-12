export class BasePanel {
    create(root, title) {
        root.append("hr");
        root.append("h2")
            .text(title);
    }
}

export function formatText(selection) {
    selection
        .attr('text-anchor', 'middle')
        .attr('fill', 'black')
        .attr('font-size', '15')
}

export class BasePlot extends BasePanel {
    create(parent, title, plotWidth = 1000, plotHeight = 500) {
        super.create(parent, title);
        this.plotWidth = plotWidth;
        this.plotHeight = plotHeight;

        this.svg = parent.append("svg")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("viewBox", "0 0 "+this.plotWidth+" "+this.plotHeight);
    }

    getPlotWidth() {
        return this.plotWidth;
    }
    getPlotHeight() {
        return this.plotHeight;
    }
}