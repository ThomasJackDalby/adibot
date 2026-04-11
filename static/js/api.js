export default class Api { 

    constructor() {
        this.rootUrl = "http://127.0.0.1"
        this.port = 80;
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