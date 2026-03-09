import * as d3 from './d3-modules.js';
import { BasePlot } from "./base-plot.js"

const plotWidth = 1000;
const plotHeight = 500;

export default class SessionPlot extends BasePlot { 

    create(parent) {
        super.create(parent);


    }

    update(api) {

        let data = api.get("/api/v1/sessions/1")

        // draw a line per 
        for(let i=0;i<data[])

        

    }
}