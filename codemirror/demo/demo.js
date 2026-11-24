import {defaultHighlightStyle, syntaxHighlighting} from "@codemirror/language";
import {EditorState} from "@codemirror/state";
import {EditorView} from "@codemirror/view";
import {alloy} from "../src/alloy.js";

const picker = document.querySelector("#fixture");
const status = document.querySelector("#status");
const editor = new EditorView({
  state: EditorState.create({
    doc: "",
    extensions: [alloy, syntaxHighlighting(defaultHighlightStyle), EditorView.lineWrapping],
  }),
  parent: document.querySelector("#editor"),
});

async function loadFixture(filename) {
  status.textContent = "Loading…";
  try {
    const response = await fetch(`/tests/fixtures/${encodeURIComponent(filename)}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const source = await response.text();
    editor.setState(EditorState.create({
      doc: source,
      extensions: [alloy, syntaxHighlighting(defaultHighlightStyle), EditorView.lineWrapping],
    }));
    status.textContent = `${filename} · ${source.split("\n").length} lines`;
  } catch (error) {
    status.textContent = `Could not load ${filename}: ${error.message}`;
  }
}

picker.addEventListener("change", () => loadFixture(picker.value));
loadFixture(picker.value);
