import BasePlot from './base-plot.js';
import * as d3 from './d3-modules.js';


class PieChart extends BasePlot {
    create(parent, title) {
        super.create(parent, title);
    }
}

let arcGenerator = d3.arc()
	.innerRadius(10)
	.outerRadius(plotHeight / 2 - 20)
	.padAngle(.1)
	.padRadius(50)
	.cornerRadius(10);

export default class SessionGamesChart extends PieChart { 

    create(parent) {
        super.create(parent);
        
        this.root.append("text")
            .attr("x", 10)
            .attr("y", 20)
            .text("ATTENDANCE");
    }

    update(api) {
        let members = api.get("/api/v1/members");

        const pie = d3.pie()
            .value((d) => d.games_master_count);
        const arcs = pie(members);

        this.root
            .append("g")
            .attr("transform", "translate("+plotWidth/2+","+plotHeight/2+")")
            .selectAll('path')
            .data(arcs)
            .join('path')
            .attr('d', arcGenerator)
            .style("stroke", "black")
            .style('fill', function(d, i) {
                let hsl;
                if (i == 0) hsl = [51, 100, 50];
                else if (i == 1)  hsl = [0, 0, 75];
                else if (i == 2) hsl = [30, 61, 50];
                else hsl = [220, 100, 80];
                return "hsl("+hsl[0]+","+hsl[1]+"%,"+hsl[2]+"%)"
            })
    }
}