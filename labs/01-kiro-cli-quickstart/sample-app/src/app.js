import http from "node:http";

const todos = [{ id: 1, title: "Try Kiro CLI", done: false }];

export function createServer() {
  return http.createServer((req, res) => {
    if (req.method === "GET" && req.url === "/todos") {
      res.writeHead(200, { "content-type": "application/json" });
      return res.end(JSON.stringify(todos));
    }
    res.writeHead(404, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "not found" }));
  });
}
