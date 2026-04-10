import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePanel from "./base-panel.js"
import BasePlot, { formatText } from "./base-plot.js";

const marginTop = 50;
const memberHeight = 80;
const gameLineHeight = 60;
const memberLineHeight = 2;

const sessionStartHour = 19;

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

let GAME_COLORS = [];
for(let i=0;i<50;i++) {
    GAME_COLORS.push(getRandomColor())
}

export class SessionPlot extends BasePlot {

    constructor(sessionId) {
        super();
        this.sessionId = sessionId;
    }

    async create(api, parent) {
        let session = await api.get("/api/v1/sessions/"+this.sessionId+"/full");
        let plotHeight = 500; // session.members.length * memberHeight + marginTop;

        super.create(parent, "SESSION TIMELINE", 1000, 500);

        let data = session.members
            .map((member, i) =>
            {
                member.yTop = (i-1) * memberHeight;
                member.yMid = member.yTop + memberHeight / 2.0;
                member.yBottom = member.yTop + memberHeight;

                member.sessions = session.sessionMembers
                    .filter(d => d.memberId == member.id)
                    .map(function(sessionMember, j) {
                    sessionMember.yMid = member.yMid;

                    sessionMember.sessionMemberGames.forEach(d => {
                        d.yMid = member.yMid
                        d.gameFill = GAME_COLORS[session.games.findIndex(g => g.id == d.gameId)]
                    }) 

                    return sessionMember;
                });
                return member;
            });
        data = d3.sort(data, member => member.name);
        
        // get session start/end datetime
        let sessionStart = d3.map(session.sessionMembers, sessionMember => new Date(sessionMember.start))
            .reduce((a, b) => a.getTime() < b.getTime() ? a : b);
        sessionStart.setMinutes(sessionStart.getMinutes()-30);
        let sessionEnd = d3.map(session.sessionMembers, sessionMember => new Date(sessionMember.end))
            .reduce((a, b) => a.getTime() > b.getTime() ? a : b);
        sessionEnd.setMinutes(sessionEnd.getMinutes()+30);
        const scaleTime = d3.scaleTime([sessionStart, sessionEnd], [100, this.plotWidth-100]);

        this.root.append("g")
            .attr("transform", "translate(0,"+marginTop+")")
            .attr("class", "axis")
            .call(d3.axisTop(scaleTime));

        // add some grid lines
        let gridTime = new Date(sessionStart);
        while(gridTime.getTime() < sessionEnd.getTime())
        {
            this.root.append("line")
                .attr("x1", scaleTime(gridTime))
                .attr("x2", scaleTime(gridTime))
                .attr("y1", marginTop)
                .attr("y2", marginTop+session.members.length*memberHeight)
                .attr("stroke-dasharray", 4)
                .attr("stroke", "black")

            for(let i=0;i<3;i++){
                gridTime.setMinutes(gridTime.getMinutes()+15);
                if (gridTime.getTime() > sessionEnd.getTime()) break;
                this.root.append("line")
                    .attr("x1", scaleTime(gridTime))
                    .attr("x2", scaleTime(gridTime))
                    .attr("y1", marginTop)
                    .attr("y2", marginTop+session.members.length*memberHeight)
                    .attr("stroke-dasharray", 2)
                    .attr("stroke-thickness", 0.5)
                    .attr("stroke", "rgb(100, 100, 100)")
            }
            gridTime.setMinutes(gridTime.getMinutes()+15);
        }

        // create a line for each member
        // members is actually session_members
        let member = this.root.selectAll("g.member")
            .data(data)
            .join("g")
            .attr("class", "member");

        member.attr("transform", "translate(0,"+(marginTop+memberHeight)+")");

        member
            .append("text")
            .call(formatText)
            .attr('x', 10)
            .attr('text-anchor', "left")
            .attr('dominant-baseline', "central")
            .attr('y', d => d.yMid)
            .text(function (d) { return d.name });
         
        let memberSessions = member.selectAll("g.member-session")
            .data(d => d.sessions)
            .join("g")
            .attr("class", "member-session");

        memberSessions.append("line")
            .attr("x1", d => scaleTime(new Date(d.start)))
            .attr("x2", d => scaleTime(new Date(d.end)))
            .attr("y1", d => d.yMid)
            .attr("y2", d => d.yMid)
            .attr("stroke", "black")

        memberSessions.append("rect")
            .attr("x", d => scaleTime(new Date(d.start)))
            .attr("y", d => d.yMid-memberLineHeight/2)
            .attr("width", d => scaleTime(new Date(d.end)) - scaleTime(new Date(d.start)))
            .attr("height", memberLineHeight)
            .attr("stroke", "black")
            .style("fill", "white")
        
        let sessionMemberGames = memberSessions.selectAll("g.session-member-game")
            .data(d => d.sessionMemberGames)
            .join("g")
            .attr("class", "member-session-game");

        sessionMemberGames.append("rect")
            .attr("x", d => scaleTime(new Date(d.start)))
            .attr("y", d => d.yMid-gameLineHeight/2)
            .attr("width", d => scaleTime(new Date(d.end)) - scaleTime(new Date(d.start)))
            .attr("height", gameLineHeight)
            .attr("stroke", "black")
            .style("fill", d => d.gameFill) 
    }
}

const gameHeight = 100;



export class SessionSummaryPanel extends BasePlot 
{
    constructor(sessionId) {
        super();
        this.sessionId = sessionId;
    }

    async create(api, parent) {
        super.create(parent, "SESSION GAMES");

        let session = await api.get("/api/v1/sessions/"+this.sessionId+"/full");
        let data = session.games
            .map((game, i) =>
            {
                game.yTop = i * gameHeight;
                game.yMid = game.yTop + gameHeight / 2.0;
                game.yBottom = game.yTop + gameHeight;
                game.gameFill = GAME_COLORS[i]
                // member.sessions = session.sessionMembers
                //     .filter(d => d.memberId == member.id)
                //     .map(function(sessionMember, j) {
                //     sessionMember.yMid = member.yMid;

                //     sessionMember.sessionMemberGames.forEach(d => d.yMid = member.yMid) 

                //     return sessionMember;
                // });
                return game;
            });
        data = d3.sort(data, game => game.name);
        console.log(data);

        let game = this.root
            .append("g")
            .selectAll("g")
            .data(data)
            .join("g");
        
        const squareSize = 25;
        game.append("rect")
            .attr('x', 10)
            .attr('y', d => d.yMid-squareSize/2)
            .attr("width", squareSize)
            .attr("height", squareSize)
            .attr("stroke", "black")
            .style("fill", d => d.gameFill)

        game.append("text")
            .call(formatText)
            .attr('x', 10 + squareSize + 5)
            .attr('text-anchor', "left")
            .attr('dominant-baseline', "central")
            .attr('y', d => d.yMid)
            .text(d => d.name);
    }
}