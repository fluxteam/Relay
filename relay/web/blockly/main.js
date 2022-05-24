/**
    Load string files.
 */
import * as strings from "/strings.js";
import * as blockly_data from "/blockly.js";
export const tr = (key) => key.split('.').reduce((previous, current) => previous[current], strings._);

// Fill variables.
export const RELAY_DOCS = blockly_data._["docs_url"];
export const BLOCKS = blockly_data._["blocks"];
export const THEME = blockly_data._["theme"];
export const BLOCK_NAMES = blockly_data._["block_names"];
export const BLOCK_EXTRA = blockly_data._["extra"];
export const TOOLBOX = blockly_data._["toolbox"];

import fileSaver from "https://cdn.skypack.dev/pin/file-saver@v2.0.5-UsWqrW8RsYF08S1pEHIw/mode=imports,min/optimized/file-saver.js";
import {
    setBlocklyMessages, 
    createPreferences, 
    populateFunctions, 
    labelProgress, 
    addProgress, 
    showParticipants,
    nextTutorial,
    prevTutorial,
    closeTutorial,
    changeButtonState,
    getButtonState,
    showToast,
    getSetting,
    showTour,
    logClose,
    logToggleAutoScroll,
    logClear
} from "./utils.js";
import "./extra/mutators.js";
import {workspaceListener} from "./listener.js";
import {registerButtons, registerContext} from "./context.js";
import {socket} from "./socket.js";
import {registerParameter} from "./extra/lexical_fields.js";
import * as LexicalVariables from "./extra/lexical_variables.js";

export var workspace = null;
var backpack = null;

window.LexicalVariables = LexicalVariables;
window.fileSaver = fileSaver;

Blockly.FieldDropdown.ARROW_CHAR = "▼";

registerParameter();
setBlocklyMessages(BLOCK_NAMES);
Blockly.defineBlocksWithJsonArray(BLOCKS);

/*
    Create Blockly workspace, inject Backpack and load lexical variables.
    This can be called multiple times.
*/
function blockly(blocks, backpack_contents = null) {
    const opt = createPreferences(TOOLBOX, THEME);
    document.getElementById("workspace").innerHTML = "";
    window._workspaceLoading = true;
    workspace = Blockly.inject('workspace', opt.workspace);
    const bckp = backpack_contents || backpack.getContents();
    if (backpack)
        backpack.dispose();
    backpack = new Backpack(workspace, opt.backpack);
    backpack.init();
    backpack.setContents(bckp);
    LexicalVariables.init(workspace);
    registerButtons();
    registerContext();
    workspace.addChangeListener((event) => {
        // Check for warnings only if user enabled warnings.
        if ((event.type != Blockly.Events.BUBBLE_OPEN) && getSetting("warnings")) {
            // TODO: Implement warnings again.
            // doWarnings(event);
        }
        workspaceListener(event);
    });
    Blockly.serialization.workspaces.load(blocks, workspace, {
        recordUndo: false
    });
    if (getSetting("keep_toolbox_open")) {
        workspace.toolbox_.flyout_.autoClose = false;
    }
}

function loadStage1() {
    labelProgress(tr("web.progress_stage_1"));
    // Fetch workspace blocks.
    fetch(ENDPOINT_WORKSPACE).then(response => {
        if (response.ok) {
            window._blocksReady = true;
            return response.json();
        } else {
            window._blocksReady = false;
            throw new Error("Falling back to pull blocks from socket.");
        }
    })
    .then(data => {
        loadStage2(data);
        setTimeout(() => socket.connect(), 100);
    })
    .catch((error) => {
        // TODO: Is there a better way for checking Blockly errors?
        if (error.message.startsWith("Unknown block type")) {
            labelProgress(tr("web.corrupted_blocks"))
        } else {
            labelProgress(tr("web.progress_failed"))
        }
        throw error;
    })
}

export function loadStage2(data) {
    labelProgress(tr("web.progress_stage_2"));
    window._workspaceTutorials = data.tutorials;
    window._workspacePreferences = data.preferences || {};
    populateFunctions(data.workspace.variables);
    blockly(data.workspace, data.backpack, data.preferences);
    addProgress(40, "API");
}

export function loadStage3() {
    labelProgress(tr("web.progress_stage_3"));
    if (typeof dialogPolyfill != "undefined") {
        for (const el of document.querySelectorAll("dialog")) { dialogPolyfill.registerDialog(el); }
    }
    document.getElementById("save-button").className = "element-button";
    addProgress(40, "EXTRA");
}

function saveBlocks() {
    if (!["UNSAVED", "NONE"].includes(getButtonState()))
        return;
    changeButtonState("SAVE");
    // Save blocks and backpack.
    fetch(ENDPOINT_SAVE, {method: "POST", headers: {"Content-Type": "application/json;charset=UTF-8"}, body: 
        JSON.stringify({
            workspace: Blockly.serialization.workspaces.save(workspace),
            backpack: backpack.getContents()
        })
    }).then(response => {
        if (response.ok) {
            changeButtonState("DONE");
            return response.json();
        } else {
            changeButtonState("FAIL");
        }
    }).then(data => {
        console.clear();
        console.log(JSON.stringify(data, null, 4));
        // If Discord couldn't save application commands, 
        // show toast about that.
        // TODO
        if (data["errors"].includes("DISCORD_SAVE_ERROR")) {
            console.error(tr("actions.error_discord_commands"));
        }
    })
    .catch((error) => { changeButtonState("FAIL"); showToast(tr("web.progress_failed")); });
}

// Start loading blockly.
loadStage1();

// Expose functions to page.
window.showParticipants = showParticipants;
window.prevTutorial = prevTutorial;
window.closeTutorial = closeTutorial;
window.nextTutorial = nextTutorial;
window.saveBlocks = saveBlocks;
window.showTour = showTour;
window.logClose = logClose;
window.logClear = logClear;
window.logToggleAutoScroll = logToggleAutoScroll;
window.addProgress = addProgress;