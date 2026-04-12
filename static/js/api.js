export default class Api { 

    constructor() {
        this.cache = {}
    }

    async get(url) {
        if (url in this.cache) return this.cache[url];
        let response = await fetch(url)
        this.cache[url] = response.json();
        return this.cache[url];
    } 
}