import {clients} from "./socket.js";
import {tr, BLOCK_EXTRA, TOOLBOX} from "./main.js";

/*
    Checks for listeners and events.
*/
export const isEvent            = (block) => block.type.startsWith("WORKFLOW_") && block.type.endsWith("_LISTENER");
export const isFunction         = (block) => block.type == "FUNCTION_CREATE";
export const isFunctionCall     = (block) => block.type == "FUNCTION_CALL";
export const isGatewayEvent     = (block) => block.type == "WORKFLOW_EVENT_LISTENER";
export const isWebhookEvent     = (block) => block.type == "WORKFLOW_WEBHOOK_LISTENER";
export const isInteractionEvent = (block) => isEvent(block) && (!isGatewayEvent(block)) && (!isWebhookEvent(block));
export const isListener         = (block) => isEvent(block) || isFunction(block);
export const isRestrictedEvent  = (type)  => ["WEBHOOK", "INTERACTION_CREATE"].includes(type);

export const getWebhookURL      = (id) => `${window.location.protocol}//${window.location.host}/hooks/${WORKSPACE_SERVER_ID}/${convertId(id)}`;

/*
    Converts a text to title case.
*/
export const titleCase = (str) => str.toLowerCase().replace(/\b(\w)/g, s => s.toUpperCase());

/*
    Converts a single character (from a Blockly ID)
    to a two-digit numeric string.
*/
export const convertChar = (char) => ("00" + ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%()*+,-./:;=?@[]^_`{|}~".indexOf(char) + 1)).slice(-"00".length);

/*
    Converts a Blockly ID to a numeric string.
    We do this to fix problems which caused by characters.
*/
export const convertId = (text) => {
    var id = [];
    for (var i = 0; i < text.length; i++) {
        id.push(convertChar(text.charAt(i)));
    }
    return id.join("");
}

/*
    Gets the event name from listener.
    For gateway events; this will be selected option from "event" dropdown.
    For webhooks; "WEBHOOK". For other listeners; "INTERACTION_CREATE"
*/
export function getEventValue(block) {
    return isGatewayEvent(block) ? block.getFieldValue("event") : isWebhookEvent(block) ? "WEBHOOK" : "INTERACTION_CREATE";
}

/*
    Adds a warning to a block,
    and optionally for the root block.
*/
export function addWarning(block, text, apply_root = true) {
    block.setWarningText(text, text);
    if (apply_root)
        addWarning(block.getRootBlock(), text, false);
}

/*
    Removes a warning from a block,
    and optionally for the root block.
*/
export function removeWarning(block, text, apply_root = true) {
    if (!text)
        return;
    block.setWarningText(null, text);
    if (apply_root)
        removeWarning(block.getRootBlock(), text, false);
}

/*
    A shortcut to register a context menu item.
*/
export function registerContextMenu(name, callback, scope, weight = 0, precondition = null) {
    Blockly.ContextMenuRegistry.registry.register({
        displayText: function() { 
            return Blockly.Msg[name]; 
        },
        preconditionFn: precondition ? (scope) => {
            for (const test of precondition) { 
                if (!test(scope.block)) 
                    return 'hidden';
                if (scope.block && scope.block.isInFlyout)
                    return 'hidden';
            }
            return 'enabled';
        } : (scope) => 'enabled',
        callback: callback, 
        scopeType: scope, 
        id: name, 
        weight: weight
    });
}

/*
    Gets an avatar URL.
*/
export function getAvatarUrl(id, tag, hash = null, extension = "jpg", size = 128, allow_animated = false) {
    const cdn = "https://cdn.discordapp.com";
    var is_animated = !hash || !allow_animated ? false : hash.startswith("a_")
    if (hash)
        return `${cdn}/avatars/${id}/${hash}.${is_animated ? 'gif' : extension}` + (size ? `?size=${size}` : "")
    else
        return `${cdn}/embed/avatars/${tag % 5}.png`
}

/*
    Get help URL for a listener block.
*/
export function getListenerHelp(block) {
    const root = block.getRootBlock();
    const eventUrl = "/docs/api/actions/events#";
    const webhookUrl = "/docs/actions#webhook";
    if (isGatewayEvent(root)) {
        return eventUrl + root.getFieldValue("event").toLowerCase();
    } else if (isWebhookEvent(root)) {
        return webhookUrl;
    } else if (isInteractionEvent(root)) {
        return eventUrl + "interaction_create";
    }
    return null;
}

/*
    Get help URL for a built-in block.
*/
export function getBlockHelp(category, name) {
    if (category == "DISCORD") {
        return "/docs/api/actions/discord#relay.actions.discord.Discord." + name.toLowerCase();
    }
    else if (category == "DISCORDM") {
        var override = null;
        // Override for block names that has more than 1 word.
        switch (name) {
            case "EMBEDAUTHOR":
                override = "EMBED_AUTHOR"; break;
            case "EMBEDFIELD":
                override = "EMBED_FIELD"; break;
            case "EMBEDFOOTER":
                override = "EMBED_FOOTER"; break;
            default:
                override = name; break;
        }
        return "/docs/api/actions/entities#" + override.replace("MODEL_", "").replaceAll("_", "-").toLowerCase();
    }
    else {
        return `https://pyconduit.ysfchn.com/blocks/${category.toLowerCase()}/#pyconduit.categories.${category.toLowerCase()}.${titleCase(category)}.${name.toLowerCase()}`;
    }
}

/*
    Get unviewed tutorials.
*/
export function getTutorials(viewed_tutorials = [], return_all = false) {
    const TUTORIALS = BLOCK_EXTRA["CHANGELOG"];
    // Build a list for unviewed tutorials.
    var tutorials = [];
    // Get splash items.
    const all_splash = TUTORIALS["all"][TUTORIALS["all"].findIndex((e) => e.is_splash)];
    const extra_splash = TUTORIALS["extra"][TUTORIALS["extra"].findIndex((e) => e.is_splash)];
    // If there are viewed tutorials,
    // use the new tutorial splash as first page.
    if (viewed_tutorials.length != 0) {
        extra_splash["title"] = tr(`changelog.${extra_splash.id}.title`);
        extra_splash["description"] = tr(`changelog.${extra_splash.id}.description`);
        tutorials.push(extra_splash);
    } else {
        all_splash["title"] = tr(`changelog.${all_splash.id}.title`);
        all_splash["description"] = tr(`changelog.${all_splash.id}.description`);
        tutorials.push(all_splash);
    }
    // Loop over all tutorials.
    for (const t of (((viewed_tutorials.length != 0) || return_all) ? TUTORIALS["all"].concat(TUTORIALS["extra"]) : TUTORIALS["extra"])) {
        if (!(viewed_tutorials.includes(t.id)) && !t.is_splash) {
            t["title"] = tr(`changelog.${t.id}.title`);
            t["description"] = tr(`changelog.${t.id}.description`);
            tutorials.push(t);
        }
    }
    // If there are no new tutorials, return empty array instead.
    if (tutorials.length == 1) {
        return [];
    }
    return tutorials;
}

/*
    Check if there is a new tutorial to view.
*/
export function hasNewTutorials(viewed_tutorials = []) {
    return getTutorials(viewed_tutorials || []) != 0;
}

/*
    Export JSON as a file.
*/
export function saveJSON(object, filename = null) {
    var blob = new Blob([JSON.stringify(object, null, 4)], {type: "application/json;charset=utf-8"});
    fileSaver.saveAs(blob, (filename || "file") + ".json");
}

/*
    Plays a sound effect.
*/
export function playSound(id) {
    if (!getSetting("enable_sounds"))
        return;
    var audio = new Audio(BLOCK_EXTRA["SOUNDS"][id]);
    audio.play();
}

/*
    Set blockly messages.
*/
export function setBlocklyMessages(block_names) {
    // Set blockly messages.
    for (const source in BLOCK_EXTRA["PREFIXES"]) {
        const target = BLOCK_EXTRA["PREFIXES"][source];
        for (const key in tr(target)) {
            Blockly.Msg[(source == "_" ? "" : source + "_") + key] = tr(target + "." + key); 
        }
    }
    // Set blockly help URLs.
    for (let i = 0; i < block_names.length; ++i) {
        const element = block_names[i];
        const parts = element.split(".");
        const category = parts[0];
        const name = parts.slice(1).join('.');
        Blockly.Msg["HELP_" + category + "_" + name.replaceAll(".", "_")] = getBlockHelp(category, name);
    }
}

/*
    Reads a user setting.
*/
export function getSetting(id) {
    var items = [];
    for (const i of BLOCK_EXTRA["SETTINGS"]) {
        items = items.concat(i["items"]);
    }
    const setting = items[items.findIndex((e) => e.id == id)];
    if (setting == undefined) {
        throw new Error(`Setting "${id}" doesn't exists.`);
    }
    const val = window._workspacePreferences[id];
    // Let's make sure someone didn't mess up the values.
    switch (setting["type"]) {
        case "BOOLEAN":
            return (val != undefined) ? !!val : setting["default"];
        case "OPTION":
            return !setting.options.includes(val) ? setting["default"] : val;
        default:
            break;
    }
}

/*
    Create preferences for injecting 
    workspace and adding backpack.
*/
export function createPreferences(toolbox, theme) {
    const horizontal = getSetting("horizontal");
    const hide_grid = getSetting("hide_grid");
    const snap_grid = getSetting("snap_grid");
    const sounds = getSetting("enable_sounds");
    var renderer = getSetting("renderer");
    const zoomWheel = getSetting("zoom_with_wheel");
    const tlbx = toolbox;
    // Hide advanced blocks if they are disabled.
    if (!getSetting("advanced_blocks")) {
        for (const b of BLOCK_EXTRA["FLAGS"]["advanced_blocks"]) {
            const toolboxIndex = tlbx["contents"].findIndex((e) => e["toolboxitemid"] == b[0]);
            const blockIndex = tlbx["contents"][toolboxIndex]["contents"].findIndex((e) => e["type"] == b[1]);
            tlbx["contents"][toolboxIndex]["contents"].splice(blockIndex, 1);
        }
    }
    return {
        "workspace": {
            "toolbox": tlbx,
            "theme": theme,
            "renderer": renderer,
            "horizontalLayout": horizontal,
            "toolboxPosition": horizontal ? "end" : "start",
            "sounds": sounds,
            "grid": hide_grid ? null : {
                "spacing": 20,
                "length": 3,
                "colour": '#1c1c1c',
                "snap": snap_grid ? true : false
            },
            "move": {
                "scrollbars": {
                    "horizontal": true,
                    "vertical": true
                },
                "drag": true,
                "wheel": !zoomWheel
            },
            "zoom": {
                "controls": true,
                "wheel": zoomWheel,
                "startScale": 1.0,
                "maxScale": 3,
                "minScale": 0.3,
                "scaleSpeed": 1.2,
                "pinch": true
            }
        },
        "backpack": {
            "allowEmptyBackpackOpen": false
        }
    }
}

/*
    Show toast on screen.
*/
export function showToast(text, color = null, avatar = null, gravity = "top") {
    const toast = Toastify({
        "avatar": avatar,
        "text": text,
        "duration": 3000,
        "close": false,
        "gravity": gravity,
        "position": "center",
        "stopOnFocus": true,
        "escapeMarkup": false,
        "style": {
            "background": "#000",
            "color": color || "#fff"
        },
        "onClick": function() {
            toast.hideToast();
        }
    }).showToast();
}

/*
    Create function blocks from variable names.
*/
export function populateFunctions(variables) {
    if (!variables)
        return
    var opt = [];
    for (const varl of variables) {
        if (varl.type == "FUNCTION") {
            opt.push([varl.name, varl.id]);
        }
    }
    if (opt.length == 0)
        return
    for (const tl of TOOLBOX["contents"]) {
        if (tl.toolboxitemid == "DEFINITION") {
            for (let index = 0; index < opt.length; index++) {
                tl.contents.splice(2 + index, 0, {kind: "block", type: "FUNCTION_CALL", enabled: true, fields: {
                    name: opt[index][0], function_id: opt[index][1]
                }});
            }
        }
    }
}

/*
    Hide progress and show tutorials if there any.
*/
export function hideProgress() {
    // Delete loading and show workspace.
    setTimeout(() => {
        const wrks = document.getElementById("main");
        document.getElementById("workspace-loading").remove();
        document.getElementById("workspace-header").removeAttribute("style");
        wrks.style.display = "flex";
        // Show tutorial dialog if there are unviewed tutorials.
        if (hasNewTutorials(window._workspaceTutorials)) {
            nextTutorial();
            document.getElementById("tutorial").showModal();
        }
        setTimeout(() => refreshSize(), 1500);
    }, 1000);
}

/*
    Workaround to re-render blockly area without loading blocks again.
*/
export function refreshSize() {
    window.dispatchEvent(new UIEvent('resize', { }));
}

/*
    Opens the logs.
*/
export function logOpen(block_id) {
    const logs = document.getElementById("workspace-logs");
    logClear();
    logs.style.display = "flex";
    logs.setAttribute("workflow", block_id);
    refreshSize();
    logInsert({
        "log": block_id
    })
}

/*
    Closes the logs.
*/
export function logClose() {
    const logs = document.getElementById("workspace-logs");
    logs.style.display = "none";
    logs.removeAttribute("workflow");
    refreshSize();
}

/*
    Clears the logs.
*/
export function logClear() {
    document.getElementsByClassName("log-drain")[0].innerHTML = "";
}

/*
    Log toggle auto-scroll.
*/
export function logToggleAutoScroll() {
    const btn = document.getElementById("scroll-button");
    if (btn.getAttribute("autoscroll") != "0") {
        btn.innerHTML = btn.innerHTML.replace("arrow-big-down-lines", "arrow-big-down");
        btn.title = tr("actions.manual_scroll");
        btn.setAttribute("autoscroll", "0");
    } else {
        btn.innerHTML = btn.innerHTML.replace("arrow-big-down", "arrow-big-down-lines");
        btn.title = tr("actions.auto_scroll");
        btn.setAttribute("autoscroll", "1");
    }
}

/*
    Inserts a log item.
*/
export function logInsert(data) {
    // Check if we received log for this workflow.
    var logs = document.getElementById("workspace-logs");
    if (data.workflow && (logs.getAttribute("workflow") != data.workflow)) {
        return;
    }
    // Get the log colors.
    var style = null;
    switch (data["log_type"] || "SYSTEM") {
        case "SUCCESS":
            style = ["#62da29", "#62da2926", tr("actions.log_success_block")];
            break;
        case "ERROR":
            style = ["#da2929", "#da292926", tr("actions.log_error_block")];
            break;
        case "INFO":
            style = ["#909090", "#2c2c2c26", tr("actions.log_info_block")];
            break;
        default:
            style = ["#296eda", "#296eda26", ""];
            break;
    }
    // Add a new log item.
    var log_drain = document.getElementsByClassName("log-drain")[0];
    var fragment = document.createElement("div");
    fragment.className = "log-content";
    fragment.style.backgroundColor = style[1];
    fragment.style.color = style[0];
    fragment.innerText = (style[2] ? style[2] + "\n" : "") + data["log"];
    log_drain.appendChild(fragment);
    // Check if auto-scroll enabled.
    const btn = document.getElementById("scroll-button");
    if (btn.getAttribute("autoscroll") != "0")
        log_drain.scrollTo({ top: log_drain.scrollHeight, left: 0, behavior: 'smooth' });
}

/*
    Add step for increasing loading progress.
    Steps also have ID to prevent increasing progress with same ID.
*/
export function addProgress(value, key, exists_callback = null) {
    if (window._addedSteps == undefined)
        window._addedSteps = [];
    if (window._addedSteps.includes(key)) {
        if (exists_callback)
            exists_callback();
        return;
    }
    window._addedSteps.push(key);
    if (document.getElementById("workspace-loading")) {
        var x = document.getElementById("progress").style.width.replace("%", "");
        var val = ((+x) + (value || 0)) || 0;
        if (val > 100)
            val = 100;
        document.getElementById("progress").style.width = val + "%";
        if (val == 100)
            hideProgress();
    }
}

/*
    Add information to progress.
*/
export function labelProgress(label) {
    const el = document.getElementById("workspace-loading-text");
    if (el)
        document.getElementById("workspace-loading-text").innerText = label;
}

/*
    Load the currently selected tutorial.
*/
export function loadTutorial() {
    const tutorials = getTutorials(window._workspaceTutorials || []);
    const step = +(document.getElementById("tutorial").getAttribute("relay-step"));
    const tutorial = tutorials[step - 1];
    const isVideo = tutorial.media.endsWith(".mp4");
    // Load tutorial media.
    document.getElementById("tutorial-title").innerHTML = tutorial.title;
    document.getElementById("tutorial-description").innerHTML = tutorial.description;
    document.getElementById(isVideo ? "tutorial-video" : "tutorial-image").src = tutorial.media;
    document.getElementById("tutorial-image").style.display = isVideo ? "none" : "";
    document.getElementById("tutorial-video").style.display = isVideo ? "" : "none";
    // Play media if it is a video.
    if (isVideo)
        document.getElementById("tutorial-video").play();
    // Show controls.
    if (step == 1) {
        document.getElementById("tutorial-prev-button").setAttribute("disabled", "");
        document.getElementById("tutorial-next-button").removeAttribute("disabled");
    } else if (step == tutorials.length) {
        document.getElementById("tutorial-prev-button").removeAttribute("disabled");
        document.getElementById("tutorial-next-button").setAttribute("disabled", "");
        document.getElementById("tutorial-exit-button").style.display = "";
    } else {
        document.getElementById("tutorial-prev-button").removeAttribute("disabled");
        document.getElementById("tutorial-next-button").removeAttribute("disabled");
    }
}

/*
    Switch to next tutorial.
*/
export function nextTutorial() {
    const step = +(document.getElementById("tutorial").getAttribute("relay-step"));
    document.getElementById("tutorial").setAttribute("relay-step", (step + 1).toString());
    loadTutorial();
}

/*
    Switch to previous tutorial.
*/
export function prevTutorial() {
    const step = +(document.getElementById("tutorial").getAttribute("relay-step"));
    document.getElementById("tutorial").setAttribute("relay-step", (step - 1).toString());
    loadTutorial();
}

/*
    Close the tutorial.
*/
export function closeTutorial() {
    document.getElementById("tutorial").close();
}

/*
    Show a list of participants.
    TODO: Improve
*/
export function showParticipants() {
    var prtc = [];
    for (const c of Object.values(clients)) {
        if (!prtc[c.id]) {
            prtc.push(c);
        }
    }
    // Send participants as toasts.
    for (const user of Object.values(prtc).slice().reverse()) {
        showToast(user.username, "#fff", getAvatarUrl(user.id, user.discriminator, user.avatar_hash));
    }
    showToast(tr("actions.participants"), "#fff");
}

/*
    Scroll to a block.
*/
export function scrollToBlock(block) {
    const MARGIN = 20;
    const position = block.getRelativeToSurfaceXY();
    const w = Blockly.getMainWorkspace();
    const metrics = w.getMetrics();
    const x = position.x * w.scale - metrics.contentLeft;
    const y = position.y * w.scale - metrics.contentTop;
    w.scrollbar.set(x - MARGIN, y - MARGIN);
    block.select();
}

/*
    Copies a text to clipboard.
*/
export function copyText(text, msg) {
    navigator.clipboard.writeText(text);
    showToast(msg);
}

/*
    Gets a Blockly variable from name.
*/
export function getVariableByName(name, type = "") {
    for (const vr of Blockly.getMainWorkspace().getVariablesOfType(type)) { 
        if ((vr.name == name) && (vr.type == type)) 
            return vr; 
    }
    return null;
}

/*
    Export marked blocks.
*/
export function getMarkedBlocks() {
    const exported = {"blocks": {"languageVersion": 0, "blocks": []}};
    for (const block of (window._markedForExport || [])) {
        if (isListener(block)) {
            exported["blocks"]["blocks"].push(Blockly.serialization.blocks.save(block, {
                addCoordinates: true,
                addInputBlocks: true,
                addNextBlocks: true,
                doFullSerialization: true
            }));
        }
    }
    return (exported["blocks"]["blocks"].length == 0) ? null : exported;
}

/*
    Locks/unlocks the save button.
*/
export function changeButtonState(state = "NONE") {
    const btn = document.getElementById("save-button");
    btn.blur();
    btn.style.removeProperty("background-color");
    btn.setAttribute("data-state", state);
    if ((state == "NONE") || (state == "UNSAVED")) {
        btn.className = state == "NONE" ? "element-button" : "form-button";
        btn.innerHTML = `<i class="ti ti-device-floppy"></i>&nbsp;&nbsp;${tr('common.save')}`;
        btn.removeAttribute("disabled");
    } else if (state == "SAVE") {
        btn.className = "element-button shimmer shimmer-save";
        btn.innerHTML = `<i class="ti ti-rotate-clockwise spin"></i>&nbsp;&nbsp;${tr('web.save_starting')}`;
        btn.setAttribute("disabled", "");
    } else if (state == "DONE") {
        btn.className = "element-button";
        btn.style.backgroundColor = "#4fff4299";
        btn.innerHTML = tr('web.save_done');
        btn.removeAttribute("disabled");
        playSound("save_done");
        setTimeout(() => changeButtonState("NONE"), 1000);
    } else if (state == "FAIL") {
        btn.className = "element-button";
        btn.style.backgroundColor = "#ff584299";
        btn.innerHTML = tr('web.save_error');
        btn.removeAttribute("disabled");
        playSound("save_fail");
        setTimeout(() => changeButtonState("NONE"), 1000);
    }
}

/*
    Gets the button state.
*/
export function getButtonState() {
    return document.getElementById("save-button").getAttribute("data-state") || "NONE";
}

/*
    Show tutorial screen.
    TODO: Not implemented yet.
*/
export function showTour(step = 0) {
    const maxSteps = 10;
    if ((step > (maxSteps - 1)) || (step < 0)) {
        throw Error("Invalid tour number: " + step);
    }
    // Hide the existing tutorial toast.
    if (window._tutorialToast) {
        window._tutorialToast.hideToast();
        window._tutorialToast = null;
    }
    // An element for showing tutorial progress.
    const progressDiv = `
        <div class="tour-progress">
            <span class="tour-step">${step > (maxSteps - 2) ? maxSteps - 2 : step}/${(maxSteps - 2)}</span>
            <div class="tour-bar">
                <div class="tour-bar-filled" style="width: ${step < 2 ? 0 : (100 / (maxSteps - 2)) * (step - 2)}%"></div>
            </div>
            <button class="element-button element-button-second" style="margin: 0px; display: ${(step + 1) > (maxSteps - 1) ? 'none' : 'initial'}" onclick="showTour(${step + 1})">Atla</button>
        </div>`;
    const startDiv = `
        <br><br><button class="element-button form-button" onclick="showTour(1);">${tr("web.start_tutorial")}</button>
        <button class="element-button element-button-second" onclick="window._tutorialToast.hideToast(); window._tutorialToast = null;">${tr("web.no_thanks")}</button>
        `;
    const tours = [];
    window._tutorialToast = Toastify({
        "text": (step != 0 ? progressDiv : "") + tours[step].replaceAll("\n", "<br>") + (step == 0 ? startDiv : ""),
        "duration": -1,
        "close": false,
        "gravity": "bottom",
        "position": "right",
        "stopOnFocus": true,
        "escapeMarkup": false,
        "style": { "background": "#000", "color": "#fff", "cursor": "default" }
    }).showToast();
    if (step > 0) {
        setTimeout(() => {
            document.getElementsByClassName("tour-bar-filled")[0].style.width = ((100 / (maxSteps - 2)) * (step - 1)) + "%";
        }, 500);
    }
}