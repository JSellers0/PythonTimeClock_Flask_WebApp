class Model {
    async read() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch("http://ec2-54-166-143-158.compute-1.amazonaws.com/api/users", options);
        let data = await response.json();
        return data;
    }

    async create(user) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(user)
        };
        let response = await fetch("http://ec2-54-166-143-158.compute-1.amazonaws.com/api/users", options);
        let data = await response.json();
        return data;
    }

}

class View {
    constructor() {
        this.NEW_NOTE = 0;
        this.EXISTING_NOTE = 1;
        this.table = document.querySelector(".users table");
        this.userid = document.getElementById("userid");
        this.user_name = document.getElementById("user_name");
        this.email = document.getElementById("email");
        this.createButton = document.getElementById("create");
    }

    reset() {
        this.userid.textContent = "";
        this.user_name.textContent = "";
        this.email.textContent = "";
        this.user_name.focus();
    }

    buildTable(users) {
        let tbody,
            html = "";

        // Iterate over the users and build the table
        users.forEach((user) => {
            html += `
            <tr data-user_id="${user.userid}" data-user_name="${user.user_name}" data-email="${user.email}>
                <td class="name">${user.user_name}</td>
            </tr>`;
        });
        // Is there currently a tbody in the table?
        if (this.table.tBodies.length !== 0) {
            this.table.removeChild(this.table.getElementsByTagName("tbody")[0]);
        }
        // Update tbody with our new content
        tobdy = this.table.createTBody();
        tbody.innerHTML = html;
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
            
        }
    }
}


// Create the MVC components
const model = new Model();
const view = new View();
const controller = new Controller(model, view);

// Export the MVC components as the default
export default {
    model,
    view,
    controller
};