import * as d3 from './d3-modules.js';
import BasePlot, { formatText } from "./base-plot.js";

class BarChart extends BasePlot {
    create(parent, title) {
        super.create(parent, title);

        this.bottomMargin = 20;
        this.topMargin = 50;
        this.barGap = 10;
        this.maxRectHeight = super.getPlotHeight() - this.bottomMargin - this.topMargin;
    }

    async update(data) {
        let parent = this;
        let barWidth = super.getPlotWidth() / data.length - this.barGap;
        let maxCount = d3.max(data, d => d.count);
        let scale = d3.scaleLinear()
            .domain([0, maxCount])
            .range([0, this.maxRectHeight]);
        
        let selection = this.root
            .selectAll('g')
            .data(data)
            .join('g')
            .attr('transform', function(d, i) {
                let x = i * (barWidth + parent.barGap) + 0.5 * parent.barGap;
                let y = 0;
                return "translate("+x+","+y+")";
            })
    
        this.bars = selection
            .append("rect")
            .attr('x', 0)
            .attr('y', function (d, i) { 
                return parent.topMargin + parent.maxRectHeight - scale(d.count);
            })
            .attr('height', function (d, i) { return scale(d.count) })
            .attr('stroke', 'black')
            .attr('width', barWidth);

        this.topLabel = selection
            .append("text")
            .call(formatText)
            .attr('x', barWidth/2)
            .attr('y', this.topMargin + this.maxRectHeight + 15)
            .text(function (d) { return d.category });
    
        this.bottomLabel = selection
            .append("text")
            .call(formatText)
            .attr('x', barWidth/2)
            .attr('y', function (d) { return parent.topMargin + parent.maxRectHeight - scale(d.count)-5 })
            .text(function (d) { return d.count });
    }
}

export class GamesMasterCountChart extends BarChart {  
    
    create(parent) {
        super.create(parent, "GAMES MASTER COUNT");
    }
    
    async update(api){
        let members = await api.get("/api/v1/members");
        let data = d3.map(members, function(member) {
            return { 
                "category" : member.name,
                "count" : member.games_master_count
             }
        });

        await super.update(data);

        let minCount = d3.min(data, d => d.count);
        let maxCount = d3.max(data, d => d.count);
        const color = d3.scaleSequential([minCount, maxCount], d3.interpolatePiYG);
        this.bars.style('fill', (d, i) => color(d.count))
    }
}

export class DaysSinceGamesMasterChart extends BarChart {  
    
    create(parent) {
        super.create(parent, "DAYS SINCE GM");
    }

    async update(api){
        let members = await api.get("/api/v1/members");
        let data = d3.map(members, function(member) {
            return { 
                "category" : member.name,
                "count" : member.days_since_gm
            }
        });
        data.sort(function(x, y) {
            return d3.descending(x.count, y.count);
        })

        await super.update(data);

        const color = d3.scaleSequential([0, data.length-1], d3.interpolatePiYG);
        this.bars.style('fill', (d, i) => color(i))
    }
}

export class TotalAttendanceCount extends BarChart {  
    
    create(parent) {
        super.create(parent, "TOTAL ATTENDANCE COUNT");
    }

    async update(api){
        let members = await api.get("/api/v1/members");
        let data = d3.map(members, function(member) {
            return { 
                "category" : member.name,
                "count" : member.total_attendance
            }
        });


        await super.update(data);

        let minCount = d3.min(data, d => d.count);
        let maxCount = d3.max(data, d => d.count);
        const color = d3.scaleSequential([minCount, maxCount], d3.interpolatePiYG);
        this.bars.style('fill', (d, i) => color(d.count))
    }
}