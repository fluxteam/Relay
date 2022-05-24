import { getEventValue, getListenerHelp, isEvent } from "../utils.js";

// TODO: Cleanup

const GENERIC_MUTATOR = {
    /**
     * Block for creating a list with any number of elements of any type.
     * @this {Block}
     */
    init: null,
    /**
     * Create XML to represent list inputs.
     * Backwards compatible serialization implementation.
     * @return {!Element} XML storage element.
     * @this {Block}
     */
    mutationToDom: function () {
        const container = Blockly.utils.xml.createElement('mutation');
        container.setAttribute('items', this.itemCount_);
        return container;
    },
    /**
     * Parse XML to restore the list inputs.
     * Backwards compatible serialization implementation.
     * @param {!Element} xmlElement XML storage element.
     * @this {Block}
     */
    domToMutation: function (xmlElement) {
        this.itemCount_ = parseInt(xmlElement.getAttribute('items'), 10);
        this.updateShape_();
    },
    /**
     * Returns the state of this block as a JSON serializable object.
     * @return {{itemCount: number}} The state of this block, ie the item count.
     */
    saveExtraState: function () {
        return {
            'itemCount': this.itemCount_,
        };
    },
    /**
     * Applies the given state to this block.
     * @param {*} state The state to apply to this block, ie the item count.
     */
    loadExtraState: function (state) {
        this.itemCount_ = state['itemCount'];
        this.updateShape_();
    },
    /**
     * Populate the mutator's dialog with this block's components.
     * @param {!Workspace} workspace Mutator's workspace.
     * @return {!Block} Root block in mutator.
     * @this {Block}
     */
    decompose: function (workspace) {
        const containerBlock = workspace.newBlock(this.container_name_);
        containerBlock.initSvg();
        let connection = containerBlock.getInput('STACK').connection;
        for (let i = 0; i < this.itemCount_; i++) {
            const itemBlock = workspace.newBlock(this.container_item_);
            itemBlock.initSvg();
            connection.connect(itemBlock.previousConnection);
            connection = itemBlock.nextConnection;
        }
        return containerBlock;
    },
    /**
     * Reconfigure this block based on the mutator dialog's components.
     * @param {!Block} containerBlock Root block in mutator.
     * @this {Block}
     */
    compose: function (containerBlock) {
        let itemBlock = containerBlock.getInputTargetBlock('STACK');
        // Count number of inputs.
        const connections = [];
        while (itemBlock && !itemBlock.isInsertionMarker()) {
            connections.push(itemBlock.valueConnection_);
            itemBlock =
                itemBlock.nextConnection && itemBlock.nextConnection.targetBlock();
        }
        // Disconnect any children that don't belong.
        for (let i = 0; i < this.itemCount_; i++) {
            const connection = this.getInput('value' + i).connection.targetConnection;
            if (connection && connections.indexOf(connection) === -1) {
                connection.disconnect();
            }
        }
        this.itemCount_ = connections.length;
        this.updateShape_();
        // Reconnect any child blocks.
        for (let i = 0; i < this.itemCount_; i++) {
            Blockly.Mutator.reconnect(connections[i], this, 'value' + i);
        }
    },
    /**
     * Store pointers to any connected child blocks.
     * @param {!Block} containerBlock Root block in mutator.
     * @this {Block}
     */
    saveConnections: function (containerBlock) {
        let itemBlock = containerBlock.getInputTargetBlock('STACK');
        let i = 0;
        while (itemBlock) {
            const input = this.getInput('value' + i);
            itemBlock.valueConnection_ = input && input.connection.targetConnection;
            itemBlock =
                itemBlock.nextConnection && itemBlock.nextConnection.targetBlock();
            i++;
        }
    },
    /**
     * Modify this block to have the correct number of inputs.
     * @private
     * @this {Block}
     */
    updateShape_: function () {
        if (this.itemCount_ && this.getInput('EMPTY')) {
            this.removeInput('EMPTY');
        } else if (!this.itemCount_ && !this.getInput('EMPTY')) {
            this.appendDummyInput('EMPTY').appendField(
                this.empty_msg_
            );
        }
        // Add new inputs.
        for (let i = 0; i < this.itemCount_; i++) {
            if (!this.getInput('value' + i)) {
                const input = this.appendValueInput('value' + i).setCheck(this.item_check_).setAlign(Blockly.ALIGN_RIGHT);
                if (i === 0) {
                    input.appendField(this.item_msg_);
                }
            }
        }
        // Remove deleted inputs.
        for (let i = this.itemCount_; this.getInput('value' + i); i++) {
            this.removeInput('value' + i);
        }
    },
};


Blockly.Blocks['LISTS_CREATE'] = {
    /**
     * Block for creating a list with any number of elements of any type.
     * @this {Block}
     */
    init: function () {
        this.setHelpUrl("");
        this.setStyle('lists_blocks');
        this.itemCount_ = 3;
        this.empty_msg_ = Blockly.Msg['BLOCK_LISTS_CREATE_EMPTY'];
        this.item_msg_ = Blockly.Msg['BLOCK_LISTS_CREATE'];
        this.container_name_ = "lists_create_with_container";
        this.container_item_ = "lists_create_with_item";
        this.item_check_ = null;
        this.updateShape_();
        this.setOutput(true, 'List');
        this.setMutator(new Blockly.Mutator(['lists_create_with_item']));
        this.setTooltip(Blockly.Msg["TOOLTIP_LISTS_CREATE"]);
    },
    mutationToDom: GENERIC_MUTATOR["mutationToDom"],
    domToMutation: GENERIC_MUTATOR["domToMutation"],
    saveExtraState: GENERIC_MUTATOR["saveExtraState"],
    loadExtraState: GENERIC_MUTATOR["loadExtraState"],
    decompose: GENERIC_MUTATOR["decompose"],
    compose: GENERIC_MUTATOR["compose"],
    saveConnections: GENERIC_MUTATOR["saveConnections"],
    updateShape_: GENERIC_MUTATOR["updateShape_"]
};


Blockly.Blocks['DICTIONARY_CREATE'] = {
    /**
     * Block for creating a list with any number of elements of any type.
     * @this {Block}
     */
    init: function () {
        this.setHelpUrl("");
        this.setStyle('dictionary_blocks');
        this.itemCount_ = 3;
        this.empty_msg_ = Blockly.Msg['BLOCK_DICTIONARY_CREATE_EMPTY'];
        this.item_msg_ = Blockly.Msg['BLOCK_DICTIONARY_CREATE'];
        this.container_name_ = "dictionary_create_with_container";
        this.container_item_ = "dictionary_create_with_item";
        this.item_check_ = "Pair";
        this.updateShape_();
        this.setOutput(true, 'Dictionary');
        this.setMutator(new Blockly.Mutator(['dictionary_create_with_item']));
        this.setTooltip(Blockly.Msg["TOOLTIP_DICTIONARY_CREATE"]);
    },
    mutationToDom: GENERIC_MUTATOR["mutationToDom"],
    domToMutation: GENERIC_MUTATOR["domToMutation"],
    saveExtraState: GENERIC_MUTATOR["saveExtraState"],
    loadExtraState: GENERIC_MUTATOR["loadExtraState"],
    decompose: GENERIC_MUTATOR["decompose"],
    compose: GENERIC_MUTATOR["compose"],
    saveConnections: GENERIC_MUTATOR["saveConnections"],
    updateShape_: GENERIC_MUTATOR["updateShape_"]
};


Blockly.Blocks['lists_create_with_container'] = {
    init: function () {
        this.setStyle('lists_blocks');
        this.appendDummyInput().appendField(Blockly.Msg['MUTATOR_LIST_CONTAINER']);
        this.appendStatementInput('STACK');
        this.setTooltip("");
        this.contextMenu = false;
    },
};

Blockly.Blocks['lists_create_with_item'] = {
    init: function () {
        this.setStyle('lists_blocks');
        this.appendDummyInput().appendField(Blockly.Msg['MUTATOR_LIST_ITEM']);
        this.setPreviousStatement(true);
        this.setNextStatement(true);
        this.setTooltip("");
        this.contextMenu = false;
    },
};

Blockly.Blocks['dictionary_create_with_container'] = {
    init: function () {
        this.setStyle('dictionary_blocks');
        this.appendDummyInput().appendField(Blockly.Msg['MUTATOR_DICTIONARY_CONTAINER']);
        this.appendStatementInput('STACK');
        this.setTooltip("");
        this.contextMenu = false;
    },
};

Blockly.Blocks['dictionary_create_with_item'] = {
    init: function () {
        this.setStyle('dictionary_blocks');
        this.appendDummyInput().appendField(Blockly.Msg['MUTATOR_DICTIONARY_ITEM']);
        this.setPreviousStatement(true);
        this.setNextStatement(true);
        this.setTooltip("");
        this.contextMenu = false;
    },
};

Blockly.Extensions.register(
    'event_help_builder', 
    function() {
        var block = this;
        block.setHelpUrl(function() { return getListenerHelp(block) || null });
    }
);

// Custom field label to store data without creating a view in UI.
export const FieldLabelContext = function(opt_value, opt_class, opt_config) {
    FieldLabelContext.superClass_.constructor.call(
        this, opt_value, opt_class, opt_config);
};
Blockly.utils.object.inherits(FieldLabelContext, Blockly.FieldLabel);
FieldLabelContext.fromJson = function(options) {
    const text = Blockly.utils.parsing.replaceMessageReferences(options['text']);
    // `this` might be a subclass of FieldLabelContext if that class doesn't
    // override the static fromJson method.
    return new this(text, undefined, options);
};
FieldLabelContext.prototype.EDITABLE = false;
FieldLabelContext.prototype.SERIALIZABLE = true;
FieldLabelContext.prototype.initView = function() {};
FieldLabelContext.prototype.isVisible = function() {return false};
FieldLabelContext.prototype.isDirty_ = false;
Blockly.fieldRegistry.register('field_label_context', FieldLabelContext);