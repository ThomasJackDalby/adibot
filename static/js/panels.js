
export default class GamesMasterSuccessionPanel
{
    async create(api, root) {
        let data = await api.get("/api/v1/games-master-succession")
        root.append("p")
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
        root.append("p")
            .style("font-size", "20px")
            .text(text);
    }
}