import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePlot, { formatText } from "./base-plot.js";

const memberHeight = 100;

export class SessionPlot extends BasePlot{

    constructor(sessionId) {
        super();
        this.sessionId = sessionId;
    }

    async create(api, parent) {
        super.create(parent, "SESSION");

        let session = await api.get("/api/v1/sessions/"+this.sessionId+"/full");
        console.log(session);

        let data = d3.map(session.members, function(member, i) {
            member.yTop = (i-1) * memberHeight;
            member.yMid = member.yTop + memberHeight / 2.0;
            member.yBottom = member.yTop + memberHeight;

            member.sessions = d3.map(session.sessionMembers, function(sessionMember, j) {
                return sessionMember;
            }).filter(d => d.memberId == member.id);
            console.log(member.id)
            console.log(member.name)
            console.log(member.sessions)
            return member;
        });
        
        // create a line for each member
        // members is actually session_members

        let member = this.root.selectAll("g")
            .data(data)
            .join("g")

        member.attr("transform", "translate(0,"+memberHeight+")");

        member.append("rect")
            .attr("x", 0)
            .attr("y", d => d.yTop)
            .attr("width", this.plotWidth)
            .attr("height", memberHeight)
            .attr("fill", null)
            .attr("stroke", "black")

        member
            .append("text")
            .call(formatText)
            .attr('x', 10)
            .attr('text-anchor', "left")
            .attr('dominant-baseline', "central")
            .attr('y', d => d.yMid)
            .text(function (d) { return d.name });

            
        let memberSessions = member.selectAll("g")
            .data(d => d.member.sessions)
            .join("g");
            
        const scaleTime = d3.scaleTime([new Date(2000, 0, 1), new Date(2000, 0, 2)], [0, 960]);
        memberSessions.append("line")
            .attr("x1", d => scaleTime(d.start))
            .attr("x2", d => scaleTime(d.end))
            .attr("y1", d => d.yMid)
            .attr("y2", d => d.yMid)
            .attr("stroke", "black")
    }
}