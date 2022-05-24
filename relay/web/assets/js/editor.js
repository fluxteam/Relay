/*
    Functions for Relay Frontend.
*/

window.onload = function() {
    // Register all dialogs if dialogPolyfill exists.
    if (typeof dialogPolyfill != "undefined") {
        var dialogs = document.querySelectorAll("dialog");
        for (let index = 0; index < dialogs.length; index++) {
            dialogPolyfill.registerDialog(dialogs[index]);
        }
    }
    // Show form.
    var form = document.getElementById("form");
    if (form) {
        form.removeAttribute("style");
    }
}

// -----------------------------------------
// UTILS
// -----------------------------------------

// Gets nodes of element but only includes children of parent.
function querySelectorAllParent(elem, selector) {
    var elements = elem.querySelectorAll(selector);
    var elements_output = [];
    for (let index = 0; index < elements.length; index++) {
        if (elements[index].parentNode == elem) {
            elements_output.push(elements[index]);
        }
    }
    return elements_output
}

// Gets nodes of element but only includes children of parent.
function querySelectorParent(elem, selector) {
    return querySelectorAllParent(elem, selector)[0] || null;
}

// -----------------------------------------
// FUNCTIONS
// -----------------------------------------

/**
    Shows the parent dialog element from existing element.

    @param {Element} elem
*/
function showDialog(elem) {
    var element = querySelectorParent(elem.parentNode, "dialog");
    element.showModal();
}

/**  
    Adds a dialog input.

    @param {Element} elem
    @param {String} id
    @param {Function} inputFunc
    @param {Boolean} show_hidden
*/
function addDialogInput(elem, id, inputFunc, show_hidden = true) {
    // Get all buttons.
    var buttons = elem.parentNode.querySelectorAll("button");
    // Remove style from all buttons.
    for (let index = 0; index < buttons.length; index++) {
        if (show_hidden) {
            buttons[index].removeAttribute("relay-ui");
        } else {
            var attrb = buttons[index].getAttribute("relay-ui");
            if (attrb == "selected") {
                buttons[index].removeAttribute("relay-ui");
            }
        }
    }
    // Add style for clicked element.
    elem.setAttribute("relay-ui", "selected");
    // Get content div of the dialog.
    var dialog_content = elem.parentNode.parentNode.querySelector(".dialog-content");
    var dialog_field = document.createElement("div");
    dialog_field.setAttribute("relay-attribute", "field");
    dialog_field.innerHTML = inputFunc(id).outerHTML;
    dialog_content.innerHTML = dialog_field.outerHTML;
    dialog_content.removeAttribute("relay-export");
    // Add plus / minus buttons if inputFunc is list or mapping generator.
    if (inputFunc == inputMapping || inputFunc == inputList) {
        // Add a "multiple" attribute to check if this is a list or mapping later.
        dialog_content.setAttribute("relay-export", inputFunc == inputMapping ? "mapping" : "list");
        dialog_content.insertAdjacentHTML("beforeend", element("button", {
            "class": "element-button",
            "onclick": "addField(this, true)",
            "innerHTML": "<i class=\"ti ti-plus\"></i>"
        }).outerHTML);
        dialog_content.insertAdjacentHTML("beforeend", "\n ");
        dialog_content.insertAdjacentHTML("beforeend", element("button", {
            "class": "element-button",
            "onclick": "deleteField(this)",
            "innerHTML": "<i class=\"ti ti-minus\"></i>"
        }).outerHTML);
    }
}

/**
    Create a new input by copying the first one.
    If first one is not exists ("hidden") then show it instead.

    @param {Element} elem
    @param {Boolean} is_dialog
*/
function addField(elem, is_dialog = false) {
    var elements = querySelectorAllParent(elem.parentNode, '*[relay-attribute="field"]');
    if (elements[0]) {
        if (elements[0].style.display == "none") {
            // Clear all inner dialogs for the "ANY" field.
            if (is_dialog) {
                var dialogs = elements[0].querySelectorAll("dialog");
                for (let index = 0; index < dialogs.length; index++) {
                    dialogs[index].remove();
                }
            }
            // Make it visible.
            elements[0].removeAttribute("style");
        } else {
            // Clone previous element.
            var cloned = elements[0].cloneNode(true);
            // Clear all inner dialogs for the "ANY" field.
            var dialogs = cloned.querySelectorAll("dialog");
            for (let index = 0; index < dialogs.length; index++) {
                dialogs[index].remove();
            }
            clearField(cloned);
            elem.parentNode.insertBefore(cloned, elem);
        }
    }
};


/**
    Create a new dialog by copying the parent one.

    @param {Element} elem
*/
function addDialog(elem) {
    // Get outer dialog in a "field".
    var current_dialog = elem.parentNode.parentNode.parentNode;
    // However, mapping field contains an another <div>, so if element is not a dialog,
    // try going up to parent one more.
    if (current_dialog.tagName != "DIALOG") {
        current_dialog = elem.parentNode.parentNode.parentNode.parentNode;
    }
    // If element is not in a dialog, get previous field's dialog.
    if (current_dialog.tagName != "DIALOG") {
        current_dialog = elem.parentNode.parentNode.parentNode.querySelector("dialog");
    }
    // Check if dialog is not added already.
    if (querySelectorParent(elem.parentNode, "dialog") == null) {
        // We can't clone a dialog because it gives error when trying to open the 
        // new dialog as the source dialog already opened. So we are creating a new
        // dialog element.
        new_dialog = document.createElement("dialog");
        new_dialog.className = current_dialog.className;
        new_dialog.setAttribute("name", current_dialog.getAttribute("name"));
        // We need to delete dialog elements in parent dialog,
        // so new dialog won't contain inner dialogs.
        cloned_dialog = current_dialog.cloneNode(true);
        var cloned_dialog_dialogs = cloned_dialog.querySelectorAll("dialog");
        for (let index = 0; index < cloned_dialog_dialogs.length; index++) {
            cloned_dialog_dialogs[index].remove();
        }
        // Copy the innerHTML.
        new_dialog.innerHTML = cloned_dialog.innerHTML;
        // Change the tab to "None".
        var none_button = new_dialog.querySelector('.button-tabs > *[relay-dialog="none"]');
        addDialogInput(none_button, new_dialog.getAttribute("name"), inputNone);
        // Register new dialog.
        dialogPolyfill.registerDialog(new_dialog);
        elem.parentNode.insertBefore(new_dialog, elem);
    }
    querySelectorParent(elem.parentNode, "dialog").showModal();
};

/**
    Exports the custom value to JSON.

    @param {Element} dialog
*/
function exportDialog(dialog) {
    var dialog_data = null;
    // Get dialog content <div>.
    var content = dialog.querySelector(".dialog-content");
    // Get export mode.
    var export_mode = content.getAttribute("relay-export") || null;
    // Get a list of inner visible fields.
    var fields = querySelectorAllParent(content, '*[relay-attribute="field"]:not([style*="display: none"])');
    // If field is blank, return none.
    if (fields.length == 0) {
        dialog_data = null;
    }
    // If field is one length list, then return the field value.
    else if ((fields.length == 1) && (export_mode == null)) {
        dialog_data = getField(fields[0].querySelector("*[relay-type]"));
    }
    // If field is contains more than more field, then search for all dialogs.
    else {
        // If field is a key/value mapping,
        if (export_mode == "mapping") {
            dialog_data = {};
            for (let index = 0; index < fields.length; index++) {
                var key = fields[index].querySelector('*[relay-attribute="mapping"]').querySelector('*[relay-type]');
                var value = fields[index].querySelector('*[relay-attribute="mapping"]').querySelector('dialog');
                // Check if a dialog exists.
                if (getField(key) == null) {
                    continue
                } else if (value == null) {
                    dialog_data[getField(key)] = null;
                } else {
                    dialog_data[getField(key)] = exportDialog(value);
                }
            }
        }
        // If field is a list.
        else if (export_mode == "list") {
            dialog_data = [];
            for (let index = 0; index < fields.length; index++) {
                var value = fields[index].querySelector('dialog');
                // Check if a dialog exists.
                if (value != null) {
                    dialog_data.push(exportDialog(value));
                }
            }
        }
    }
    return dialog_data;
}


/**
    Delete the last created field.
    If there is only one element, then hide it instead.
    
    @param {Element} elem
*/
function deleteField(elem) {
    var elements = querySelectorAllParent(elem.parentNode, '*[relay-attribute="field"]');
    if (elements.length > 1) {
        elements[elements.length - 1].remove();
    } else if (elements.length == 1) {
        elements[0].style.display = "none";
        // If element contains a dialog, then change the tab to None.
        var dialog = elements[0].querySelector("dialog");
        if (dialog != null) {
            // Change the tab to "None".
            var none_button = dialog.querySelector('.button-tabs > *[relay-dialog="none"]');
            addDialogInput(none_button, dialog.getAttribute("name"), inputNone);
        }
        clearField(elements[0]);
    }
};


/**
    Delete the all fields.
    If there is only one element, then hide it instead.
    
    @param {Element} elem
*/
function deleteAllField(elem) {
    var elements = elem.parentNode.querySelectorAll('*[relay-attribute="field"]');
    for (let index = 0; index < elements.length; index++) {
        if (index == 0) {
            elements[index].style.display = "none";
            clearField(elements[index]);
        } else {
            elements[index].remove();
        }
    }
};


/**
    Clears value of all form elements inside the specified element.

    @param {Element} elem
*/
function clearField(elem) {
    // Delete value from inner inputs.
    field_nodes = elem.querySelectorAll('*[relay-type]');
    for (let index = 0; index < field_nodes.length; index++) {
        field_nodes[index].value = "";
    }
};


/**
    Gets the value of a element.

    @param {Element} elem
*/
function getField(elem) {
    if (elem.tagName == "DIALOG")
        return exportDialog(elem);
    return processInput(elem.value, elem.getAttribute("relay-type"));
}


/**
    Convert string values (as form elements store the value as string)
    to their values before sending it to server.
    
    TODO: Merge the repeating lines

    @param {object} data
    @param {string} type
    @returns {any}
*/
function processInput(data, type) {
    switch (type) {
        // Null
        case "none":
            return null;
        // Boolean
        case "boolean":
            return data == "true" ? true : data == "false" ? false : null;
        // Number
        case "number":
            return data == "" ? null : +data;
        // String
        case "string":
            return data == "" ? null : data;
        // Snowflake
        case "snowflake":
            return data == "" ? null : data;
        // Choice
        case "choice":
            return data == "" ? null : data;
        // Any
        case "any":
            return data == "" ? null : data;
        // Default
        default:
            return data == "" ? null : data;
    }
}


/**
    Relay uses JavaScript instead of typical HTML Form to send the forms as
    default HTML submitting method has several drawbacks such as not accepting non-ASCII values
    and having no support for nested values.

    @returns {object}
*/
function getFormData() {
    var data = {};
    var elements = document.querySelectorAll(
        '*[relay-attribute="container"] > *[relay-attribute="field"] > *[relay-type],' + 
        '*[relay-attribute="container"] > *[relay-attribute="field"] > dialog,' +
        '*[relay-attribute="container"] > *[relay-attribute="field"] > *[relay-attribute="mapping"]'
    );
    for (let index = 0; index < elements.length; index++) {
        const element = elements[index];
        // If element is hidden, skip it.
        // Doesn't applies for mapping fields, because they needs to have its name in the form data even if its empty.
        if (element.style.display == "none")
            continue
        // Check if input is a mapping field.
        else if (element.getAttribute("relay-attribute") == "mapping") {
            // Get key and value elements.
            var key = element.querySelectorAll('*[relay-type]')[0];
            var value = element.querySelectorAll('*[relay-type]')[1] || element.querySelector('dialog');
            // If main data doesn't contain the object key,
            // add it first.
            if (!(key.getAttribute("name") in data)) {
                data[key.getAttribute("name")] = {};
            }
            // Abort if key or value is empty.
            if ((getField(key) == null) || ((getField(value) == null) && (value.tagName != "DIALOG")))
                continue
            data[key.getAttribute("name")][getField(key)] = getField(value);
        } else {
            // Abort if value is empty for non-dialog elements.
            if ((element.tagName != "DIALOG") && (getField(element) == null))
                continue
            // Add value to the list if parent element contains a + or - button.
            var is_list = querySelectorParent(element.parentNode.parentNode, ".element-button") ? true : false;
            // If main data already contains the object key,
            // append to the list.
            if (element.getAttribute("name") in data) {
                if (Array.isArray(data[element.getAttribute("name")])) {
                    data[element.getAttribute("name")].push(getField(element));
                } else {
                    data[element.getAttribute("name")] = [data[element.getAttribute("name")], getField(element)];
                }
            } else {
                if (is_list) {
                    data[element.getAttribute("name")] = [];
                    // Don't include value for supporting zero-sized dialog lists.
                    if ((element.tagName == "DIALOG") && (element.parentNode.style.display != "none")) {
                        data[element.getAttribute("name")].push(getField(element));
                    }
                } else {
                    data[element.getAttribute("name")] = getField(element);
                }
            }
        }
    }
    return data;
};


/**
    Relay uses JavaScript instead of typical HTML Form to send the forms as
    default HTML submitting method has several drawbacks such as not accepting non-ASCII values
    and having no support for nested values.

    @returns {object}
*/
function getActionData() {
    var data = {};
    // Add steps.
    data["steps"] = [];
    var elements = document.querySelectorAll(
        '*[relay-attribute="parameter"]'
    );
    // Add metadata.
    data["name"] = getField(document.querySelector('input[name="action_name"]'));
    data["description"] = getField(document.querySelector('input[name="action_description"]'));
    // Parse events.
    data["events"] = [];
    // Get a list of events.
    var event_list = document.querySelector('div[name="action_events_list"] > table').rows;
    for (let event_pos = 0; event_pos < event_list.length; event_pos++) {
        // Get checkbox from row.
        var checkbox = event_list[event_pos].querySelector("td > input");
        if (checkbox && checkbox.checked) {
            data["events"].push(checkbox.value);
        }
    }
    // Get a list of steps.
    for (let index = 0; index < elements.length; index++) {
        const element = elements[index];
        // If step is hidden, skip it.
        if (element.style.display == "none")
            continue
        // Get step ID.
        var step_id = getField(element.querySelector('input[name="id"]'));
        var step_action = getField(element.querySelector('input[name="action"]'));
        var step_condition = getField(element.querySelector('dialog[name="if"]'));
        var step_parameters = getField(element.querySelector('dialog[name="parameters"]'));
        // Add step to result.
        data["steps"].push({
            "action": step_action ? step_action.toUpperCase() : "",
            "id": step_id,
            "if": step_condition,
            "parameters": step_parameters || {}
        })
    }
    return data;
};


/**
    Hides the error banner by setting the style attribute of
    elements that has "error" class.
*/
function hideError() {
    location.href = "#";
    var elem = document.querySelector(".error");
    if (!elem)
        return
    elem.style.display = "none";
    var text = document.querySelector(".error > span");
    text.innerHTML = "";
};


/**
    Shows a error banner by setting the inner content and
    changing the style attribute of elements that has "error" class.

    @param {object} errors
*/
function showError(errors) {
    var elem = document.querySelector(".error");
    if (!elem)
        return
    elem.removeAttribute("style");
    var text = document.querySelector(".error > span");
    text.innerHTML = "";
    if (Array.isArray(errors)) {
        for (let index = 0; index < errors.length; index++) {
            text.innerHTML = text.innerHTML + "<br>・ " + errors[index];
        }
    } else {
        text.innerHTML = text.innerHTML + "<br>・ " + errors;
    }
    scrollError();
};


/**
    Scrolls a element to the bottom.

    @param {Element} elem
*/
function scrollToBottom(elem) {
    elem.scrollTo({ top: elem.scrollHeight, left: 0, behavior: 'smooth' });
}


/**
    Scrolls to the error banner.
*/
function scrollError() {
    location.href = "#";
    location.href = "#errorbox";
}


/**
    Switches a tab for .button-tabs

    @param {Element} elem
*/
function switchTab(elem, callback) {
    for (const e of querySelectorAllParent(elem.parentNode, 'button[relay-ui]')) {
        e.setAttribute('relay-ui', '');
    }
    elem.setAttribute('relay-ui', 'selected');
    elem.blur();
    callback();
}


/** 
    Toggle optional parameters.
*/
function toggleParameters(toggle = true) {
    // Show form.
    var form = document.getElementById("form");
    if (form) {
        if (toggle)
            form.removeAttribute("hide-optional");
        else
            form.setAttribute("hide-optional", "");
    }
}


/** 
    Redirect user to install page from overview page.
*/
function closeOverview(install_url) {
    var server = document.getElementById("server");
    if ((!server) || (!server.value))
        return;
    window.location.href = install_url.replace('{}', server.value);
}


/** 
    Installs a package from overview page directly.
*/
function installOverview(post_url, success_url) {
    var server = document.getElementById("server");
    if ((!server) || (!server.value))
        return;
    httpRequest('POST', post_url.replace('{}', server.value), getFormData(), success_url);
}


/**
    Makes a XHR request.
    If server returns a success code, redirect to a 
    page that says operation has completed. But if not, show a error banner with
    showError() function.

    @param {string} method
    @param {string} url
    @param {string} data
    @param {string} success_url
    @param {string} success_message
*/
function httpRequest(method, url, data, success_url, success_message = null) {
    var xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var response = null;
            try {
                response = JSON.parse(xhr.responseText);
            } catch (e) {
                response = null;
            }
            // Show error if payload is incorrect.
            if ((xhr.status != 200) && response == null) {
                showError("Unhandled exception. The service has returned " + xhr.status);
            } else if ((xhr.status != 200) && ("description" in response)) {
                showError(response.description);
            } else {
                hideError();
                if (success_url) {
                    window.location.replace(success_url);
                } else {
                    alert(success_message || "Done!");
                }
            }
        }
    };
    xhr.send(JSON.stringify(data));
};