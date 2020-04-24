import { user_model } from "./models.js"

class View {
    constructor() {
        this.table = document.querySelector(".users table");
        this.error = document.querySelector(".error");
        this.userid = document.getElementById("userid");
        this.user_name = document.getElementById("user_name");
        this.email = document.getElementById("email");
        this.createButton = document.getElementById("create");
        this.updateButton = document.getElementById("update");
        this.deleteButton = document.getElementById("delete");
        this.resetButton = document.getElementById("reset");
    }

    reset() {
        this.userid.textContent = "";
        this.user_name.value = "";
        this.email.value = "";
        this.user_name.focus();
    }

    updateEditor(user) {
        this.userid.textContent = user.userid;
        this.user_name.value = user.user_name;
        this.email.value = user.email;
        this.user_name.focus();
    }

    buildTable(users) {
        let tbody,
            html = "";

        // Iterate over the users and build the table
        users.forEach((user) => {
            html += `
            <tr data-userid="${user.userid}" data-user_name="${user.user_name}" data-email="${user.email}">
                <td class="user_name">${user.user_name}</td>
                <td class="email">${user.email}</td>
            </tr>`;
        });
        // Is there currently a tbody in the table?
        if (this.table.tBodies.length !== 0) {
            this.table.removeChild(this.table.getElementsByTagName("tbody")[0]);
        }
        // Update tbody with our new content
        tbody = this.table.createTBody();
        tbody.innerHTML = html;
    }

    errorMessage(message) {
        this.error.innerHTML = message;
        this.error.classList.add("visible");
        this.error.classList.remove("hidden");
        setTimeout(() => {
            this.error.classList.add("hidden");
            this.error.classList.remove("visible");
        }, 2000);
    }
}

class Controller {
    constructor(model, view) {
        this.model = model;
        this.view = view;

        this.initialize();
    }

    async initialize() {
        await this.initializeTable();
        this.initializeTableEvents();
        //this.initializeCreateEvent();
        //this.initializeUpdateEvent();
        //this.initializeDeleteEvent();
        this.initializeResetEvent();
    }

    async initializeTable() {
        try {
            let urlUserID = parseInt(document.getElementById("url_user_id").value),
                users = await this.model.read();

            this.view.buildTable(users);

            // Did we navigate here with a person selected?
            if (urlUserID) {
                let user = await this.model.readOne(urlUserID);
                this.view.updateEditor(user);

            // Otherwise, nope, so leave the editor blank    
            } else {
                this.view.reset();
            }
            this.initializeTableEvents();
        } catch(err) {
            this.view.errorMessage(err);
        }
    }

    initializeTableEvents() {
        document.querySelector("table tbody").addEventListener("click", (evt) => {
            let target = evt.target.parentElement,
                userid = target.getAttribute("data-userid"),
                user_name = target.getAttribute("data-user_name"),
                email = target.getAttribute("data-email");

            this.view.updateEditor({
                userid: userid,
                user_name: user_name,
                email: email
            });

        });
    }

    initializeResetEvent() {
        document.getElementById("reset").addEventListener("click", async (evt) => {
            evt.preventDefault();
            this.view.reset();
        });
    }
}

// Create the VC components
const view = new View();
const controller = new Controller(user_model, view);

// Export the MVC components as the default
export default {
    user_model,
    view,
    controller
};