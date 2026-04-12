import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import { BasePlot, formatText } from "./base-panels.js";

class BarChart extends BasePlot {
    create(parent, title) {
        super.create(parent, title);

        this.bottomMargin = 20;
        this.topMargin = 50;
        this.barGap = 10;
        this.maxRectHeight = super.getPlotHeight() - 30 - this.bottomMargin - this.topMargin;
    }

    async update(data) {
        let parent = this;
        let barWidth = super.getPlotWidth() / data.length - this.barGap;
        let maxCount = d3.max(data, d => d.count);
        let scale = d3.scaleLinear()
            .domain([0, maxCount])
            .range([0, this.maxRectHeight]);
        
        let selection = this.svg
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
                let height = maxCount == 0 ? 0 : scale(d.count);
                let y = parent.topMargin + parent.maxRectHeight - height;
                if (isNaN(y)) return 0;
                return y;
            })
            .attr('height', function (d, i) { return maxCount == 0 ? 0 : scale(d.count); })
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
            .attr('y', function (d) { 
                let y = parent.topMargin + parent.maxRectHeight - scale(d.count) - 5;
                return isNaN(y) ? 0 : y;
            })
            .text(function (d) { return d.count });
    }
}

export class GamesMasterCountChart extends BarChart {
    async create(api, parent) {
        super.create(parent, "GAMES MASTER COUNT");

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

        let minCount = d3.min(data, d => d.count);
        let maxCount = d3.max(data, d => d.count);
        const color = d3.scaleSequential([minCount, maxCount], d3.interpolatePiYG);
        this.bars.style('fill', d => {
            if (d.data.in_rotation) return color(d.count);
            return "#2ed8b9";
        });
    }
}

export class DaysSinceGamesMasterChart extends BarChart {  
    
    async create(api, parent) {
        super.create(parent, "DAYS SINCE GM");
    
        let members = await api.get("/api/v1/members");
        let data = d3.map(members, function(member) {
            return { 
                "category" : member.name,
                "count" : member.days_since_games_master
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