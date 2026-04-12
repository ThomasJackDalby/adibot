import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { BasePlot } from "./base-panels.js";

class PieChart extends BasePlot
{
    create(root, title) {
        super.create(root, title);

        this.radius = 200;
        this.innerRadius = 20;
        this.textOffsetRadius = 20;
    }

    async update(data) {
        // Chart dimensions

        // const svg = this.root
        //     .attr('width', width)
        //     .attr('height', height)
        //     .append('g')
        //     .attr('transform', `translate(${width / 2}, ${height / 2})`);



        const color = d3.scaleOrdinal()
            .domain(data.map(d => d.category))
            .range(d3.schemeCategory10);

        // Create the pie generator
        const pie = d3.pie()
            .padAngle(0.039)
            .value(d => d.count);

        // Create the arc generator
        const arc = d3.arc()
            .innerRadius(this.innerRadius)
            .outerRadius(this.radius);

        // Bind data to pie slices
        let g = this.svg.append("g")
            .attr('transform', `translate(${this.plotWidth / 2}, ${this.plotHeight / 2})`)

        let slice = g.selectAll('path')
            .data(pie(data))
            .enter()
            .append('path')
            .attr('d', d => arc(d))
            .attr('fill', d => color(d.data.category))
            .attr('stroke', 'black')
            .style('stroke-width', '1px');

        // Add labels to slices
        let label = g.selectAll('text')
            .data(pie(data))
            .join("text")
            .attr('text-anchor', "middle")
            .attr('dominant-baseline', "central")
            .attr("x", d => (this.radius + this.textOffsetRadius) * Math.cos(d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI / 2))
            .attr("y", d => (this.radius + this.textOffsetRadius) * Math.sin(d.startAngle + (d.endAngle - d.startAngle)/2 - Math.PI / 2))
            .text(d => d.data.category)
            .style('font-size', '12px')
            .style('fill', 'black');
    }
}

export class SessionPieChart extends PieChart {
async create(api, parent) {
        super.create(parent, "GAMES MASTER COUNT PIE");
        let members = await api.get("/api/v1/members");
        let data = members
            .map(member =>
        {
            return {
                "data" : member,
                "category" : member.name,
                "count" : member.games_master_count
            }
        });

        await super.update(data);

        // let minCount = d3.min(data, d => d.count);
        // let maxCount = d3.max(data, d => d.count);
        // const color = d3.scaleSequential([minCount, maxCount], d3.interpolatePiYG);
        // this.bars.style('fill', d => {
        //     if (d.data.in_rotation) return color(d.count);
        //     return "#2ed8b9";
        // });
    }
}