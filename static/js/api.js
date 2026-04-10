export default class Api { 

    constructor() {
        this.rootUrl = "http://localhost"
        //this.rootUrl = "http://192.168.0.100"
        this.port = 8000;
        this.cache = {}
    }

    async get(url) {
        if (url in this.cache) return this.cache[url];
        let fullUrl = this.rootUrl + ":" + this.port + url;
        let response = await fetch(fullUrl)
        this.cache[url] = response.json();
        return this.cache[url];
    } 
}