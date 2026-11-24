import { createServer } from "./app.js";
const port = process.env.PORT || 3000;
createServer().listen(port, () => console.log(`listening on :${port}`));
