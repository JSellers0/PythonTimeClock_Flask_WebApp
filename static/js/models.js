import { server_endpoint } from "./endpoint.js"

class ClientsModel {
    async readAll() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/clients`, options);
        let data = await response.json();
        return data;
    }

    async readOne(clientid) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/clients/${clientid}`, options);
        let data = await response.json();
        return data;
    }

    async create(client) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(client)
        };
        let response = await fetch(`${server_endpoint}/clients/`, options);
        let data = await response.json();
        return data;
    }

    async update(clientid, client) {
        // Doesn't Exist Yet!
        let options = {
            method: "PUT",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(client)
        };
        let response = await fetch(`${server_endpoint}/clients/${clientid}`, options);
        let data = await response.json();
        return data;
    }

    async delete(clientid) {
        // Doesn't Exist Yet!
        let options = {
            method: "DELETE",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/clients/${clientid}`, options);
        return response;
    }
}

class ProjectsModel {
    async readAll() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/projects`, options);
        let data = await response.json();
        return data;
    }

    async readOne(projectid) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/projects/${projectid}`, options);
        let data = await response.json();
        return data;
    }

    async create(project) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(project)
        };
        let response = await fetch(`${server_endpoint}/projects/`, options);
        let data = await response.json();
        return data;
    }

    async update(projectid, project) {
        // ToDo: Add update to projects object/swagger file.
        let options = {
            method: "PUT",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(project)
        };
        let response = await fetch(`${server_endpoint}/projects/${projectid}`, options);
        let data = await response.json();
        return data;
    }

    async delete(projectid) {
        // Doesn't Exist Yet!
        let options = {
            method: "DELETE",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/projects/${projectid}`, options);
        return response;
    }
}

class UsersModel {
    async readAll() {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/users`, options);
        let data = await response.json();
        return data;
    }

    async readOne(userid) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/users/${userid}`, options);
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
        let response = await fetch(`${server_endpoint}/users`, options);
        let data = await response.json();
        return data;
    }

    async update(user) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: JSON.stringify(user)
        };
        let response = await fetch(`${server_endpoint}/users/${user.userid}`, options);
        let data = await response.json();
        return data;
    }

    async delete(userid) {
        let options = {
            method: "DELETE",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/users/${userid}`, options);
        return response;
    }
}

class TimelogModel {
    async readUserRows(userid) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/timelog/users/${userid}`, options);
        let data = await response.json();
        return data;
    }

    async readUserCurrentRow(userid) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            }
        };
        let response = await fetch(`${server_endpoint}/timelog/users/${userid}/current`, options);
        let data = await response.json();
        return data;
    }

    async readUserRowsDateRange(userid, daterange) {
        let options = {
            method: "GET",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: json.stringify(daterange)
        };
        let response = await fetch(`${server_endpoint}/timelog/users/${userid}/daterange`, options);
        let data = await response.json();
        return data;
    }

    async updateUserCurrentRow(userid, timelog){
        let options = {
            method: "PUT",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body: json.stringify(timelog)
        };
        let response = await fetch(`${server_endpoint}/timelog/users/${userid}/current`, options);
        let data = await response.json();
        return data;
    }

    async create(userid, timelog) {
        let options = {
            method: "POST",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body = json.stringify(timelog)
        };
        let response = await fetch(`${server_endpoint}/timelog/users/${userid}`, options);
        let data = await response.json();
        return data;
    }

    async updateRow(timelogid, timelog) {
        let options = {
            method: "PUT",
            cache: "no-cache",
            headers: {
                "Content-Type": "application/json",
                "accepts": "application/json"
            },
            body = json.stringify(timelog)
        };
        let response = await fetch(`${server_endpoint}/timelog/${timelogid}`, options);
        let data = await response.json();
        return data;
    }

    // ToDo: deleteRow

}

// Create the models
const client_model = new ClientModel();
const project_model = new ProjectModel();
const timelog_model = new TimelogModel();
const user_model = new UserModel();

// Export the MVC components as the default
export default {
    client_model,
    project_model,
    timelog_model,
    user_model
};