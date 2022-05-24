/*
    If page contains an adaptive-card element,
    automatically render it as Adaptive Card.
*/

var markdown = null;
// Set page-specific options.
const opt = document.getElementById("page-options");

function parseActionData(data) {
    var d = {"options": {}, "data": {}};
    for (const key in data) {
        if (key.startsWith("_")) {
            d["options"][key.replace("_", "")] = data[key];
        } else {
            d["data"][key] = data[key];
        }
    }
    return d;
}

function parseAction(action) {
    const act = parseActionData(action.data);
    console.log(act);
}

function setContentWidth(width) {
    if (!width)
        return;
    const area = document.querySelector(".md-main__inner.md-grid");
    if (area)
        area.setAttribute("style", "max-width: " + width + "px;");
}

if (opt) {
    setContentWidth(opt.getAttribute("docs-width") || null);
    opt.parentElement.remove();
}

function renderAdaptiveCard(ac) {
    if (!ac.innerText)
        return;
    const card = JSON.parse(ac.innerText);
    ac.innerHTML = "";
    var adaptiveCard = new AdaptiveCards.AdaptiveCard();
    adaptiveCard.hostConfig = new AdaptiveCards.HostConfig({
        fontFamily: "var(--md-text-font,_),-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif",
        fontSizes: {
            small: 14,
            default: 16,
            medium: 20,
            large: 24,
            extraLarge: 30
        },
        spacing: {
            small: 16,
            default: 30,
            medium: 45,
            large: 60
        }
    });
    adaptiveCard.parse(card);
    adaptiveCard.onExecuteAction = AdaptiveCards.onExecuteAction;
    var renderedCard = adaptiveCard.render();
    ac.removeAttribute("style");
    // Use mkdocs styles.
    for (const el of renderedCard.querySelectorAll("button")) {
        el.className = "md-button md-button--primary primary-button";
    }
    for (const el of renderedCard.querySelectorAll('input[type="text"]')) {
        el.className = "md-input";
    }
    for (const el of renderedCard.querySelectorAll('.ac-textBlock')) {
        el.className = "md-typeset";
        el.style.removeProperty("color");
        el.style.removeProperty("line-height");
    }
    for (const el of renderedCard.querySelectorAll('.ac-textRun')) {
        el.className = "md-typeset";
    }
    ac.appendChild(renderedCard);
}

function renderAllAdaptiveCards() {
    var md = document.createElement("script");
    md.src = "https://unpkg.com/markdown-it@12.3.2/dist/markdown-it.min.js";
    md.onload = () => {
        markdown = window.markdownit();
        var script = document.createElement("script");
        script.src = "https://unpkg.com/adaptivecards@2.10.0/dist/adaptivecards.min.js";
        script.onload = () => {
            AdaptiveCards.onProcessMarkdown = function(text, result) {
                result.outputHtml = markdown.render(text);
                result.didProcess = true;
            }
            // Add action handler.
            AdaptiveCards.onExecuteAction = (action) => {
                if (action instanceof AdaptiveCards.SubmitAction) {
                    parseAction(action);
                }
            }
            for (const elem in document.getElementsByName("adaptivecard")) {
                renderAdaptiveCard(elem);
            }
        }
        document.body.appendChild(script);
    }
    document.body.appendChild(md);
}

renderAllAdaptiveCards();