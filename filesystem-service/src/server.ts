import express from "express";
import cors from "cors";
import filesystemRoutes from "./filesystem.routes";

const app = express();

app.use(cors());

app.use(express.json());

app.get("/health", (req, res) => {
    res.json({
        status: "ok"
    });
});

app.use("/api", filesystemRoutes);

const PORT = 3005;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Filesystem service running on port ${PORT}`);
});