import {getButtonState, changeButtonState} from "./utils.js";
import { socket } from "./socket.js";
import {tr} from "./main.js";

/*
    Listen for workspace changes and send Blockly events
    to other clients.
*/
export function workspaceListener(event) {
    // doUpdate(event, workspaceLoading); // TODO
    // Finished loading.
    if (event.type == Blockly.Events.FINISHED_LOADING) {
        window._workspaceLoading = false;
        return;
    } else if (window._workspaceLoading) {
        return;
    }
    if (!event.isUiEvent) {
        if ((getButtonState() != "UNSAVED") && !window._workspaceLoading)
            changeButtonState("UNSAVED");
        // Send event to other people who working on same workspace.
        if (socket.connected && !window._blockSendingEvents) {
            socket.emit("relay_workspace_push", event.toJson());
        }
        // If socket is not connected, save as offline edit.
        if (!socket.connected && !window._blockSendingEvents) {
            if (window._offlineEvents == undefined)
                window._offlineEvents = [];
            window._offlineEvents.push(event.toJson());
        }
        window._blockSendingEvents = false;
    }
}

/*
    Warn user before leaving with unsaved changes.
*/
window.addEventListener("beforeunload", function (e) {
    if (!["UNSAVED", "SAVE", "FAIL"].includes(getButtonState()))
        return;
    const msg = tr("web.exit_prompt");
    (e || window.event).returnValue = msg;
    return msg;
});