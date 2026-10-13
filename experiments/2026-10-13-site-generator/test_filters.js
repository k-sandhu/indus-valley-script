"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const path = require("node:path");

async function run() {
  const out = process.argv[2] || "_site";
  const rows = JSON.parse(fs.readFileSync(path.join(out, "questions/index.json"), "utf8"));
  const page = fs.readFileSync(path.join(out, "questions/index.html"), "utf8");
  const ids = [...page.matchAll(/data-id="([^"]+)"/g)].map(match => match[1]);
  const eligible = rows.filter(row => ["open", "claimed"].includes(row.status));
  assert.deepEqual(ids, eligible.map(row => row.id));
  const nodes = ids.map(id => ({dataset: {id}, hidden: false}));
  const handlers = {};
  let values = new Map([["search", ""]]);
  const form = {addEventListener: (name, fn) => {handlers[name] = fn;}};
  const count = {textContent: ""};
  const listing = {
    dataset: {index: "index.json"},
    querySelector: selector => selector === "form" ? form : count,
    querySelectorAll: () => nodes
  };
  class TestFormData {
    get(field) { return values.get(field); }
    [Symbol.iterator]() { return values[Symbol.iterator](); }
  }
  vm.runInNewContext(fs.readFileSync("site/static/site.js", "utf8"), {
    document: {querySelectorAll: () => [listing]}, FormData: TestFormData,
    fetch: async url => {assert.equal(url, "index.json"); return {ok: true, json: async () => rows};},
    setTimeout
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(typeof handlers.input, "function");
  const chosen = eligible[0];
  values = new Map([["search", chosen.title.toLowerCase()]]);
  handlers.input();
  assert.equal(nodes.filter(node => !node.hidden).length, 1);
  assert.equal(nodes.find(node => !node.hidden).dataset.id, chosen.id);
  for (const field of ["area", "kind", "difficulty", "data_access", "priority"]) {
    values = new Map([["search", ""], [field, String(chosen[field])]]);
    handlers.change();
    const expected = eligible.filter(row => String(row[field]) === String(chosen[field]));
    assert.deepEqual(nodes.filter(node => !node.hidden).map(node => node.dataset.id), expected.map(row => row.id));
  }
  values = new Map([["search", ""], ["area", chosen.area], ["kind", chosen.kind], ["priority", String(chosen.priority)]]);
  handlers.change();
  const combined = eligible.filter(row => row.area === chosen.area && row.kind === chosen.kind && row.priority === chosen.priority);
  assert.equal(nodes.filter(node => !node.hidden).length, combined.length);
  values = new Map([["search", ""]]);
  handlers.reset();
  await new Promise(resolve => setTimeout(resolve, 10));
  assert.equal(nodes.filter(node => !node.hidden).length, eligible.length);
  let prevented = false;
  handlers.submit({preventDefault: () => {prevented = true;}});
  assert.ok(prevented);
  return {ok: true, questions: eligible.length, search: "passed", filters: "all five and combined passed", reset: "passed", no_script_rows: "complete"};
}
run().then(result => process.stdout.write(JSON.stringify(result, null, 2) + "\n")).catch(error => {console.error(error); process.exitCode = 1;});
