import { convertId, addWarning, removeWarning, getEventValue, isEvent, isRestrictedEvent } from "../utils.js";
import { BLOCK_EXTRA } from "../main.js";

const getOtherParameters = (block) => {
    var parameter_flydown = Blockly.registry.getClass("FIELD", "field_event_parameter_flydown");
    var var_names = [];
    if (isEvent(block)) {
        // If block is an listener, return the available parameters from extras.
        const event_value = getEventValue(block) == "-" ? Object.keys(BLOCK_EXTRA["EVENTS"])[0] : getEventValue(block);
        for (const opt of BLOCK_EXTRA["EVENTS"][event_value]) {
            var_names.push([Blockly.utils.parsing.replaceMessageReferences(opt[0]), opt[1]]);
        }
    } else {
        // If block is not an listener, get the other lexical field parameter names.
        for (const input of block.inputList) {
            for (const field of input.fieldRow) {
                if (field instanceof parameter_flydown) {
                    var_names.push([field.name, field.name]);
                }
            }
        }
    }
    return var_names;
}

/*
    Builds a new getter/setter block name for event parameters.
    It also deletes the previous block with same name.
*/
const getParameterBlockType = (sourceBlock, isSetter = true) => {
    return `EVENT_PARAMETER_${isSetter ? "SET" : "GET"}_${convertId(sourceBlock.id)}`;
}

/*
    Creates a new getter/setter block and returns the ID
    of the created block.
*/
const createParameterBlock = (helpUrl, sourceBlock, isSetter = true) => {
    const blockName = getParameterBlockType(sourceBlock, isSetter);
    delete Blockly.Blocks[blockName];
    Blockly.Blocks[blockName] = {
        init: function() {
            // Setter block
            if (isSetter) {
                this.appendValueInput('value')
                .appendField('set')
                .appendField(new Blockly.FieldDropdown(() => getOtherParameters(sourceBlock)), 'parameter')
                .appendField('to');
                this.setNextStatement(true);
                this.setPreviousStatement(true);
            // Getter block
            } else {
                this.appendDummyInput()
                .appendField('get')
                .appendField(new Blockly.FieldDropdown(() => getOtherParameters(sourceBlock)), 'parameter');
                this.setOutput(true);
            }
            this.setTooltip(`Parameter setter/getter`);
            helpUrl && this.setHelpUrl(helpUrl);
            this.setStyle('variable_blocks');
            this.setOnChange(function(changeEvent) {
                // TODO: Check if current block added as value to source block.
                if (this.getRootBlock() == sourceBlock) {
                    removeWarning(this, Blockly.Msg["WARNING_INVALID_SETTER_GETTER"], false);
                } else {
                    addWarning(this, Blockly.Msg["WARNING_INVALID_SETTER_GETTER"], false);
                }
            });
        }
    }
}

export function registerParameter() {
    const FieldParameterFlydown = Blockly.registry.getClass("FIELD", "field_parameter_flydown");
    class FieldEventParameterFlydown extends FieldParameterFlydown {
        constructor(paramName, isEditable, disableSetter, disableGetter) {
            super(paramName, isEditable);
            this.paramName = paramName;
            this.disableGetter = !!disableGetter;
            this.disableSetter = !!disableSetter;
        }

        flydownBlocksXML_() {
            // Create new setter/getter blocks.
            var xml = "";
            if (!this.disableGetter)
                xml += `<block type="${getParameterBlockType(this.sourceBlock_, false)}"><field name="parameter">${this.paramName}</field></block>`;
            if (!this.disableSetter)
                xml += `<block type="${getParameterBlockType(this.sourceBlock_, true)}"><field name="parameter">${this.paramName}</field></block>`;
            return "<xml>" + xml + "</xml>";
        }
    }
    FieldEventParameterFlydown.fromJson = function(options) {
        const name = Blockly.utils.parsing.replaceMessageReferences(options['name']);
        return new FieldEventParameterFlydown(
            name, options['is_editable'], options['disable_setter'], options['disable_getter']
        );
    };
    Blockly.fieldRegistry.register('field_event_parameter_flydown', FieldEventParameterFlydown);
}


Blockly.Extensions.register(
    'build_setter_getter',
    function() {
        var block = this;
        createParameterBlock(null, block, false);
        createParameterBlock(null, block);
    });


Blockly.Extensions.register(
    'prefill_event_dropdown',
    function() {
        var block = this;
        block.getField("event").menuGenerator_ = () => {
            var x = [];
            for (const opt in BLOCK_EXTRA["EVENTS"]) {
                if (!isRestrictedEvent(opt))
                    x.push([Blockly.utils.parsing.replaceMessageReferences(`%{BKY_VALUE_EVENT_${opt}}`), opt]);
            }
            return x;
        };
        block.getField("event").setValue(Object.keys(BLOCK_EXTRA["EVENTS"])[0]);
    }
)