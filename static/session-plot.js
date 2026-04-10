import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
import BasePlot, { formatText } from "./base-plot.js";

export class SessionPlot extends BasePlot{

    async create(api, parent) {
        super.create(parent, "SESSION");

        let sessionData = await api.get("/api/v1/sessions/1/full");
        console.log(sessionData);
        
        // create a line for each member
        // members is actually session_members





        let data = d3.map(members, function(member) {
            return { 
                "category" : member.name,
                "count" : member.games_master_count
             }
        });



    }

}