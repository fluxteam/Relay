/**
    Creates a new element.

    @param {String} tag
    @param {object} attributes
    @param {Array} children
    @returns {HTMLElement}
*/
function element(tag, attributes, children = []) {
    elem = document.createElement(tag);
    for (const key in attributes) {
        // If value is true, then add a blank attribute,
        // if false, then don't add the attribute.
        if (typeof attributes[key] == "boolean") {
            if (attributes[key] == true) {
                elem.setAttribute(key, "");
            }
        }
        // If key is innerHTML, then add in innerHTML.
        else if (key == "innerHTML") {
            elem.innerHTML = attributes[key];
        }
        // Else set attribute as it is.
        else {
            elem.setAttribute(key, attributes[key]);
        }
    }
    // Add children to element.
    for (let index = 0; index < children.length; index++) {
        elem.insertAdjacentHTML("beforeend", children[index].outerHTML);
    }
    return elem;
}

/**
    Creates a Edit button.
*/
function inputEdit() {
    return element("button", {
        "type": "button",
        "class": "element-button",
        "onclick": "addDialog(this);",
        "innerHTML": `<i class="ti ti-external-link"></i>&nbsp;&nbsp;Edit`
    })
}

/**
    Creates a BOOLEAN input.
*/
function inputBoolean(id, value = null, placeholder = "---", options = null) {
    return element("select",
    {
        "name": id,
        "relay-type": "boolean"
    }, [
        element("option", {"value": "", "innerHTML": "Boolean", "selected": value == null}),
        element("option", {"value": "true", "innerHTML": "✔ " + "true", "selected": value == true}),
        element("option", {"value": "false", "innerHTML": "❌ " + "false", "selected": value == false})
    ]);
}

/**
    Creates a STRING input.
*/
function inputString(id, value = null, placeholder = "", options = null) {
    return element("input",
    {
        "type": "text",
        "name": id,
        "relay-type": "string",
        "value": value || "",
        "placeholder": "String"
    });
}

/**
    Creates a NUMBER input.
*/
function inputNumber(id, value = null, placeholder = "", options = null) {
    return element("input",
    {
        "type": "number",
        "name": id,
        "relay-type": "number",
        "value": value || "",
        "placeholder": "Number",
        "step": "any"
    });
}

/**
    Creates a SNOWFLAKE input.
*/
function inputSnowflake(id, value = null, placeholder = "", options = null) {
    return element("input",
    {
        "type": "text",
        "name": id,
        "relay-type": "snowflake",
        "pattern": "[0-9]{15,}",
        "value": value || "",
        "placeholder": "ID"
    });
}

/**
    Creates a MAPPING input.
*/
function inputMapping(id, value = null, placeholder = "", options = null) {
    return element("div", {"relay-attribute": "mapping"}, [
        inputString(id),
        inputEdit()
    ]);
}

/**
    Creates a LIST input.
*/
function inputList(id, value = null, placeholder = "", options = null) {
    return inputEdit();
}

/**
    Creates a BLANK input.
*/
function inputNone(id, value = null, placeholder = "", options = null) {
    return element("input",
    {
        "type": "text",
        "name": id,
        "relay-type": "none",
        "value": "Empty",
        "disabled": true
    });
}