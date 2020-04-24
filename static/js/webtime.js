import {timelog_model } from "./models.js"

class View {
    constructor() {
        this.message = document.getElementById("message");
        this.stopButton = document.getElementById("stop");
    }
}

class Controller {
    constructor(model, view) {
        this.model = model;
        this.view = view;

        this.initialize();
    }

    async initialize() {
        this.initializeStopEvent();
    }
}