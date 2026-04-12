import { BasePanel } from "./base-panels.js";

export class GamesMasterSuccessionPanel extends BasePanel
{
    async create(api, parent) {
        super.create(parent, "GAMES MASTER SUCCESSION");

        let data = await api.get("/api/v1/games-master-succession")
        parent.append("p")
            .style("font-size", "30px")
            .text("NEXT GM IS "+data[0].member_name.toUpperCase());
        
        let text = "Backups are ";
        const numberOfBackups = 4;
        for (let i=0;i<numberOfBackups;i++) {
            text += data[i+1].member_name.toUpperCase()
            if (i < numberOfBackups - 2) text += ", ";
            else if (i < numberOfBackups - 1) text += " then ";
            else text += ".";
        }
        parent.append("p")
            .style("font-size", "20px")
            .text(text);
    }
}

export class SessionListPanel extends BasePanel
{
    async create(api, parent) {
        super.create(parent, "SESSIONS");
        let data = await api.get("/api/v1/sessions");

        let container = parent.append("div")
            .attr("class", "link-container");

        let session = container.selectAll("div")
            .data(data)
            .join("div")
            .attr("class", "link-item");

        session.append("a")
            .attr("href", d => "/sessions/"+d.id)
            .text(d => d.date);
    }
}

export class MemberListPanel extends BasePanel
{
    async create(api, root) {
        super.create(root, "MEMBERS");
        let data = await api.get("/api/v1/members");

        let container = root.append("div")
            .attr("class", "link-container");

        let member = container.selectAll("div")
            .data(data)
            .join("div")
            .attr("class", "link-item");

        member.append("a")
            .attr("href", d => "/members/"+d.id)
            .text(d => d.name);
    }
}

export class GameListPanel extends BasePanel
{
    async create(api, root) {
        super.create(root, "GAMES");
        let data = await api.get("/api/v1/games");

        let container = root.append("div")
            .attr("class", "link-container");

        let session = container.selectAll("div")
            .data(data)
            .join("div")
            .attr("class", "link-item");

        session.append("a")
            .attr("href", d => "/games/"+d.id)
            .text(d => d.name);
    }
}