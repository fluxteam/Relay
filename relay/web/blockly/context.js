import { 
    registerContextMenu, 
    isFunctionCall, 
    isListener, 
    isWebhookEvent, 
    isEvent, 
    isFunction, 
    scrollToBlock,
    copyText,
    getWebhookURL,
    convertId,
    getMarkedBlocks,
    getVariableByName,
    saveJSON,
    logOpen
} from "./utils.js";
import {workspace, tr} from "./main.js";

const ScopeType = Blockly.ContextMenuRegistry.ScopeType;

/*
    ----------------------------
    CONTEXT CALLBACKS
    ----------------------------
*/

/*
    Saves marked blocks as JSON.
*/
function _contextExportMarkedBlocks() {
    const exported = getMarkedBlocks();
    if (!exported)
        return;
    if (window._markedToast) {
        window._markedToast.hideToast();
        window._markedToast = null;
    }
    saveJSON(exported, "workspace");
}

/*
    Saves all blocks in workspace as JSON.
*/
function _contextExportAllBlocks() {
    const saved = Blockly.serialization.workspaces.save(workspace);
    saveJSON(saved, "workspace");
}

/*
    Saves a block as JSON.
*/
function _contextExportBlock(scope) {
    const saved = Blockly.serialization.blocks.save(scope.block, {
        addCoordinates: true,
        addInputBlocks: true,
        addNextBlocks: true,
        doFullSerialization: true
    });
    saveJSON(saved, scope.block.type);
} // TODO: unused

/*
    Marks a block for exporting later.
*/
function _contextMarkBlock(scope) {
    if (window._markedForExport == undefined)
        window._markedForExport = [];
    if (window._markedForExport.includes(scope.block)) {
        scope.block.pathObject.svgRoot.classList.remove("blocklyMarked");
        window._markedForExport.splice(window._markedForExport.indexOf(scope.block), 1);
    } else {
        scope.block.pathObject.svgRoot.classList.add("blocklyMarked");
        window._markedForExport.push(scope.block);
    }
    _showExportToast();
}

/*
    Go function from function call block.
*/
function _contextGoFunction(scope) {
    for (const block of workspace.getBlocksByType("FUNCTION_CREATE")) {
        if (block.getFieldValue("function_id") == scope.block.getFieldValue("function_id")) {
            scrollToBlock(block);
            return;
        }
    }
}

/*
    Clears all marked blocks.
*/
function _contextClearMark() {
    for (const elem of document.getElementsByClassName("blocklyMarked")) {
        elem.classList.remove("blocklyMarked");
    }
    window._markedForExport = [];
    _showExportToast();
}

/*
    Copies a webhook URL.
*/
function _contextCopyWebhookURL(scope) {
    copyText(getWebhookURL(scope.block.id), tr("web.webhook_copied"));
}

/*
    Copies ID of the block.
*/
function _contextCopyWorkflowID(scope) {
    copyText(convertId(scope.block.id), tr("web.id_copied"));
}

/*
    Opens a new window to view logs
    of a listener.
*/
function _contextViewLogs(scope) {
    logOpen(convertId(scope.block.id));
}

/*
    Renames a function.
*/
function _contextRenameFunction(scope) {
    Blockly.Variables.renameVariable(workspace, workspace.getVariableById(scope.block.getFieldValue("function_id")), function(vari) {
        if (vari) {
            scope.block.getField("name").setValue(vari);
            for (const block of workspace.getBlocksByType("FUNCTION_CALL")) {
                if (block.getFieldValue("function_id") == scope.block.getFieldValue("function_id"))
                    block.getField("name").setValue(vari);
            }
        }
    });
}

/*
    Shows export toast.
    TODO: Simplify.
*/
function _showExportToast() {
    if (window._markedToast) {
        window._markedToast.hideToast();
        window._markedToast = null;
    }
    if ((!window._markedForExport) || (window._markedForExport.length == 0))
        return;
    window._markedToast = Toastify({
        text: tr("web.blocks_selected").replace("{0}", window._markedForExport.length),
        duration: -1,
        close: false,
        gravity: "bottom",
        position: "center",
        style: {
            background: "#000",
            color: "#f690dc"
        },
        onClick: function() {
            window._markedToast.hideToast();
            _contextExportMarkedBlocks();
        }
    })
    window._markedToast.showToast();
}


/*
    ----------------------------
    BUTTON HANDLERS
    ----------------------------
*/

function _callbackGlobalVariable(button) {
    Blockly.Variables.createVariableButtonHandler(workspace, null, "GLOBAL");
}

function _callbackLocalVariable(button) {
    Blockly.Variables.createVariableButtonHandler(workspace, null, "LOCAL");
}

function _callbackFunctionVariable(button) {
    Blockly.Variables.createVariableButtonHandler(workspace, (param) => {
        if (param) {
            const metrics = workspace.getMetrics();
            const bl = workspace.newBlock("FUNCTION_CREATE");
            const f = getVariableByName(param, "FUNCTION").getId();
            bl.initSvg();
            bl.render();
            bl.getField("name").setValue(param);
            bl.getField("function_id").setValue(f);
            bl.moveBy(
                (metrics.viewWidth - bl.width) / workspace.scale, 
                (metrics.viewHeight - bl.height) / workspace.scale
            );
            scrollToBlock(bl);
        }
    }, "FUNCTION");
}


/*
    Register extra context menu items.
*/
export function registerContext() {
    registerContextMenu("CONTEXT_COPY_WEBHOOK_URL", (scope) => _contextCopyWebhookURL(scope), ScopeType.BLOCK, 0, [isWebhookEvent]);
    registerContextMenu("CONTEXT_COPY_WORKFLOW_ID", (scope) => _contextCopyWorkflowID(scope), ScopeType.BLOCK, 0, [isEvent]);
    registerContextMenu("CONTEXT_VIEW_LIVE_LOGS", (scope) => _contextViewLogs(scope), ScopeType.BLOCK, 0, [isEvent]);
    registerContextMenu("CONTEXT_RENAME_FUNCTION", (scope) => _contextRenameFunction(scope), ScopeType.BLOCK, 2, [isFunction]);
    registerContextMenu("CONTEXT_GO_FUNCTION", (scope) => _contextGoFunction(scope), ScopeType.BLOCK, 2, [isFunctionCall]);
    registerContextMenu("CONTEXT_MARK_FOR_EXPORT", (scope) => _contextMarkBlock(scope), ScopeType.BLOCK, 5, [isListener, (x) => { return !x.disabled; }]);
    registerContextMenu("CONTEXT_CLEAR_MARK", (scope) => _contextClearMark(), ScopeType.WORKSPACE, 5, [(x) => { return (window._markedForExport) ? window._markedForExport.length != 0 : false; }]);
    registerContextMenu("CONTEXT_EXPORT_BLOCKS_MARKED", (scope) => _contextExportMarkedBlocks(), ScopeType.WORKSPACE, 5, [(x) => { return (window._markedForExport) ? window._markedForExport.length != 0 : false; }]);
    registerContextMenu("CONTEXT_EXPORT_BLOCKS_ALL", (scope) => _contextExportAllBlocks(), ScopeType.WORKSPACE, 5);
}

export function registerButtons() {
    workspace.registerButtonCallback("CREATE_GLOBAL_VARIABLE", _callbackGlobalVariable);
    workspace.registerButtonCallback("CREATE_LOCAL_VARIABLE", _callbackLocalVariable);
    workspace.registerButtonCallback("CREATE_FUNCTION_VARIABLE", _callbackFunctionVariable);
}