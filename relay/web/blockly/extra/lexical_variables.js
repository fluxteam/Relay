// Source:
// https://cdn.skypack.dev/-/@mit-app-inventor/blockly-block-lexical-variables@v0.0.10-VYCWdaHPnk4Edn9akP76/dist=es2019,mode=imports/optimized/@mit-app-inventor/blockly-block-lexical-variables.js
// Don't load bundled Blockly, as we already loading Blockly ourselves.
// import __commonjs_module0 from "/-/blockly@v7.20211209.2-cqC9gVTrPDtr4BuUdg6E/dist=es2019,mode=imports/optimized/blockly.js";
const __commonjs_module0 = Blockly;
const {Css} = __commonjs_module0;
const {Msg} = __commonjs_module0;
const {utils} = __commonjs_module0;
const {FieldDropdown} = __commonjs_module0;
const {getMainWorkspace} = __commonjs_module0;
const {fieldRegistry} = __commonjs_module0;
const {Substitution} = __commonjs_module0;
const {NameSet} = __commonjs_module0;
const {Variables} = __commonjs_module0;
const {Drawer} = __commonjs_module0;
const {WorkspaceSvg} = __commonjs_module0;
const {FieldTextInput} = __commonjs_module0;
const {bindEvent_} = __commonjs_module0;
const {Xml} = __commonjs_module0;
const {svgResize} = __commonjs_module0;
const {VerticalFlyout} = __commonjs_module0;
const {Flyout} = __commonjs_module0;
const {ComponentManager} = __commonjs_module0;
const {Events} = __commonjs_module0;
const {Blocks} = __commonjs_module0;
const {Names} = __commonjs_module0;
const {unprefixName: unprefixName$1} = __commonjs_module0;
const {ALIGN_RIGHT} = __commonjs_module0;
const {Mutator} = __commonjs_module0;
const {BlockSvg} = __commonjs_module0;
const {Field} = __commonjs_module0;
const {Procedures} = __commonjs_module0;
const {JavaScript} = __commonjs_module0;
const {VARIABLE_CATEGORY_NAME} = __commonjs_module0;
const {isNumber} = __commonjs_module0;
const {PROCEDURE_CATEGORY_NAME} = __commonjs_module0;
const {Options} = __commonjs_module0;
;
const EXTRA_CSS = [
  ".blocklyFieldParameter>rect {",
  "  fill: rgb(222, 143, 108);",
  "  fill-opacity: 1.0;",
  "  stroke-width: 2;",
  "  stroke: rgb(231, 175, 150);",
  "}",
  ".blocklyFieldParameter>text {",
  "  stroke-width: 1;",
  "  fill: #000;",
  "}",
  ".blocklyFieldParameter:hover>rect {",
  "  stroke-width: 2;",
  "  stroke: rgb(231,175,150);",
  "  fill: rgb(231,175,150);",
  "  fill-opacity: 1.0;",
  "}",
  "/*",
  " * [lyn, 10/08/13] Control flydown with the getter/setter blocks.",
  " */",
  ".blocklyFieldParameterFlydown {",
  "  fill: rgb(231,175,150);",
  "  fill-opacity: 0.8;",
  "}",
  "/*",
  " * [lyn, 10/08/13] Control parameter fields with flydown procedure",
  " * caller block.",
  " */",
  ".blocklyFieldProcedure>rect {",
  "  fill: rgb(215,203,218);",
  "  fill-opacity: 1.0;",
  "  stroke-width: 0;",
  "  stroke: #000;",
  "}",
  ".blocklyFieldProcedure>text {",
  "  fill: #000;",
  "}",
  ".blocklyFieldProcedure:hover>rect {",
  "  stroke-width: 2;",
  "  stroke: #fff;",
  "  fill: rgb(215,203,218);",
  "  fill-opacity: 1.0;",
  "}",
  "/*",
  " * [lyn, 10/08/13] Control flydown with the procedure caller block.",
  " */",
  ".blocklyFieldProcedureFlydown {",
  "  fill: rgb(215,203,218);",
  "  fill-opacity: 0.8;",
  "}"
];
function registerCss() {
  Css.register(EXTRA_CSS);
}
/**
 * @license
 * Copyright 2021 Mark Friedman
 * SPDX-License-Identifier: Apache-2.0
 */
Msg["LANG_VARIABLES_GLOBAL_DECLARATION_TITLE_INIT"] = "initialize global";
Msg["LANG_VARIABLES_GLOBAL_DECLARATION_NAME"] = "name";
Msg["LANG_VARIABLES_GLOBAL_DECLARATION_TO"] = "to";
Msg["LANG_VARIABLES_GLOBAL_DECLARATION_COLLAPSED_TEXT"] = "global";
Msg["LANG_VARIABLES_GLOBAL_DECLARATION_TOOLTIP"] = "Creates a global variable and gives it the value of the attached blocks.";
Msg["LANG_VARIABLES_GLOBAL_PREFIX"] = "global";
Msg["LANG_VARIABLES_GET_TITLE_GET"] = "get";
Msg["LANG_VARIABLES_GET_COLLAPSED_TEXT"] = "get";
Msg["LANG_VARIABLES_GET_TOOLTIP"] = "Returns the value of this variable.";
Msg["LANG_VARIABLES_SET_TITLE_SET"] = "set";
Msg["LANG_VARIABLES_SET_TITLE_TO"] = "to";
Msg["LANG_VARIABLES_SET_COLLAPSED_TEXT"] = "set";
Msg["LANG_VARIABLES_SET_TOOLTIP"] = "Sets this variable to be equal to the input.";
Msg["LANG_VARIABLES_VARIABLE"] = " variable";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_TITLE_INIT"] = "initialize local";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_DEFAULT_NAME"] = "name";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_INPUT_TO"] = "to";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_IN_DO"] = "in";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_COLLAPSED_TEXT"] = "local";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_TOOLTIP"] = "Allows you to create variables that are only accessible in the do part of this block.";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_TRANSLATED_NAME"] = "initialize local in do";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_IN_RETURN"] = "in";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_COLLAPSED_TEXT"] = "local";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_TOOLTIP"] = "Allows you to create variables that are only accessible in the return part of this block.";
Msg["LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_TRANSLATED_NAME"] = "initialize local in return";
Msg["LANG_VARIABLES_LOCAL_MUTATOR_CONTAINER_TITLE_LOCAL_NAMES"] = "local names";
Msg["LANG_VARIABLES_LOCAL_MUTATOR_CONTAINER_TOOLTIP"] = "";
Msg["LANG_VARIABLES_LOCAL_MUTATOR_ARG_TITLE_NAME"] = "name";
Msg["LANG_VARIABLES_LOCAL_MUTATOR_ARG_DEFAULT_VARIABLE"] = "x";
Msg["LANG_PROCEDURES_DEFNORETURN_DEFINE"] = "to";
Msg["LANG_PROCEDURES_DEFNORETURN_PROCEDURE"] = "procedure";
Msg["LANG_PROCEDURES_DEFNORETURN_DO"] = "do";
Msg["LANG_PROCEDURES_DEFNORETURN_COLLAPSED_PREFIX"] = "to ";
Msg["LANG_PROCEDURES_DEFNORETURN_TOOLTIP"] = "A procedure that does not return a value.";
Msg["LANG_PROCEDURES_DOTHENRETURN_THEN_RETURN"] = "result";
Msg["LANG_PROCEDURES_DOTHENRETURN_DO"] = "do";
Msg["LANG_PROCEDURES_DOTHENRETURN_RETURN"] = "result";
Msg["LANG_PROCEDURES_DOTHENRETURN_TOOLTIP"] = "Runs the blocks in 'do' and returns a statement. Useful if you need to run a procedure before returning a value to a variable.";
Msg["LANG_PROCEDURES_DOTHENRETURN_COLLAPSED_TEXT"] = "do/result";
Msg["LANG_PROCEDURES_DEFRETURN_DEFINE"] = "to";
Msg["LANG_PROCEDURES_DEFRETURN_PROCEDURE"] = "procedure";
Msg["LANG_PROCEDURES_DEFRETURN_RETURN"] = "result";
Msg["LANG_PROCEDURES_DEFRETURN_COLLAPSED_PREFIX"] = "to ";
Msg["LANG_PROCEDURES_DEFRETURN_TOOLTIP"] = "A procedure returning a result value.";
Msg["LANG_PROCEDURES_DEF_DUPLICATE_WARNING"] = "Warning:\nThis procedure has\nduplicate inputs.";
Msg["LANG_PROCEDURES_CALLNORETURN_CALL"] = "call ";
Msg["LANG_PROCEDURES_CALLNORETURN_PROCEDURE"] = "procedure";
Msg["LANG_PROCEDURES_CALLNORETURN_COLLAPSED_PREFIX"] = "call ";
Msg["LANG_PROCEDURES_CALLNORETURN_TOOLTIP"] = "Call a procedure with no return value.";
Msg["LANG_PROCEDURES_CALLNORETURN_TRANSLATED_NAME"] = "call no return";
Msg["LANG_PROCEDURES_CALLRETURN_COLLAPSED_PREFIX"] = "call ";
Msg["LANG_PROCEDURES_CALLRETURN_TOOLTIP"] = "Call a procedure with a return value.";
Msg["LANG_PROCEDURES_CALLRETURN_TRANSLATED_NAME"] = "call return";
Msg["LANG_PROCEDURES_MUTATORCONTAINER_TITLE"] = "inputs";
Msg["LANG_PROCEDURES_MUTATORARG_TITLE"] = "input:";
Msg["LANG_PROCEDURES_HIGHLIGHT_DEF"] = "Highlight Procedure";
Msg["LANG_PROCEDURES_MUTATORCONTAINER_TOOLTIP"] = "";
Msg["LANG_PROCEDURES_MUTATORARG_TOOLTIP"] = "";
Msg["LANG_CONTROLS_FOR_INPUT_WITH"] = "count with";
Msg["LANG_CONTROLS_FOR_INPUT_VAR"] = "x";
Msg["LANG_CONTROLS_FOR_INPUT_FROM"] = "from";
Msg["LANG_CONTROLS_FOR_INPUT_TO"] = "to";
Msg["LANG_CONTROLS_FOR_INPUT_DO"] = "do";
Msg["LANG_CONTROLS_FOR_TOOLTIP"] = "Count from a start number to an end number.\nFor each count, set the current count number to\nvariable '%1', and then do some statements.";
Msg["LANG_CONTROLS_FORRANGE_INPUT_ITEM"] = "for each";
Msg["LANG_CONTROLS_FORRANGE_INPUT_VAR"] = "number";
Msg["LANG_CONTROLS_FORRANGE_INPUT_START"] = "from";
Msg["LANG_CONTROLS_FORRANGE_INPUT_END"] = "to";
Msg["LANG_CONTROLS_FORRANGE_INPUT_STEP"] = "by";
Msg["LANG_CONTROLS_FORRANGE_INPUT_DO"] = "do";
Msg["LANG_CONTROLS_FORRANGE_INPUT_COLLAPSED_TEXT"] = "for number in range";
Msg["LANG_CONTROLS_FORRANGE_INPUT_COLLAPSED_PREFIX"] = "for";
Msg["LANG_CONTROLS_FORRANGE_INPUT_COLLAPSED_SUFFIX"] = " in range";
Msg["LANG_CONTROLS_FORRANGE_TOOLTIP"] = "Runs the blocks in the 'do' section for each numeric value in the range from start to end, stepping the value each time.  Use the given variable name to refer to the current value.";
Msg["LANG_CONTROLS_FOREACH_INPUT_ITEM"] = "for each";
Msg["LANG_CONTROLS_FOREACH_INPUT_VAR"] = "item";
Msg["LANG_CONTROLS_FOREACH_INPUT_INLIST"] = "in list";
Msg["LANG_CONTROLS_FOREACH_INPUT_DO"] = "do";
Msg["LANG_CONTROLS_FOREACH_INPUT_COLLAPSED_TEXT"] = "for item in list";
Msg["LANG_CONTROLS_FOREACH_INPUT_COLLAPSED_PREFIX"] = "for ";
Msg["LANG_CONTROLS_FOREACH_INPUT_COLLAPSED_SUFFIX"] = " in list";
Msg["LANG_CONTROLS_FOREACH_TOOLTIP"] = "Runs the blocks in the 'do'  section for each item in the list.  Use the given variable name to refer to the current list item.";
Msg["LANG_CONTROLS_FOREACH_DICT_INPUT"] = "for each %1 with %2 in dictionary %3";
Msg["LANG_CONTROLS_FOREACH_DICT_INPUT_DO"] = "do";
Msg["LANG_CONTROLS_FOREACH_DICT_INPUT_KEY"] = "key";
Msg["LANG_CONTROLS_FOREACH_DICT_INPUT_VALUE"] = "value";
Msg["LANG_CONTROLS_FOREACH_DICT_TITLE"] = "for each in dictionary";
Msg["LANG_CONTROLS_FOREACH_DICT_TOOLTIP"] = "Runs the blocks in the 'do' section for each key-value entry in the dictionary. Use the given variable names to refer to the key/value of the current dictionary item.";
Msg["ERROR_SELECT_VALID_ITEM_FROM_DROPDOWN"] = "Select a valid item in the drop down.";
Msg["ERROR_BLOCK_CANNOT_BE_IN_DEFINITION"] = "This block cannot be in a definition";
Msg["HORIZONTAL_PARAMETERS"] = "Arrange Parameters Horizontally";
Msg["VERTICAL_PARAMETERS"] = "Arrange Parameters Vertically";
Msg["LANG_CONTROLS_DO_THEN_RETURN_INPUT_DO"] = "do";
Msg["LANG_CONTROLS_DO_THEN_RETURN_INPUT_RETURN"] = "result";
Msg["LANG_CONTROLS_DO_THEN_RETURN_TOOLTIP"] = "Runs the blocks in 'do' and returns a statement. Useful if you need to run a procedure before returning a value to a variable.";
Msg["LANG_CONTROLS_DO_THEN_RETURN_COLLAPSED_TEXT"] = "do/result";
Msg["LANG_CONTROLS_DO_THEN_RETURN_TITLE"] = "do result";
const InstantInTime = function(myConn, otherConn) {
  if (!myConn.sourceBlock_.rendered || !otherConn.sourceBlock_.rendered) {
    if (otherConn.check_ && !otherConn.check_.includes("InstantInTime")) {
      otherConn.sourceBlock_.badBlock();
    }
    return true;
  }
  return !otherConn.check_ || otherConn.check_.includes("InstantInTime");
};
const YailTypeToBlocklyTypeMap = {
  number: {
    input: ["Number"],
    output: ["Number", "String", "Key"]
  },
  text: {
    input: ["String"],
    output: ["Number", "String", "Key"]
  },
  boolean: {
    input: ["Boolean"],
    output: ["Boolean", "String"]
  },
  list: {
    input: ["Array"],
    output: ["Array", "String"]
  },
  component: {
    input: ["COMPONENT"],
    output: ["COMPONENT", "Key"]
  },
  InstantInTime: {
    input: ["InstantInTime", InstantInTime],
    output: ["InstantInTime", InstantInTime]
  },
  any: {
    input: null,
    output: null
  },
  dictionary: {
    input: ["Dictionary"],
    output: ["Dictionary", "String", "Array"]
  },
  pair: {
    input: ["Pair"],
    output: ["Pair", "String", "Array"]
  },
  key: {
    input: ["Key"],
    output: ["String", "Key"]
  }
};
const INPUT = "input";
const yailTypeToBlocklyType = function(yail, inputOrOutput) {
  const type = YailTypeToBlocklyTypeMap[yail][inputOrOutput];
  if (type === void 0) {
    throw new Error("Unknown Yail type: " + yail + " -- YailTypeToBlocklyType");
  }
  return type;
};
const getChildren = function(element) {
  if (element.children !== void 0) {
    return element.children;
  }
  return Array.prototype.filter.call(element.childNodes, function(node) {
    return node.nodeType == utils.dom.NodeType.ELEMENT_NODE;
  });
};
const checkErrors = function(block) {
  if (!block.getSvgRoot() || block.readOnly) {
    if (block.hasWarning) {
      block.hasWarning = false;
    }
    if (block.hasError) {
      block.hasError = false;
    }
    return;
  }
  if (!block.errors) {
    block.errors = [];
  }
  if (!block.warnings) {
    block.warnings = [];
  }
  const errorTestArray = block.errors;
  const warningTestArray = block.warnings;
  for (let i = 0; i < errorTestArray.length; i++) {
    if (errorTestArray[i].func && errorTestArray[i].func.call(this, block, errorTestArray[i])) {
      if (!block.hasError) {
        block.hasError = true;
      }
      if (block.hasWarning) {
        block.hasWarning = false;
      }
      return;
    }
  }
  if (block.hasError) {
    block.hasError = false;
  }
  for (let i = 0; i < warningTestArray.length; i++) {
    if (warningTestArray[i].func && warningTestArray[i].func.call(this, block, warningTestArray[i])) {
      if (!block.hasWarning) {
        block.hasWarning = true;
      }
      return;
    }
  }
  if (block.warning) {
    block.setWarningText(null);
  }
  if (block.hasWarning) {
    block.hasWarning = false;
  }
};
const checkIsInDefinition = function(block) {
  const rootBlock = block.getRootBlock();
  if (rootBlock.type === "global_declaration") {
    const errorMessage = Msg.ERROR_BLOCK_CANNOT_BE_IN_DEFINITION;
    block.setWarningText(errorMessage);
    return true;
  } else {
    return false;
  }
};
const checkDropDownContainsValidValue = function(block, params) {
  if (block.workspace.isDragging()) {
    return false;
  }
  for (let i = 0; i < params.dropDowns.length; i++) {
    const dropDown = block.getField(params.dropDowns[i]);
    const dropDownList = dropDown.menuGenerator_();
    const text = dropDown.getText();
    const value = dropDown.getValue();
    let textInDropDown = false;
    if (dropDown.updateMutation) {
      dropDown.updateMutation();
    }
    for (let k = 0; k < dropDownList.length; k++) {
      if (dropDownList[k][1] === value && value !== " ") {
        textInDropDown = true;
        if (dropDownList[k][0] !== text) {
          dropDown.setValue(dropDownList[k][0]);
        }
        break;
      }
    }
    if (!textInDropDown) {
      const errorMessage = Msg.ERROR_SELECT_VALID_ITEM_FROM_DROPDOWN;
      block.setWarningText(errorMessage);
      return true;
    }
  }
  return false;
};
var WarningHandler = /* @__PURE__ */ Object.freeze({
  __proto__: null,
  checkErrors,
  checkIsInDefinition,
  checkDropDownContainsValidValue
});
const usePrefixInCode = false;
const GLOBAL_KEYWORD = "global";
const procedureParameterPrefix = "input";
const localNamePrefix = "local";
const loopParameterPrefix = "item";
const loopRangeParameterPrefix = "counter";
const menuSeparator = " ";
const possiblyPrefixMenuNameWith = function(prefix) {
  return function(name) {
    return "" + name;
  };
};
const prefixGlobalMenuName = function(name) {
  return Msg.LANG_VARIABLES_GLOBAL_PREFIX + menuSeparator + name;
};
const unprefixName = function(name) {
  if (name.indexOf(Msg.LANG_VARIABLES_GLOBAL_PREFIX + menuSeparator) === 0) {
    return [
      Msg.LANG_VARIABLES_GLOBAL_PREFIX,
      name.substring(Msg.LANG_VARIABLES_GLOBAL_PREFIX.length + menuSeparator.length)
    ];
  } else if (name.indexOf(GLOBAL_KEYWORD + menuSeparator) === 0) {
    return [GLOBAL_KEYWORD, name.substring(6 + menuSeparator.length)];
  } else {
    return ["", name];
  }
};
const possiblyPrefixGeneratedVarName = function(prefix) {
  return function(name) {
    return "" + name;
  };
};
const FieldLexicalVariable = function(varname) {
  FieldDropdown.call(this, FieldLexicalVariable.dropdownCreate, FieldLexicalVariable.dropdownChange);
  if (varname) {
    this.doValueUpdate_(varname);
  } else {
    this.doValueUpdate_(Variables.generateUniqueName());
  }
};
utils.object.inherits(FieldLexicalVariable, FieldDropdown);
FieldLexicalVariable.prototype.setValue = function(text) {
  if (text && text !== " ") {
    const parts = text.split(" ");
    if (parts.length == 2 && parts[0] !== "global") {
      text = "global " + parts[1];
    }
  }
  FieldLexicalVariable.superClass_.setValue.call(this, text);
};
FieldLexicalVariable.prototype.doClassValidation_ = function(opt_newValue) {
  return opt_newValue;
};
FieldLexicalVariable.prototype.getBlock = function() {
  return this.block_;
};
FieldLexicalVariable.prototype.setBlock = function(block) {
  this.block_ = block;
};
FieldLexicalVariable.getGlobalNames = function(optExcludedBlock) {
  if (getMainWorkspace() && getMainWorkspace().getWarningHandler && getMainWorkspace().getWarningHandler().cacheGlobalNames) {
    return getMainWorkspace().getWarningHandler().cachedGlobalNames;
  }
  const globals = [];
  if (getMainWorkspace()) {
    let blocks = [];
    {
      blocks = getMainWorkspace().getTopBlocks();
    }
    for (let i = 0; i < blocks.length; i++) {
      const block = blocks[i];
      if (block.getGlobalNames && block != optExcludedBlock) {
        globals.push(...block.getGlobalNames());
      }
    }
  }
  return globals;
};
FieldLexicalVariable.prototype.getNamesInScope = function() {
  return FieldLexicalVariable.getNamesInScope(this.block_);
};
FieldLexicalVariable.getNamesInScope = function(block) {
  let globalNames = FieldLexicalVariable.getGlobalNames();
  globalNames = LexicalVariable.sortAndRemoveDuplicates(globalNames);
  globalNames = globalNames.map(function(name) {
    return [prefixGlobalMenuName(name), "global " + name];
  });
  const allLexicalNames = FieldLexicalVariable.getLexicalNamesInScope(block);
  return globalNames.concat(allLexicalNames);
};
FieldLexicalVariable.getLexicalNamesInScope = function(block) {
  let allLexicalNames = [];
  let parent;
  let child;
  function rememberName(name, list, prefix) {
    let fullName;
    {
      fullName = possiblyPrefixMenuNameWith()(name);
    }
    list.push(fullName);
  }
  child = block;
  if (child) {
    parent = child.getParent();
    if (parent) {
      while (parent) {
        if (parent.withLexicalVarsAndPrefix) {
          parent.withLexicalVarsAndPrefix(child, (lexVar, prefix) => {
            rememberName(lexVar, allLexicalNames);
          });
        }
        child = parent;
        parent = parent.getParent();
      }
    }
  }
  allLexicalNames = LexicalVariable.sortAndRemoveDuplicates(allLexicalNames);
  return allLexicalNames.map(function(name) {
    return [name, name];
  });
};
FieldLexicalVariable.dropdownCreate = function() {
  const variableList = this.getNamesInScope();
  return variableList.length == 0 ? [[" ", " "]] : variableList;
};
FieldLexicalVariable.prototype.doValueUpdate_ = function(newValue) {
  FieldDropdown.superClass_.doValueUpdate_.call(this, newValue);
  const options = this.getOptions(true, [[newValue, newValue]]);
  for (let i = 0, option; option = options[i]; i++) {
    if (option[1] == this.value_) {
      this.selectedOption_ = option;
    }
  }
  this.forceRerender();
};
FieldLexicalVariable.prototype.getOptions = function(opt_useCache, opt_extraOption) {
  if (Array.isArray(opt_useCache)) {
    opt_extraOption = opt_useCache;
  }
  const extraOption = opt_extraOption || [];
  if (this.isOptionListDynamic()) {
    if (!this.generatedOptions_ || !opt_useCache) {
      this.generatedOptions_ = this.menuGenerator_.call(this).concat(extraOption);
      validateOptions(this.generatedOptions_);
    }
    return this.generatedOptions_.concat(extraOption);
  }
  return this.menuGenerator_;
};
const validateOptions = function(options) {
  if (!Array.isArray(options)) {
    throw TypeError("FieldDropdown options must be an array.");
  }
  if (!options.length) {
    throw TypeError("FieldDropdown options must not be an empty array.");
  }
  let foundError = false;
  for (let i = 0; i < options.length; ++i) {
    const tuple = options[i];
    if (!Array.isArray(tuple)) {
      foundError = true;
      console.error("Invalid option[" + i + "]: Each FieldDropdown option must be an array. Found: ", tuple);
    } else if (typeof tuple[1] != "string") {
      foundError = true;
      console.error("Invalid option[" + i + "]: Each FieldDropdown option id must be a string. Found " + tuple[1] + " in: ", tuple);
    } else if (tuple[0] && typeof tuple[0] != "string" && typeof tuple[0].src != "string") {
      foundError = true;
      console.error("Invalid option[" + i + "]: Each FieldDropdown option must have a string label or image description. Found" + tuple[0] + " in: ", tuple);
    }
  }
  if (foundError) {
    throw TypeError("Found invalid FieldDropdown options.");
  }
};
FieldLexicalVariable.dropdownChange = function(text) {
  if (text) {
    this.doValueUpdate_(text);
    const topWorkspace = this.sourceBlock_.workspace.getTopWorkspace();
    if (topWorkspace.getWarningHandler) {
      topWorkspace.getWarningHandler().checkErrors(this.sourceBlock_);
    }
  }
};
FieldLexicalVariable.nameNotIn = function(name, nameList) {
  const namePrefixSuffix = FieldLexicalVariable.prefixSuffix(name);
  const namePrefix = namePrefixSuffix[0];
  const nameSuffix = namePrefixSuffix[1];
  let emptySuffixUsed = false;
  let isConflict = false;
  const suffixes = [];
  for (let i = 0; i < nameList.length; i++) {
    const prefixSuffix = FieldLexicalVariable.prefixSuffix(nameList[i]);
    const prefix = prefixSuffix[0];
    const suffix = prefixSuffix[1];
    if (prefix === namePrefix) {
      if (suffix === nameSuffix) {
        isConflict = true;
      }
      if (suffix === "") {
        emptySuffixUsed = true;
      } else {
        suffixes.push(suffix);
      }
    }
  }
  if (!isConflict) {
    return name;
  } else if (!emptySuffixUsed) {
    return namePrefix;
  } else {
    const suffixesAsNumbers = suffixes.map(function(elt, i, arr) {
      return parseInt(elt, 10);
    });
    suffixesAsNumbers.sort(function(a, b) {
      return a - b;
    });
    let smallest = 2;
    let index = 0;
    while (index < suffixesAsNumbers.length) {
      if (smallest < suffixesAsNumbers[index]) {
        return namePrefix + smallest;
      } else if (smallest == suffixesAsNumbers[index]) {
        smallest++;
        index++;
      } else {
        index++;
      }
    }
    return namePrefix + smallest;
  }
};
FieldLexicalVariable.prefixSuffix = function(name) {
  const matchResult = name.match(/^(.*?)(\d+)$/);
  if (matchResult) {
    return [matchResult[1], matchResult[2]];
  } else {
    return [name, ""];
  }
};
FieldLexicalVariable.fromJson = function(options) {
  const name = utils.replaceMessageReferences(options["name"]);
  return new FieldLexicalVariable(name);
};
fieldRegistry.register("field_lexical_variable", FieldLexicalVariable);
const LexicalVariable = {};
LexicalVariable.renameGlobal = function(newName) {
  const oldName = this.value_;
  newName = LexicalVariable.makeLegalIdentifier(newName);
  this.sourceBlock_.getField("NAME").doValueUpdate_(newName);
  const globals = FieldLexicalVariable.getGlobalNames(this.sourceBlock_);
  newName = FieldLexicalVariable.nameNotIn(newName, globals);
  if (this.sourceBlock_.rendered) {
    if (getMainWorkspace()) {
      const blocks = getMainWorkspace().getAllBlocks();
      for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i];
        const renamingFunction = block.renameLexicalVar;
        if (renamingFunction) {
          renamingFunction.call(block, GLOBAL_KEYWORD + menuSeparator + oldName, GLOBAL_KEYWORD + menuSeparator + newName, Msg.LANG_VARIABLES_GLOBAL_PREFIX + menuSeparator + oldName, Msg.LANG_VARIABLES_GLOBAL_PREFIX + menuSeparator + newName);
        }
      }
    }
  }
  return newName;
};
LexicalVariable.renameParam = function(newName) {
  const htmlInput = this.htmlInput_;
  const oldName = this.getValue() || htmlInput && htmlInput.defaultValue || this.getText();
  newName = LexicalVariable.makeLegalIdentifier(newName);
  return LexicalVariable.renameParamFromTo(this.sourceBlock_, oldName, newName, false);
};
LexicalVariable.renameParamFromTo = function(block, oldName, newName, renameCapturables) {
  if (block.mustNotRenameCapturables) {
    return LexicalVariable.renameParamWithoutRenamingCapturables(block, oldName, newName, []);
  } else if (renameCapturables) {
    LexicalVariable.renameParamRenamingCapturables(block, oldName, newName);
    return newName;
  } else {
    return LexicalVariable.renameParamWithoutRenamingCapturables(block, oldName, newName, []);
  }
};
LexicalVariable.renameParamRenamingCapturables = function(sourceBlock, oldName, newName) {
  if (newName !== oldName) {
    const namesDeclaredHere = sourceBlock.declaredNames ? sourceBlock.declaredNames() : [];
    if (namesDeclaredHere.indexOf(oldName) == -1) {
      throw Error("LexicalVariable.renamingCapturables: oldName " + oldName + " is not in declarations {" + namesDeclaredHere.join(",") + "}");
    }
    const namesDeclaredAbove = [];
    FieldLexicalVariable.getNamesInScope(sourceBlock).map(function(pair) {
      if (pair[0] == pair[1]) {
        namesDeclaredAbove.push(pair[0]);
      } else {
        namesDeclaredAbove.push(pair[0], pair[1]);
      }
    });
    const declaredNames = namesDeclaredHere.concat(namesDeclaredAbove);
    if (declaredNames.indexOf(newName) != -1) {
      throw Error("LexicalVariable.renameParamRenamingCapturables: newName " + newName + " is in existing declarations {" + declaredNames.join(",") + "}");
    } else {
      if (sourceBlock.renameBound) {
        const boundSubstitution = Substitution.simpleSubstitution(oldName, newName);
        const freeSubstitution = new Substitution();
        sourceBlock.renameBound(boundSubstitution, freeSubstitution);
      } else {
        throw Error("LexicalVariable.renameParamRenamingCapturables: block " + sourceBlock.type + " is not a declaration block.");
      }
    }
  }
};
LexicalVariable.renameFree = function(block, freeSubstitution) {
  if (block) {
    if (block.renameFree) {
      block.renameFree(freeSubstitution);
    } else {
      block.getChildren().map(function(blk) {
        LexicalVariable.renameFree(blk, freeSubstitution);
      });
    }
  }
};
LexicalVariable.freeVariables = function(block) {
  let result = [];
  if (!block) {
    result = new NameSet();
  } else if (block.freeVariables) {
    result = block.freeVariables();
  } else {
    const nameSets = block.getChildren().map(function(blk) {
      return LexicalVariable.freeVariables(blk);
    });
    result = NameSet.unionAll(nameSets);
  }
  return result;
};
LexicalVariable.renameParamWithoutRenamingCapturables = function(sourceBlock, oldName, newName, OKNewNames) {
  if (oldName === newName) {
    return oldName;
  }
  sourceBlock.declaredNames ? sourceBlock.declaredNames() : [];
  let sourcePrefix = "";
  const helperInfo = LexicalVariable.renameParamWithoutRenamingCapturablesInfo(sourceBlock, oldName, sourcePrefix);
  const blocksToRename = helperInfo[0];
  const capturables = helperInfo[1];
  let declaredNames = [];
  if (sourceBlock.declaredNames) {
    declaredNames = sourceBlock.declaredNames();
    const oldIndex = declaredNames.indexOf(oldName);
    if (oldIndex != -1) {
      declaredNames.splice(oldIndex, 1);
    }
    if (OKNewNames.indexOf(newName) != -1) {
      const newIndex = declaredNames.indexOf(newName);
      if (newIndex != -1) {
        declaredNames.splice(newIndex, 1);
      }
    }
  }
  const conflicts = LexicalVariable.sortAndRemoveDuplicates(capturables.concat(declaredNames));
  newName = FieldLexicalVariable.nameNotIn(newName, conflicts);
  if (!(newName === oldName)) {
    const oldNameValid = declaredNames.indexOf(oldName) != -1;
    if (!oldNameValid) {
      for (let i = 0; i < blocksToRename.length; i++) {
        const block = blocksToRename[i];
        const renamingFunction = block.renameLexicalVar;
        if (renamingFunction) {
          renamingFunction.call(block, possiblyPrefixMenuNameWith()(oldName), possiblyPrefixMenuNameWith()(newName));
        }
      }
    }
  }
  return newName;
};
LexicalVariable.renameParamWithoutRenamingCapturablesInfo = function(sourceBlock, oldName, sourcePrefix) {
  let inScopeBlocks = [];
  if (sourceBlock.blocksInScope) {
    inScopeBlocks = sourceBlock.blocksInScope();
  }
  const referenceResults = inScopeBlocks.map(function(blk) {
    return LexicalVariable.referenceResult(blk, oldName, sourcePrefix, []);
  });
  let blocksToRename = [];
  let capturables = [];
  for (let r = 0; r < referenceResults.length; r++) {
    blocksToRename = blocksToRename.concat(referenceResults[r][0]);
    capturables = capturables.concat(referenceResults[r][1]);
  }
  capturables = LexicalVariable.sortAndRemoveDuplicates(capturables);
  return [blocksToRename, capturables];
};
LexicalVariable.checkIdentifier = function(ident) {
  const transformed = ident.trim().replace(/[\s\xa0]+/g, "_");
  const legalStartCharRegExp = "^[^-0-9!&%^/>=<`'\"#:;,\\\\*+.()|{}[\\] ]";
  const legalRestCharsRegExp = `[^-!&%^/>=<'"#:;,\\\\*+.()|{}[\\] ]*$`;
  const legalRegexp = new RegExp(legalStartCharRegExp + legalRestCharsRegExp);
  const isLegal = transformed.search(legalRegexp) == 0;
  return {isLegal, transformed};
};
LexicalVariable.makeLegalIdentifier = function(ident) {
  const check = LexicalVariable.checkIdentifier(ident);
  if (check.isLegal) {
    return check.transformed;
  } else if (check.transformed === "") {
    return "_";
  } else {
    return "name";
  }
};
LexicalVariable.referenceResult = function(block, name, prefix, env) {
  if (!block) {
    return [[], []];
  }
  const referenceResults = block.referenceResults ? block.referenceResults(name, prefix, env) : block.getChildren().map(function(blk) {
    return LexicalVariable.referenceResult(blk, name, prefix, env);
  });
  let blocksToRename = [];
  let capturables = [];
  for (let r = 0; r < referenceResults.length; r++) {
    blocksToRename = blocksToRename.concat(referenceResults[r][0]);
    capturables = capturables.concat(referenceResults[r][1]);
  }
  return [blocksToRename, capturables];
};
LexicalVariable.sortAndRemoveDuplicates = function(strings) {
  const sorted = strings.sort();
  const nodups = [];
  if (strings.length >= 1) {
    let prev = sorted[0];
    nodups.push(prev);
    for (let i = 1; i < sorted.length; i++) {
      if (!(sorted[i] === prev)) {
        prev = sorted[i];
        nodups.push(prev);
      }
    }
  }
  return nodups;
};
LexicalVariable.getNextTargetBlock = function(block) {
  if (block && block.nextConnection && block.nextConnection.targetBlock()) {
    return block.nextConnection.targetBlock();
  } else {
    return null;
  }
};
LexicalVariable.stringListsEqual = function(strings1, strings2) {
  const len1 = strings1.length;
  const len2 = strings2.length;
  if (len1 !== len2) {
    return false;
  } else {
    for (let i = 0; i < len1; i++) {
      if (strings1[i] !== strings2[i]) {
        return false;
      }
    }
  }
  return true;
};
const procDefaultValue = ["", ""];
const onChange = function(procedureId) {
  let workspace = this.block.workspace.getTopWorkspace();
  if (!this.block.isEditable()) {
    workspace = Drawer.flyout_.workspace_;
    return;
  }
  const def = workspace.getProcedureDatabase().getProcedure(procedureId);
  if (!def)
    return;
  const text = def.getFieldValue("NAME");
  if (text == "" || text != this.getValue()) {
    for (let i = 0; this.block.getInput("ARG" + i) != null; i++) {
      this.block.removeInput("ARG" + i);
    }
  }
  this.doValueUpdate_(text);
  if (def) {
    this.block.setProcedureParameters(def.arguments_, def.paramIds_, true);
  }
};
const getProcedureNames = function(returnValue, opt_workspace) {
  const workspace = opt_workspace || getMainWorkspace();
  const topBlocks = workspace.getTopBlocks();
  const procNameArray = [procDefaultValue];
  for (let i = 0; i < topBlocks.length; i++) {
    const procName = topBlocks[i].getFieldValue("NAME");
    if (topBlocks[i].type == "procedures_defnoreturn" && !returnValue) {
      procNameArray.push([procName, procName]);
    } else if (topBlocks[i].type == "procedures_defreturn" && returnValue) {
      procNameArray.push([procName, procName]);
    }
  }
  if (procNameArray.length > 1) {
    procNameArray.splice(0, 1);
  }
  return procNameArray;
};
const getAllProcedureDeclarationBlocksExcept = function(block) {
  const topBlocks = block.workspace.getTopBlocks(false);
  const blockArray = [];
  for (let i = 0; i < topBlocks.length; i++) {
    if (topBlocks[i].type === "procedures_defnoreturn" || topBlocks[i].type === "procedures_defreturn") {
      if (topBlocks[i] !== block) {
        blockArray.push(topBlocks[i]);
      }
    }
  }
  return blockArray;
};
const removeProcedureValues = function(name, workspace) {
  if (workspace && workspace === getMainWorkspace()) {
    const blockArray = workspace.getAllBlocks();
    for (let i = 0; i < blockArray.length; i++) {
      const block = blockArray[i];
      if (block.type == "procedures_callreturn" || block.type == "procedures_callnoreturn") {
        if (block.getFieldValue("PROCNAME") == name) {
          block.removeProcedureValue();
        }
      }
    }
  }
};
const renameProcedure = function(newName) {
  const oldName = this.oldName_ || this.getValue();
  const originalNewName = newName;
  newName = LexicalVariable.makeLegalIdentifier(newName);
  const procBlocks = getAllProcedureDeclarationBlocksExcept(this.sourceBlock_);
  const procNames = procBlocks.map(function(decl) {
    return decl.getFieldValue("NAME");
  });
  newName = FieldLexicalVariable.nameNotIn(newName, procNames);
  if (newName !== originalNewName) {
    this.doValueUpdate_(newName);
  }
  const blocks = this.sourceBlock_.workspace.getAllBlocks();
  for (let x = 0; x < blocks.length; x++) {
    const func = blocks[x].renameProcedure;
    if (func) {
      func.call(blocks[x], oldName, newName);
    }
  }
  this.oldName_ = newName;
  return newName;
};
const ProcedureDatabase = function(workspace) {
  this.workspace_ = workspace;
  this.procedures_ = {};
  this.returnProcedures_ = {};
  this.voidProcedures_ = {};
  this.length = 0;
  this.returnProcedures = 0;
  this.voidProcedures = 0;
};
ProcedureDatabase.defaultValue = ["", "none"];
ProcedureDatabase.prototype.getNames = function(returnValue) {
  return getProcedureNames(returnValue, this.workspace_).map(function(v) {
    return v[0];
  });
};
ProcedureDatabase.prototype.getMenuItems = function(returnValue) {
  return getProcedureNames(returnValue, this.workspace_);
};
ProcedureDatabase.prototype.getDeclarationBlocks = function(returnValue) {
  return utils.object.values(returnValue ? this.returnProcedures_ : this.voidProcedures_);
};
ProcedureDatabase.prototype.getDeclarationsBlocksExcept = function(block) {
  const blockArray = [];
  utils.values(this.procedures_).forEach(function(b) {
    if (b !== block)
      blockArray.push(b);
  });
  return blockArray;
};
ProcedureDatabase.prototype.getAllDeclarationNames = function() {
  return utils.values(this.procedures_).map(function(block) {
    return block.getFieldValue("NAME");
  });
};
ProcedureDatabase.prototype.addProcedure = function(name, block) {
  if (block.type != "procedures_defnoreturn" && block.type != "procedures_defreturn") {
    console.warn("Attempt to addProcedure with block type " + block.type);
    return false;
  }
  const id = block.id;
  if (id in this.procedures_) {
    return false;
  }
  this.procedures_[id] = block;
  this.length++;
  if (block.type == "procedures_defnoreturn") {
    this.voidProcedures_[id] = block;
    this.voidProcedures++;
  } else {
    this.returnProcedures_[id] = block;
    this.returnProcedures++;
  }
  return true;
};
ProcedureDatabase.prototype.removeProcedure = function(id) {
  if (id in this.procedures_) {
    const block = this.procedures_[id];
    if (block.type == "procedures_defnoreturn") {
      delete this.voidProcedures_[id];
      this.voidProcedures--;
    } else {
      delete this.returnProcedures_[id];
      this.returnProcedures--;
    }
    delete this.procedures_[id];
    this.length--;
  }
  return true;
};
ProcedureDatabase.prototype.renameProcedure = function(procId, oldName, newName) {
};
ProcedureDatabase.prototype.getProcedure = function(id) {
  const proc = this.procedures_[id];
  return proc ? proc : this.getProcedureByName(id);
};
ProcedureDatabase.prototype.getProcedureByName = function(name) {
  for (const id in this.procedures_) {
    if (this.procedures_[id].getFieldValue("NAME") === name) {
      return this.procedures_[id];
    }
  }
  return void 0;
};
ProcedureDatabase.prototype.clear = function() {
  this.procedures_ = {};
  this.returnProcedures_ = {};
  this.voidProcedures_ = {};
  this.length = 0;
  this.returnProcedures = 0;
  this.voidProcedures = 0;
};
WorkspaceSvg.prototype.flydown_ = null;
WorkspaceSvg.prototype.getFlydown = function() {
  return this.flydown_;
};
WorkspaceSvg.prototype.getProcedureDatabase = function() {
  if (!this.procedureDb_) {
    this.procedureDb_ = new ProcedureDatabase(this);
  }
  return this.procedureDb_;
};
WorkspaceSvg.prototype.getTopWorkspace = function() {
  let parent = this;
  while (parent.targetWorkspace) {
    parent = parent.targetWorkspace;
  }
  return parent;
};
WorkspaceSvg.prototype.getWarningHandler = function() {
  return WarningHandler;
};
const FieldFlydown = function(name, isEditable, opt_displayLocation, opt_changeHandler) {
  this.EDITABLE = isEditable;
  this.displayLocation = opt_displayLocation || FieldFlydown.DISPLAY_RIGHT;
  FieldFlydown.superClass_.constructor.call(this, name, opt_changeHandler);
};
utils.object.inherits(FieldFlydown, FieldTextInput);
FieldFlydown.timeout = 500;
FieldFlydown.showPid_ = 0;
FieldFlydown.openFieldFlydown_ = null;
FieldFlydown.DISPLAY_BELOW = "BELOW";
FieldFlydown.DISPLAY_RIGHT = "RIGHT";
FieldFlydown.DISPLAY_LOCATION = FieldFlydown.DISPLAY_BELOW;
FieldFlydown.prototype.fieldCSSClassName = "blocklyFieldFlydownField";
FieldFlydown.prototype.flyoutCSSClassName = "blocklyFieldFlydownFlydown";
FieldFlydown.prototype.showEditor_ = function() {
  if (!this.EDITABLE) {
    return;
  }
  if (FieldFlydown.showPid_) {
    clearTimeout(FieldFlydown.showPid_);
    FieldFlydown.showPid_ = 0;
    getMainWorkspace().hideChaff();
  }
  FieldFlydown.superClass_.showEditor_.call(this);
};
FieldFlydown.prototype.init = function(block) {
  FieldFlydown.superClass_.init.call(this, block);
  utils.dom.removeClass(this.fieldGroup_, "blocklyEditableText");
  utils.dom.removeClass(this.fieldGroup_, "blocklyNoNEditableText");
  utils.dom.addClass(this.fieldGroup_, this.fieldCSSClassName);
  this.mouseOverWrapper_ = bindEvent_(this.fieldGroup_, "mouseover", this, this.onMouseOver_);
  this.mouseOutWrapper_ = bindEvent_(this.fieldGroup_, "mouseout", this, this.onMouseOut_);
};
FieldFlydown.prototype.onMouseOver_ = function(e) {
  if (!this.sourceBlock_.isInFlyout && FieldFlydown.showPid_ == 0) {
    FieldFlydown.showPid_ = window.setTimeout(this.showFlydownMaker_(), FieldFlydown.timeout);
  }
  e.stopPropagation();
};
FieldFlydown.prototype.onMouseOut_ = function(e) {
  window.clearTimeout(FieldFlydown.showPid_);
  FieldFlydown.showPid_ = 0;
  e.stopPropagation();
};
FieldFlydown.prototype.showFlydownMaker_ = function() {
  const field = this;
  return function() {
    if (FieldFlydown.showPid_ !== 0 && !field.getSourceBlock().workspace.isDragging() && !this.htmlInput_) {
      try {
        field.showFlydown_();
      } catch (e) {
        console.error("Failed to show flydown", e);
      }
    }
    FieldFlydown.showPid_ = 0;
  };
};
FieldFlydown.prototype.showFlydown_ = function() {
  getMainWorkspace().hideChaff();
  const flydown = getMainWorkspace().getFlydown();
  getMainWorkspace().getParentSvg().appendChild(flydown.svgGroup_);
  const scale = flydown.targetWorkspace.scale;
  flydown.workspace_.setScale(scale);
  flydown.setCSSClass(this.flyoutCSSClassName);
  const blocksXMLText = this.flydownBlocksXML_();
  const blocksDom = Xml.textToDom(blocksXMLText);
  const blocksXMLList = getChildren(blocksDom);
  const xy = getMainWorkspace().getSvgXY(this.borderRect_);
  const borderBBox = this.borderRect_.getBBox();
  if (this.displayLocation === FieldFlydown.DISPLAY_BELOW) {
    xy.y += borderBBox.height * scale;
  } else {
    xy.x += borderBBox.width * scale;
  }
  flydown.field_ = this;
  flydown.showAt(blocksXMLList, xy.x, xy.y);
  FieldFlydown.openFieldFlydown_ = this;
};
FieldFlydown.hide = function() {
  window.clearTimeout(FieldFlydown.showPid_);
  const flydown = getMainWorkspace().getFlydown();
  if (flydown) {
    flydown.hide();
  }
};
function callAllValidators(field, text) {
  const classResult = field.doClassValidation_(text);
  if (classResult === null) {
    return null;
  } else if (classResult !== void 0) {
    text = classResult;
  }
  const userValidator = field.getValidator();
  if (userValidator) {
    const userResult = userValidator.call(field, text);
    if (userResult === null) {
      return null;
    } else if (userResult !== void 0) {
      text = userResult;
    }
  }
  return text;
}
FieldFlydown.prototype.onHtmlInputChange_ = function(e) {
  const htmlInput = this.htmlInput_;
  const text = htmlInput.value;
  if (text !== htmlInput.oldValue_) {
    htmlInput.oldValue_ = text;
    let valid = true;
    if (this.sourceBlock_) {
      valid = callAllValidators(this, htmlInput.value);
    }
    if (valid === null) {
      utils.dom.addClass(htmlInput, "blocklyInvalidInput");
    } else {
      utils.dom.removeClass(htmlInput, "blocklyInvalidInput");
      this.doValueUpdate_(valid);
    }
  } else if (utils.userAgent.WEBKIT) {
    this.sourceBlock_.render();
  }
  this.textContent_.nodeValue = text;
  this.forceRerender();
  this.resizeEditor_();
  svgResize(this.sourceBlock_.workspace);
};
FieldFlydown.prototype.dispose = function() {
  if (FieldFlydown.openFieldFlydown_ == this) {
    FieldFlydown.hide();
  }
  FieldTextInput.prototype.dispose.call(this);
};
FieldFlydown.fromJson = function(options) {
  const name = utils.replaceMessageReferences(options["name"]);
  return new FieldFlydown(name, options["is_editable"]);
};
fieldRegistry.register("field_flydown", FieldFlydown);
const Flydown = function(workspaceOptions) {
  Flydown.superClass_.constructor.call(this, workspaceOptions);
  this.dragAngleRange_ = 360;
};
utils.object.inherits(Flydown, VerticalFlyout);
Flydown.prototype.previousCSSClassName_ = "";
Flydown.prototype.VERTICAL_SEPARATION_FACTOR = 1;
Flydown.prototype.createDom = function(cssClassName) {
  this.previousCSSClassName_ = cssClassName;
  this.svgGroup_ = utils.dom.createSvgElement("g", {class: cssClassName}, null);
  this.svgBackground_ = utils.dom.createSvgElement("path", {}, this.svgGroup_);
  this.svgGroup_.appendChild(this.workspace_.createDom());
  return this.svgGroup_;
};
Flydown.prototype.setCSSClass = function(newCSSClassName) {
  if (newCSSClassName !== this.previousCSSClassName_) {
    utils.dom.removeClass(this.svgGroup_, this.previousCSSClassName_);
    utils.dom.addClass(this.svgGroup_, newCSSClassName);
    this.previousCSSClassName_ = newCSSClassName;
  }
};
Flydown.prototype.init = function(workspace) {
  Flyout.prototype.init.call(this, workspace, false);
  workspace.getComponentManager().addCapability(this.id, ComponentManager.Capability.AUTOHIDEABLE);
};
Flydown.prototype.position = function() {
  return;
};
Flydown.prototype.showAt = function(xmlList, x, y) {
  Events.disable();
  try {
    this.show(xmlList);
  } finally {
    Events.enable();
  }
  const margin = this.CORNER_RADIUS * this.workspace_.scale;
  const edgeWidth = this.width_ - 2 * margin;
  const edgeHeight = this.height_ - 2 * margin;
  const path = ["M 0," + margin];
  path.push("a", margin, margin, 0, 0, 1, margin, -margin);
  path.push("h", edgeWidth);
  path.push("a", margin, margin, 0, 0, 1, margin, margin);
  path.push("v", edgeHeight);
  path.push("a", margin, margin, 0, 0, 1, -margin, margin);
  path.push("h", -edgeWidth);
  path.push("a", margin, margin, 0, 0, 1, -margin, -margin);
  path.push("z");
  this.svgBackground_.setAttribute("d", path.join(" "));
  this.svgGroup_.setAttribute("transform", "translate(" + x + ", " + y + ")");
};
Flydown.prototype.reflow = function() {
  this.workspace_.scale = this.targetWorkspace.scale;
  const scale = this.workspace_.scale;
  let flydownWidth = 0;
  let flydownHeight = 0;
  const margin = this.CORNER_RADIUS * scale;
  const blocks = this.workspace_.getTopBlocks(false);
  for (let i = 0, block; block = blocks[i]; i++) {
    const blockHW = block.getHeightWidth();
    flydownWidth = Math.max(flydownWidth, blockHW.width * scale);
    flydownHeight += blockHW.height * scale;
  }
  flydownWidth += 2 * margin + this.tabWidth_ * scale;
  const rendererConstants = this.workspace_.getRenderer().getConstants();
  const startHatHeight = rendererConstants.ADD_START_HATS ? rendererConstants.START_HAT_HEIGHT : 0;
  flydownHeight += 3 * margin + margin * this.VERTICAL_SEPARATION_FACTOR * blocks.length + startHatHeight * scale / 2;
  if (this.width_ != flydownWidth) {
    for (let j = 0, block; block = blocks[j]; j++) {
      const blockHW = block.getHeightWidth();
      const blockXY = block.getRelativeToSurfaceXY();
      if (this.RTL) {
        const dx = flydownWidth - margin - scale * (this.tabWidth_ - blockXY.x);
        block.moveBy(dx, 0);
        blockXY.x += dx;
      }
      if (block.flyoutRect_) {
        block.flyoutRect_.setAttribute("width", blockHW.width);
        block.flyoutRect_.setAttribute("height", blockHW.height);
        block.flyoutRect_.setAttribute("x", this.RTL ? blockXY.x - blockHW.width : blockXY.x);
        block.flyoutRect_.setAttribute("y", blockXY.y);
      }
    }
    this.width_ = flydownWidth;
    this.height_ = flydownHeight;
  }
};
Flydown.prototype.onMouseMove_ = function(e) {
  return;
};
Flydown.prototype.placeNewBlock_ = function(originBlock) {
  const targetWorkspace = this.targetWorkspace;
  const svgRootOld = originBlock.getSvgRoot();
  if (!svgRootOld) {
    throw Error("originBlock is not rendered.");
  }
  let scale = this.workspace_.scale;
  const xyOld = this.workspace_.getSvgXY(svgRootOld);
  const scrollX = xyOld.x;
  xyOld.x += scrollX / targetWorkspace.scale - scrollX;
  const scrollY = xyOld.y;
  scale = targetWorkspace.scale;
  xyOld.y += scrollY / scale - scrollY;
  const xml = Xml.blockToDom(originBlock);
  const block = Xml.domToBlock(xml, targetWorkspace);
  const svgRootNew = block.getSvgRoot();
  if (!svgRootNew) {
    throw Error("block is not rendered.");
  }
  const xyNew = targetWorkspace.getSvgXY(svgRootNew);
  xyNew.x += targetWorkspace.scrollX / targetWorkspace.scale - targetWorkspace.scrollX;
  xyNew.y += targetWorkspace.scrollY / targetWorkspace.scale - targetWorkspace.scrollY;
  if (targetWorkspace.toolbox_ && !targetWorkspace.scrollbar) {
    xyNew.x += targetWorkspace.toolbox_.getWidth() / targetWorkspace.scale;
    xyNew.y += targetWorkspace.toolbox_.getHeight() / targetWorkspace.scale;
  }
  block.moveBy(xyOld.x - xyNew.x, xyOld.y - xyNew.y);
  return block;
};
Flydown.prototype.shouldHide = true;
Flydown.prototype.hide = function() {
  if (this.shouldHide) {
    Flyout.prototype.hide.call(this);
    FieldFlydown.openFieldFlydown_ = null;
  }
  this.shouldHide = true;
};
Flydown.prototype.autoHide = function() {
  this.hide();
};
const FieldGlobalFlydown = function(name, displayLocation) {
  FieldGlobalFlydown.superClass_.constructor.call(this, name, true, displayLocation, LexicalVariable.renameGlobal);
};
utils.object.inherits(FieldGlobalFlydown, FieldFlydown);
FieldGlobalFlydown.prototype.fieldCSSClassName = "blocklyFieldParameter";
FieldGlobalFlydown.prototype.flyoutCSSClassName = "blocklyFieldParameterFlydown";
FieldGlobalFlydown.prototype.flydownBlocksXML_ = function() {
  const name = Msg.LANG_VARIABLES_GLOBAL_PREFIX + " " + this.getText();
  const getterSetterXML = '<xml><block type="lexical_variable_get"><title name="VAR">' + name + '</title></block><block type="lexical_variable_set"><title name="VAR">' + name + "</title></block></xml>";
  return getterSetterXML;
};
FieldGlobalFlydown.fromJson = function(options) {
  const name = utils.replaceMessageReferences(options["name"]);
  return new FieldGlobalFlydown(name);
};
fieldRegistry.register("field_global_flydown", FieldGlobalFlydown);
const FieldNoCheckDropdown = function(...args) {
  FieldDropdown.apply(this, args);
};
utils.object.inherits(FieldNoCheckDropdown, FieldDropdown);
FieldNoCheckDropdown.prototype.doClassValidation_ = function(opt_newValue) {
  let isValueValid = false;
  const options = this.getOptions(true);
  for (let i = 0, option; option = options[i]; i++) {
    if (option[1] === opt_newValue) {
      isValueValid = true;
      break;
    }
  }
  if (!isValueValid) {
    this.generatedOptions_.push([opt_newValue, opt_newValue]);
  }
  return opt_newValue;
};
FieldNoCheckDropdown.fromJson = function(options) {
  return new FieldNoCheckDropdown(options["options"], void 0, options);
};
fieldRegistry.register("field_nocheck_dropdown", FieldNoCheckDropdown);
const FieldParameterFlydown = function(name, isEditable, opt_displayLocation, opt_additionalChangeHandler) {
  const changeHandler = function(text) {
    if (!FieldParameterFlydown.changeHandlerEnabled) {
      return text;
    }
    const possiblyRenamedText = LexicalVariable.renameParam.call(this, text);
    if (opt_additionalChangeHandler) {
      opt_additionalChangeHandler.call(this, possiblyRenamedText);
    }
    return possiblyRenamedText;
  };
  FieldParameterFlydown.superClass_.constructor.call(this, name, isEditable, opt_displayLocation, changeHandler);
};
utils.object.inherits(FieldParameterFlydown, FieldFlydown);
FieldParameterFlydown.prototype.fieldCSSClassName = "blocklyFieldParameter";
FieldParameterFlydown.prototype.flyoutCSSClassName = "blocklyFieldParameterFlydown";
FieldParameterFlydown.changeHandlerEnabled = true;
FieldParameterFlydown.withChangeHanderDisabled = function(thunk) {
  const oldFlag = FieldParameterFlydown.changeHandlerEnabled;
  FieldParameterFlydown.changeHandlerEnabled = false;
  try {
    thunk();
  } finally {
    FieldParameterFlydown.changeHandlerEnabled = oldFlag;
  }
};
FieldParameterFlydown.prototype.flydownBlocksXML_ = function() {
  const name = this.getText();
  const getterSetterXML = '<xml><block type="lexical_variable_get"><field name="VAR">' + name + '</field></block><block type="lexical_variable_set"><field name="VAR">' + name + "</field></block></xml>";
  return getterSetterXML;
};
FieldParameterFlydown.addHorizontalVerticalOption = function(block, options) {
  let numParams = 0;
  if (block.getParameters) {
    numParams = block.getParameters().length;
  }
  if (block.isCollapsed() || numParams <= 0) {
    return;
  }
  const horizVertOption = {
    enabled: true,
    text: block.horizontalParameters ? Msg.VERTICAL_PARAMETERS : Msg.HORIZONTAL_PARAMETERS,
    callback: function() {
      block.setParameterOrientation(!block.horizontalParameters);
    }
  };
  let insertionIndex = 0;
  for (let option; option = options[insertionIndex]; insertionIndex++) {
    if (option.text == Msg.COLLAPSE_BLOCK) {
      break;
    }
  }
  options.splice(insertionIndex, 0, horizVertOption);
  for (let i = 0, option; option = options[i]; i++) {
    if (option.text == Msg.INLINE_INPUTS) {
      options.splice(i, 1);
      break;
    }
  }
};
FieldParameterFlydown.fromJson = function(options) {
  const name = utils.replaceMessageReferences(options["name"]);
  return new FieldParameterFlydown(name, options["is_editable"]);
};
fieldRegistry.register("field_parameter_flydown", FieldParameterFlydown);
const FieldProcedureName = function(text) {
  FieldProcedureName.superClass_.constructor.call(this, text, renameProcedure);
};
utils.object.inherits(FieldProcedureName, FieldTextInput);
FieldProcedureName.prototype.setValue = function(newValue) {
  const oldValue = this.getValue();
  this.oldName_ = oldValue;
  this.doValueUpdate_(newValue);
  FieldProcedureName.superClass_.setValue.call(this, newValue);
  newValue = this.getValue();
  if (typeof newValue === "string" && this.sourceBlock_) {
    const procDb = this.sourceBlock_.workspace.getProcedureDatabase();
    if (procDb) {
      if (procDb.getProcedure(this.sourceBlock_.id)) {
        procDb.renameProcedure(this.sourceBlock_.id, oldValue, newValue);
      } else {
        procDb.addProcedure(newValue, this.sourceBlock_);
      }
    }
  }
  this.oldName_ = void 0;
};
FieldProcedureName.fromJson = function(options) {
  const name = utils.replaceMessageReferences(options["name"]);
  return new FieldProcedureName(name);
};
fieldRegistry.register("field_procedurename", FieldProcedureName);
delete Blocks["global_declaration"];
Blocks["global_declaration"] = {
  category: "Variables",
  helpUrl: Msg.LANG_VARIABLES_GLOBAL_DECLARATION_HELPURL,
  init: function() {
    this.setStyle("variable_blocks");
    this.appendValueInput("VALUE").appendField(Msg.LANG_VARIABLES_GLOBAL_DECLARATION_TITLE_INIT).appendField(new FieldGlobalFlydown(Msg.LANG_VARIABLES_GLOBAL_DECLARATION_NAME, FieldFlydown.DISPLAY_BELOW), "NAME").appendField(Msg.LANG_VARIABLES_GLOBAL_DECLARATION_TO);
    this.setTooltip(Msg.LANG_VARIABLES_GLOBAL_DECLARATION_TOOLTIP);
  },
  getVars: function() {
    const field = this.getField("NAME");
    return field ? [field.getText()] : [];
  },
  getGlobalNames: function() {
    return this.getVars();
  },
  renameVar: function(oldName, newName) {
    if (Names.equals(oldName, this.getFieldValue("NAME"))) {
      this.setFieldValue(newName, "NAME");
    }
  }
};
Blocks["lexical_variable_get"] = {
  category: "Variables",
  helpUrl: Msg.LANG_VARIABLES_GET_HELPURL,
  init: function() {
    this.setStyle("variable_blocks");
    this.fieldVar_ = new FieldLexicalVariable(" ");
    this.fieldVar_.setBlock(this);
    this.appendDummyInput().appendField(Msg.LANG_VARIABLES_GET_TITLE_GET).appendField(this.fieldVar_, "VAR");
    this.setOutput(true, null);
    this.setTooltip(Msg.LANG_VARIABLES_GET_TOOLTIP);
    this.errors = [
      {func: checkIsInDefinition},
      {
        func: checkDropDownContainsValidValue,
        dropDowns: ["VAR"]
      }
    ];
    this.setOnChange(function(changeEvent) {
      checkErrors(this);
    });
  },
  referenceResults: function(name, prefix, env) {
    const childrensReferenceResults = this.getChildren().map(function(blk) {
      return LexicalVariable.referenceResult(blk, name, prefix, env);
    });
    let blocksToRename = [];
    let capturables = [];
    for (let r = 0; r < childrensReferenceResults.length; r++) {
      blocksToRename = blocksToRename.concat(childrensReferenceResults[r][0]);
      capturables = capturables.concat(childrensReferenceResults[r][1]);
    }
    const possiblyPrefixedReferenceName = this.getField("VAR").getText();
    const unprefixedPair = unprefixName(possiblyPrefixedReferenceName);
    const referencePrefix = unprefixedPair[0];
    const referenceName = unprefixedPair[1];
    const referenceNotInEnv = env.indexOf(referenceName) == -1;
    if (!(referencePrefix === Msg.LANG_VARIABLES_GLOBAL_PREFIX)) {
      if (referenceName === name && referenceNotInEnv) {
        blocksToRename.push(this);
        {
          capturables = capturables.concat(env);
        }
      } else if (referenceNotInEnv && !usePrefixInCode) {
        capturables.push(referenceName);
      }
    }
    return [[blocksToRename, capturables]];
  },
  getVars: function() {
    return [this.getFieldValue("VAR")];
  },
  renameLexicalVar: function(oldName, newName, oldTranslatedName, newTranslatedName) {
    if (oldTranslatedName === void 0) {
      if (oldName === this.getFieldValue("VAR")) {
        this.setFieldValue(newName, "VAR");
      }
    } else if (oldTranslatedName && oldTranslatedName === this.fieldVar_.getText()) {
      this.fieldVar_.getOptions(false);
      this.fieldVar_.setValue(newName);
      if (oldName === newName) {
        this.setFieldValue(newName, "VAR");
      }
      this.fieldVar_.forceRerender();
    }
  },
  renameFree: function(freeSubstitution) {
    const prefixPair = unprefixName$1(this.getFieldValue("VAR"));
    const prefix = prefixPair[0];
    if (prefix !== Msg.LANG_VARIABLES_GLOBAL_PREFIX) {
      const oldName = prefixPair[1];
      const newName = freeSubstitution.apply(oldName);
      if (newName !== oldName) {
        this.renameLexicalVar(oldName, newName);
      }
    }
  },
  freeVariables: function() {
    const prefixPair = unprefixName$1(this.getFieldValue("VAR"));
    const prefix = prefixPair[0];
    if (prefix !== Msg.LANG_VARIABLES_GLOBAL_PREFIX) {
      const oldName = prefixPair[1];
      return new NameSet([oldName]);
    } else {
      return new NameSet();
    }
  }
};
Blocks["lexical_variable_set"] = {
  category: "Variables",
  helpUrl: Msg.LANG_VARIABLES_SET_HELPURL,
  init: function() {
    this.setStyle("variable_blocks");
    this.fieldVar_ = new FieldLexicalVariable(" ");
    this.fieldVar_.setBlock(this);
    this.appendValueInput("VALUE").appendField(Msg.LANG_VARIABLES_SET_TITLE_SET).appendField(this.fieldVar_, "VAR").appendField(Msg.LANG_VARIABLES_SET_TITLE_TO);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(Msg.LANG_VARIABLES_SET_TOOLTIP);
    this.errors = [
      {func: checkIsInDefinition},
      {
        func: checkDropDownContainsValidValue,
        dropDowns: ["VAR"]
      }
    ];
    this.setOnChange(function(changeEvent) {
      checkErrors(this);
    });
  },
  referenceResults: Blocks.lexical_variable_get.referenceResults,
  getVars: function() {
    return [this.getFieldValue("VAR")];
  },
  renameLexicalVar: Blocks.lexical_variable_get.renameLexicalVar,
  renameFree: function(freeSubstitution) {
    const prefixPair = unprefixName$1(this.getFieldValue("VAR"));
    const prefix = prefixPair[0];
    if (prefix !== Msg.LANG_VARIABLES_GLOBAL_PREFIX) {
      const oldName = prefixPair[1];
      const newName = freeSubstitution.apply(oldName);
      if (newName !== oldName) {
        this.renameLexicalVar(oldName, newName);
      }
    }
    this.getChildren().map(function(blk) {
      LexicalVariable.renameFree(blk, freeSubstitution);
    });
  },
  freeVariables: function() {
    const childrenFreeVars = this.getChildren().map(function(blk) {
      return LexicalVariable.freeVariables(blk);
    });
    const result = NameSet.unionAll(childrenFreeVars);
    const prefixPair = unprefixName$1(this.getFieldValue("VAR"));
    const prefix = prefixPair[0];
    if (prefix !== Msg.LANG_VARIABLES_GLOBAL_PREFIX) {
      const oldName = prefixPair[1];
      result.insert(oldName);
    }
    return result;
  }
};
Blocks["local_declaration_statement"] = {
  category: "Variables",
  helpUrl: Msg.LANG_VARIABLES_LOCAL_DECLARATION_HELPURL,
  bodyInputName: "STACK",
  init: function() {
    this.initLocals();
    this.appendStatementInput("STACK").appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_IN_DO);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip(Msg.LANG_VARIABLES_LOCAL_DECLARATION_TOOLTIP);
    this.lexicalVarPrefix = localNamePrefix;
  },
  referenceResults: function(name, prefix, env) {
    const localDeclNames = [];
    for (let i = 0; this.getInput("DECL" + i); i++) {
      let localName = this.getFieldValue("VAR" + i);
      localDeclNames.push(localName);
    }
    const newEnv = env.concat(localDeclNames);
    const localInits = [];
    for (let i = 0; this.getInput("DECL" + i); i++) {
      const init2 = this.getInputTargetBlock("DECL" + i);
      if (init2) {
        localInits.push(init2);
      }
    }
    const initResults = localInits.map(function(init2) {
      return LexicalVariable.referenceResult(init2, name, prefix, env);
    });
    const doResults = LexicalVariable.referenceResult(this.getInputTargetBlock("STACK"), name, prefix, newEnv);
    const nextResults = LexicalVariable.referenceResult(LexicalVariable.getNextTargetBlock(this), name, prefix, env);
    return initResults.concat([doResults, nextResults]);
  },
  withLexicalVarsAndPrefix: function(child, proc) {
    if (this.getInputTargetBlock(this.bodyInputName) == child) {
      const localNames = this.declaredNames();
      for (let i = 0; i < localNames.length; i++) {
        proc(localNames[i], this.lexicalVarPrefix);
      }
    }
  },
  initLocals: function() {
    this.setStyle("variable_blocks");
    this.localNames_ = [Msg.LANG_VARIABLES_LOCAL_DECLARATION_DEFAULT_NAME];
    const declInput = this.appendValueInput("DECL0");
    declInput.appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_TITLE_INIT).appendField(this.parameterFlydown(0), "VAR0").appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_INPUT_TO).setAlign(ALIGN_RIGHT);
    this.setMutator(new Mutator(["local_mutatorarg"]));
  },
  onchange: function() {
    this.localNames_ = this.declaredNames();
  },
  mutationToDom: function() {
    const container = document.createElement("mutation");
    for (let i = 0; i < this.localNames_.length; i++) {
      const parameter = document.createElement("localname");
      parameter.setAttribute("name", this.localNames_[i]);
      container.appendChild(parameter);
    }
    return container;
  },
  domToMutation: function(xmlElement) {
    const children = getChildren(xmlElement);
    if (children.length > 0) {
      this.localNames_ = [];
      for (let i = 0, childNode; childNode = children[i]; i++) {
        if (childNode.nodeName.toLowerCase() == "localname") {
          this.localNames_.push(childNode.getAttribute("name"));
        }
      }
    }
    this.updateDeclarationInputs_(this.localNames_);
  },
  updateDeclarationInputs_: function(names, inits) {
    const bodyInput = this.inputList[this.inputList.length - 1];
    const numDecls = this.inputList.length - 1;
    const savedRendered = this.rendered;
    this.rendered = false;
    const thisBlock = this;
    FieldParameterFlydown.withChangeHanderDisabled(function() {
      for (let i = 0; i < numDecls; i++) {
        thisBlock.removeInput("DECL" + i);
      }
    });
    this.inputList = [];
    this.localNames_ = names;
    for (let i = 0; i < names.length; i++) {
      const declInput = this.appendValueInput("DECL" + i);
      declInput.appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_TITLE_INIT).appendField(this.parameterFlydown(i), "VAR" + i).appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_INPUT_TO).setAlign(ALIGN_RIGHT);
      if (inits && inits[i]) {
        declInput.connection.connect(inits[i]);
      }
    }
    this.inputList = this.inputList.concat(bodyInput);
    this.rendered = savedRendered;
    if (this.rendered) {
      this.initSvg();
      this.render();
    }
  },
  parameterFlydown: function(paramIndex) {
    const initialParamName = this.localNames_[paramIndex];
    const localDecl = this;
    const localParameterChangeHandler = function(newParamName) {
      const newLocals = localDecl.localNames_;
      newLocals[paramIndex] = newParamName;
      if (localDecl.mutator && localDecl.mutator.rootBlock_) {
        const mutatorContainer = localDecl.mutator.rootBlock_;
        let mutatorargIndex = 0;
        let mutatorarg = mutatorContainer.getInputTargetBlock("STACK");
        while (mutatorarg && mutatorargIndex < paramIndex) {
          mutatorarg = mutatorarg.nextConnection && mutatorarg.nextConnection.targetBlock();
          mutatorargIndex++;
        }
        if (mutatorarg && mutatorargIndex == paramIndex) {
          Field.prototype.setValue.call(mutatorarg.getField("NAME"), newParamName);
        }
      }
    };
    return new FieldParameterFlydown(initialParamName, true, FieldFlydown.DISPLAY_RIGHT, localParameterChangeHandler);
  },
  decompose: function(workspace) {
    const containerBlock = workspace.newBlock("local_mutatorcontainer");
    containerBlock.initSvg();
    containerBlock.setDefBlock(this);
    let connection = containerBlock.getInput("STACK").connection;
    for (let i = 0; i < this.localNames_.length; i++) {
      const localName = this.getFieldValue("VAR" + i);
      const nameBlock = workspace.newBlock("local_mutatorarg");
      nameBlock.initSvg();
      nameBlock.setFieldValue(localName, "NAME");
      nameBlock.oldLocation = i;
      connection.connect(nameBlock.previousConnection);
      connection = nameBlock.nextConnection;
    }
    return containerBlock;
  },
  compose: function(containerBlock) {
    const newLocalNames = [];
    const initializers = [];
    let mutatorarg = containerBlock.getInputTargetBlock("STACK");
    while (mutatorarg) {
      newLocalNames.push(mutatorarg.getFieldValue("NAME"));
      initializers.push(mutatorarg.valueConnection_);
      mutatorarg = mutatorarg.nextConnection && mutatorarg.nextConnection.targetBlock();
    }
    if (!LexicalVariable.stringListsEqual(this.localNames_, newLocalNames)) {
      this.updateDeclarationInputs_(newLocalNames, initializers);
    }
  },
  dispose: function(...args) {
    BlockSvg.prototype.dispose.apply(this, args);
  },
  saveConnections: function(containerBlock) {
    let nameBlock = containerBlock.getInputTargetBlock("STACK");
    let i = 0;
    while (nameBlock) {
      const localDecl = this.getInput("DECL" + i);
      nameBlock.valueConnection_ = localDecl && localDecl.connection.targetConnection;
      i++;
      nameBlock = nameBlock.nextConnection && nameBlock.nextConnection.targetBlock();
    }
    const bodyInput = this.getInput(this.bodyInputName);
    if (bodyInput) {
      containerBlock.bodyConnection_ = bodyInput.connection.targetConnection;
    }
  },
  getVars: function() {
    const varList = [];
    for (let i = 0, input; input = this.getField("VAR" + i); i++) {
      varList.push(input.getValue());
    }
    return varList;
  },
  declaredNames: function() {
    return this.getVars();
  },
  declaredVariables: function() {
    return this.getVars();
  },
  initializerConnections: function() {
    const connections = [];
    for (let i = 0, input; input = this.getInput("DECL" + i); i++) {
      connections.push(input.connection && input.connection.targetConnection);
    }
    return connections;
  },
  blocksInScope: function() {
    const doBody = this.getInputTargetBlock(this.bodyInputName);
    const doBodyList = doBody && [doBody] || [];
    return doBodyList;
  },
  renameVar: function(oldName, newName) {
    this.renameVars(Substitution.simpleSubstitution(oldName, newName));
  },
  renameVars: function(substitution) {
    const localNames = this.declaredNames();
    const renamedLocalNames = substitution.map(localNames);
    if (!LexicalVariable.stringListsEqual(renamedLocalNames, localNames)) {
      const initializerConnections = this.initializerConnections();
      this.updateDeclarationInputs_(renamedLocalNames, initializerConnections);
      if (this.mutator.isVisible()) {
        const blocks = this.mutator.workspace_.getAllBlocks();
        for (let x = 0, block; block = blocks[x]; x++) {
          if (block.type == "procedures_mutatorarg") {
            const oldName = block.getFieldValue("NAME");
            const newName = substitution.apply(oldName);
            if (newName !== oldName) {
              block.setFieldValue(newName, "NAME");
            }
          }
        }
      }
    }
  },
  renameBound: function(boundSubstitution, freeSubstitution) {
    const oldMutation = Xml.domToText(this.mutationToDom());
    const localNames = this.declaredNames();
    for (let i = 0; i < localNames.length; i++) {
      LexicalVariable.renameFree(this.getInputTargetBlock("DECL" + i), freeSubstitution);
    }
    const paramSubstitution = boundSubstitution.restrictDomain(localNames);
    this.renameVars(paramSubstitution);
    const newFreeSubstitution = freeSubstitution.remove(localNames).extend(paramSubstitution);
    LexicalVariable.renameFree(this.getInputTargetBlock(this.bodyInputName), newFreeSubstitution);
    const newMutation = Xml.domToText(this.mutationToDom());
    if (Events.isEnabled()) {
      Events.fire(new Events.BlockChange(this, "mutation", null, oldMutation, newMutation));
    }
    if (this.nextConnection) {
      const nextBlock = this.nextConnection.targetBlock();
      LexicalVariable.renameFree(nextBlock, freeSubstitution);
    }
  },
  renameFree: function(freeSubstitution) {
    const localNames = this.declaredNames();
    const localNameSet = new NameSet(localNames);
    const bodyFreeVars = LexicalVariable.freeVariables(this.getInputTargetBlock(this.bodyInputName));
    bodyFreeVars.subtract(localNameSet);
    const renamedFreeVars = bodyFreeVars.renamed(freeSubstitution);
    const capturedVars = renamedFreeVars.intersection(localNameSet);
    if (!capturedVars.isEmpty()) {
      const forbiddenNames = localNameSet.union(renamedFreeVars).toList();
      const boundBindings = {};
      const capturedVarList = capturedVars.toList();
      for (let i = 0, capturedVar; capturedVar = capturedVarList[i]; i++) {
        const newCapturedVar = FieldLexicalVariable.nameNotIn(capturedVar, forbiddenNames);
        boundBindings[capturedVar] = newCapturedVar;
        forbiddenNames.push(newCapturedVar);
      }
      this.renameBound(new Substitution(boundBindings), freeSubstitution);
    } else {
      this.renameBound(new Substitution(), freeSubstitution);
    }
  },
  freeVariables: function() {
    const result = LexicalVariable.freeVariables(this.getInputTargetBlock(this.bodyInputName));
    const localNames = this.declaredNames();
    result.subtract(new NameSet(localNames));
    const numDecls = localNames.length;
    for (let i = 0; i < numDecls; i++) {
      result.union(LexicalVariable.freeVariables(this.getInputTargetBlock("DECL" + i)));
    }
    if (this.nextConnection) {
      const nextBlock = this.nextConnection.targetBlock();
      result.unite(LexicalVariable.freeVariables(nextBlock));
    }
    return result;
  }
};
Blocks["local_declaration_expression"] = {
  category: "Variables",
  helpUrl: Msg.LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_HELPURL,
  initLocals: Blocks.local_declaration_statement.initLocals,
  bodyInputName: "RETURN",
  init: function() {
    this.initLocals();
    this.appendValueInput("RETURN").appendField(Msg.LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_IN_RETURN);
    this.setOutput(true, null);
    this.setTooltip(Msg.LANG_VARIABLES_LOCAL_DECLARATION_EXPRESSION_TOOLTIP);
  },
  referenceResults: function(name, prefix, env) {
    const localDeclNames = [];
    for (let i = 0; this.getInput("DECL" + i); i++) {
      let localName = this.getFieldValue("VAR" + i);
      localDeclNames.push(localName);
    }
    const newEnv = env.concat(localDeclNames);
    const localInits = [];
    for (let i = 0; this.getInput("DECL" + i); i++) {
      const init2 = this.getInputTargetBlock("DECL" + i);
      if (init2) {
        localInits.push(init2);
      }
    }
    const initResults = localInits.map(function(init2) {
      return LexicalVariable.referenceResult(init2, name, prefix, env);
    });
    const returnResults = LexicalVariable.referenceResult(this.getInputTargetBlock("RETURN"), name, prefix, newEnv);
    return initResults.concat([returnResults]);
  },
  withLexicalVarsAndPrefix: Blocks.local_declaration_statement.withLexicalVarsAndPrefix,
  onchange: Blocks.local_declaration_statement.onchange,
  mutationToDom: Blocks.local_declaration_statement.mutationToDom,
  domToMutation: Blocks.local_declaration_statement.domToMutation,
  updateDeclarationInputs_: Blocks.local_declaration_statement.updateDeclarationInputs_,
  parameterFlydown: Blocks.local_declaration_statement.parameterFlydown,
  blocksInScope: Blocks.local_declaration_statement.blocksInScope,
  decompose: Blocks.local_declaration_statement.decompose,
  compose: Blocks.local_declaration_statement.compose,
  dispose: Blocks.local_declaration_statement.dispose,
  saveConnections: Blocks.local_declaration_statement.saveConnections,
  getVars: Blocks.local_declaration_statement.getVars,
  declaredNames: Blocks.local_declaration_statement.declaredNames,
  declaredVariables: Blocks.local_declaration_statement.declaredVariables,
  renameVar: Blocks.local_declaration_statement.renameVar,
  renameVars: Blocks.local_declaration_statement.renameVars,
  renameBound: Blocks.local_declaration_statement.renameBound,
  renameFree: Blocks.local_declaration_statement.renameFree,
  freeVariables: Blocks.local_declaration_statement.freeVariables
};
Blocks["local_mutatorcontainer"] = {
  init: function() {
    this.setStyle("variable_blocks");
    this.appendDummyInput().appendField(Msg.LANG_VARIABLES_LOCAL_MUTATOR_CONTAINER_TITLE_LOCAL_NAMES);
    this.appendStatementInput("STACK");
    this.setTooltip(Msg.LANG_VARIABLES_LOCAL_MUTATOR_CONTAINER_TOOLTIP);
    this.contextMenu = false;
    this.mustNotRenameCapturables = true;
  },
  setDefBlock: function(defBlock) {
    this.defBlock_ = defBlock;
  },
  getDefBlock: function() {
    return this.defBlock_;
  },
  declaredNames: function() {
    const paramNames = [];
    let paramBlock = this.getInputTargetBlock("STACK");
    while (paramBlock) {
      paramNames.push(paramBlock.getFieldValue("NAME"));
      paramBlock = paramBlock.nextConnection && paramBlock.nextConnection.targetBlock();
    }
    return paramNames;
  }
};
Blocks["local_mutatorarg"] = {
  init: function() {
    this.setStyle("variable_blocks");
    this.appendDummyInput().appendField(Msg.LANG_VARIABLES_LOCAL_MUTATOR_ARG_TITLE_NAME).appendField(new FieldTextInput(Msg.LANG_VARIABLES_LOCAL_MUTATOR_ARG_DEFAULT_VARIABLE, LexicalVariable.renameParam), "NAME");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip("");
    this.contextMenu = false;
    this.lexicalVarPrefix = localNamePrefix;
    this.mustNotRenameCapturables = true;
  },
  getContainerBlock: function() {
    let parent = this.getParent();
    while (parent && !(parent.type === "local_mutatorcontainer")) {
      parent = parent.getParent();
    }
    this.cachedContainerBlock_ = parent && parent.type === "local_mutatorcontainer" && parent || null;
    return this.cachedContainerBlock_;
  },
  getDefBlock: function() {
    const container = this.getContainerBlock();
    return container && container.getDefBlock() || null;
  },
  blocksInScope: function() {
    const defBlock = this.getDefBlock();
    return defBlock && defBlock.blocksInScope() || [];
  },
  declaredNames: function() {
    const container = this.getContainerBlock();
    return container && container.declaredNames() || [];
  },
  onchange: function() {
    const paramName = this.getFieldValue("NAME");
    if (paramName) {
      const cachedContainer = this.cachedContainerBlock_;
      const container = this.getContainerBlock();
      if (!cachedContainer && container) {
        const declaredNames = this.declaredNames();
        const firstIndex = declaredNames.indexOf(paramName);
        if (firstIndex != -1) {
          const secondIndex = declaredNames.indexOf(paramName, firstIndex + 1);
          if (secondIndex != -1) {
            const newName = FieldLexicalVariable.nameNotIn(paramName, declaredNames);
            this.setFieldValue(newName, "NAME");
          }
        }
      }
    }
  }
};
function getVariableName(name) {
  const pair = unprefixName(name);
  const prefix = pair[0];
  const unprefixedName = pair[1];
  if (prefix === Msg.LANG_VARIABLES_GLOBAL_PREFIX || prefix === GLOBAL_KEYWORD) {
    return unprefixedName;
  } else {
    return possiblyPrefixGeneratedVarName()(unprefixedName);
  }
}
function genBasicSetterCode(block, varFieldName) {
  const argument0 = JavaScript.valueToCode(block, "VALUE", JavaScript.ORDER_ASSIGNMENT) || "0";
  const varName = getVariableName(block.getFieldValue(varFieldName));
  return varName + " = " + argument0 + ";\n";
}
/**
 * @license
 * Copyright 2021 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */
registerCss();
function init(workspace) {
  const flydown = new Flydown(new Options({scrollbars: false}));
  workspace.flydown_ = flydown;
  utils.dom.insertAfter(flydown.createDom("g"), workspace.svgBubbleCanvas_);
  flydown.init(workspace);
  flydown.autoClose = true;
}

export {init};
export default null;
