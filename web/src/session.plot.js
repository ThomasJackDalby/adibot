import BasePlot, { formatText } from './base-plot.js';
import * as d3 from './d3-modules.js';

const margin = 50;

export class SessionPlot extends BasePlot { 

    create(parent) {
        super.create(parent);
        
        this.root.append("text")
            .attr("x", 10)
            .attr("y", 20)
            .text("SESSION PLOT");
    }

    async update(api) {
        let session = await api.get("/api/v1/sessions/1");

        // session.members = d3.map(session.members, sessionMember => {
        //     "startDate" : 
        // })

        let memberGroup = this.root
            .selectAll('g')
            .data(session.members)
            .join('g')
            .attr('transform', function(d, i) {
                let x = margin;
                let y = 50 + i * 50;
                return "translate("+x+","+y+")";
            })
        
        let parts = session.date.split('-');
        let sessionStart = new Date(parts[0], parts[1], parts[2], 18);
        let sessionEnd = new Date(sessionStart.getTime() + 9 * 60 * 60 * 1000)
        let timeScale = d3.scaleTime().domain([sessionStart, sessionEnd]).range([margin, this.plotWidth-margin]);

        memberGroup.append("text")
            .attr("y", 4)
            .attr("x", -5)
            .attr('text-anchor', 'end')
            .text((d) => d.name);
            
        memberGroup.append("line")
            .attr("x1", d => timeScale(d.start))
            .attr("x2", this.plotWidth)
            .attr("y1", 0)
            .attr("y2", 0)
            .attr("stroke-width", 3)
            .attr("stroke", "black")
        memberGroup.append("line")
            .attr("x1", d => timeScale(d.start))
            .attr("x2", 0)
            .attr("y1", -10)
            .attr("y2", 10)
            .attr("stroke-width", 3)
            .attr("stroke", "black")

        let xAxis = d3.axisBottom(timeScale)
            .tickFormat(d3.timeFormat("%H:%M:%S"))
            .ticks(50);

        this.root.append("g")
            // .attr("class", "x axis")
            .attr("transform", "translate(0," + 300 + ")")
            .call(xAxis)
            .selectAll("text")
            .call(formatText)
            .attr("y", -5)
            .attr("x", 40)
            .attr("transform", "rotate(90)")
    }
}