import { test } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "../src/app.js";

test("GET /todos returns a list", async () => {
  const server = createServer().listen(0);
  const { port } = server.address();
  const res = await fetch(`http://127.0.0.1:${port}/todos`);
  assert.equal(res.status, 200);
  assert.ok(Array.isArray(await res.json()));
  server.close();
});
