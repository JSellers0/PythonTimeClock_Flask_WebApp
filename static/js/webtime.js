import {timelog_model } from "./models.js"

class View {
    constructor() {
        this.message = document.getElementById("message");
        this.stopButton = document.getElementById("stop");
        this.userid = document.getElementById("url_userid")
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

    initializeStopEvent() {
        this.view.stopButton.addEventListener("click", async (evt) => {
            evt.preventDefault();

            try {
                await this.model.updateUserCurrentRow(
                    this.view.userid.value,
                    {stop: new Date().getTime()}
                );
                await this.updateMessage();
            } catch(err) {
                this.view.errorMessage(err);
            }
        });
    }
}

// Create the VC components
const view = new View();
const controller = new Controller(timelog_model, view);

// Export the MVC components as the default
export default {
    timelog_model,
    view,
    controller
};