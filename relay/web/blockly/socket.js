import {showToast, addProgress, logInsert} from "./utils.js";
import {loadStage2, loadStage3, workspace, tr} from "./main.js";

export const socket = io(window.location.protocol + "//" + window.location.host + "/user", { 
    autoConnect: false,
    reconnection: true,
    reconnectionDelay: 1000,
    timeout: 2000
});

export var clients = null;

socket.on("relay_workspace", (data) => {
    // INIT event.
    if ((data.type == "INIT")) {
        console.info("Connected to Realtime services.");
        addProgress(20, "SOCKET", () => {
            showToast(tr("actions.socket_connected"), "#65ff65", null, "bottom");
        });
        // Pull blocks.
        if (data.workspace) {
            loadStage2(data);
        }
        loadStage3();
        // Add success to log window.
        logInsert({
            "log_type": "SUCCESS",
            "log": tr("actions.socket_connected")
        });
    /*
        Blockly event payloads. When someone triggers a Blockly event,
        it is shared over other clients, and these clients executes the event.
    */
    } else if ((data.type == "PAYLOAD") && workspace) {
        var event = Blockly.Events.fromJson(data.data, workspace);
        window._blockSendingEvents = true;
        event.run(true);
    /*
        Workflow logs. When an workflow has executed, its log is displayed
        on the pop-up window. As window are opened by Workspace, we can
        directly access the method in that page.
    */
    } else if ((data.type == "WORKFLOW_LOG")) {
        logInsert({ 
            "log": data.log, 
            "log_type": data.log_type, 
            "workflow": data.workflow, 
            "event": data.event 
        });
    /*
        When a new user has joined, they will get the current blocks,
        so they can see all changes even without saving the blocks.
    */
    } else if ((data.type == "LOAD_BLOCKS")) {
        blockly(data.data.workspace);
        showToast(tr("actions.synced_blocks"));
        // Execute offline events.
        if (window._offlineEvents) {
            for (const e of window._offlineEvents) {
                window._blockSendingEvents = false;
                Blockly.Events.fromJson(e, workspace).run(true);
            }
        }
    /*
        When a new user has joined, ask the current user to
        share blocks with them.
    */
    } else if ((data.type == "NEED_SYNC")) {
        socket.emit(
            "relay_workspace_sync", { 
                "workspace": Blockly.serialization.workspaces.save(workspace) 
            }
        );
    /*
        Show toasts for joined/left users.
    */
    } else if ((data.type == "USER_REFRESH")) {
        const users = [(clients || {}), data.users];
        const statuses = [];
        const seen_ids = [];
        // Loop through users two times, one is for current users, and other one is
        // for updated users. If current users list doesn't contain one of updated users, this means
        // a "JOIN", if updated users list doesn't contain one of current users, this means a "LEFT". 
        for (let i = 0; i < users.length; i++) {
            for (const key in users[i]) {
                if (key == socket.id)
                    continue
                // Check if other list contain this user.
                if (!(users[+!i][key])) {
                    const user = users[i][key];
                    if (user.id == WORKSPACE_USER_ID)
                        continue
                    if (seen_ids.includes(user.id))
                        continue
                    statuses.push({
                        "type": i == 0 ? "LEFT" : "JOIN",
                        "avatar": getAvatarUrl(user.id, user.discriminator, user.avatar_hash),
                        "username": user.username
                    })
                }
            }
        }
        // Update participants count.
        document.getElementById("participants-count").innerHTML = Object.keys(data.users).length;
        // Don't show toast on first load.
        if (clients == null) {
            clients = data.users;
            return;
        }
        clients = data.users;
        // Show toasts for every user.
        // TODO: Simplify
        for (const value of statuses) {
            const text = tr(`actions.user_${value.type == "LEFT" ? "left" : "joined"}`).replace("{0}", `<span style="color: #fff">${user.username}</span>`);
            showToast(text, "#666666", value.avatar);
        }
    } else {
        showToast(data.message || "Unknown error.", "#ff5c5c");
    }
});

socket.on("connect", () => {  
    console.info("Connecting with Relay Realtime Services...");
    socket.emit("relay_workspace_init", { 
        "server": WORKSPACE_SERVER_ID, 
        // Pull blocks only if fetch() has failed.
        "pull_blocks": !window._blocksReady 
    });
});

socket.on("disconnect", () => {
    showToast(tr("actions.error_socket_disconnected"), "#ff5c5c", null, "bottom");
    // Add error to log window.
    logInsert({
        "log_type": "ERROR",
        "log": tr("actions.error_socket_disconnected")
    });
});

socket.on("connect_error", () => {
    // TODO: Localize error message.
    console.log("Couldn't connect to Socket.IO, retrying...");
    socket.connect();
})