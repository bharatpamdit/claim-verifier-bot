import "dotenv/config";
import app from "./app.js";
const port = Number(process.env.PORT || 5000);
const host = process.env.HOST || "127.0.0.1";
app.listen(port, host, () => console.log(`IssueLens API: http://${host}:${port}`));
