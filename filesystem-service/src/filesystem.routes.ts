import { Router } from "express";
import { FileSystemService } from "./filesystemservice";

const router = Router();

const fileSystem = new FileSystemService();


// CREATE FOLDER
router.post("/folders", async (req, res) => {
    try {
        const { name, path } = req.body;

        await fileSystem.createFolder(name, path);

        res.status(201).json({
            message: "Folder created"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to create folder"
        });
    }
});


// RENAME FOLDER
router.patch("/folders/rename", async (req, res) => {
    try {
        const { path, newName } = req.body;

        await fileSystem.renameFolder(path, newName);

        res.status(200).json({
            message: "Folder renamed"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to rename folder"
        });
    }
});


// DELETE FOLDER
router.delete("/folders", async (req, res) => {
    try {
        const { path } = req.body;

        await fileSystem.deleteFolder(path);

        res.status(200).json({
            message: "Folder deleted"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to delete folder"
        });
    }
});


// CREATE FILE
router.post("/files", async (req, res) => {
    try {
        const { name, path } = req.body;

        await fileSystem.createFile(name, path);

        res.status(201).json({
            message: "File created"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to create file"
        });
    }
});


// RENAME FILE
router.patch("/files/rename", async (req, res) => {
    try {
        const { path, newName } = req.body;

        await fileSystem.renameFile(path, newName);

        res.status(200).json({
            message: "File renamed"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to rename file"
        });
    }
});


// DELETE FILE
router.delete("/files", async (req, res) => {
    try {
        const { path } = req.body;

        await fileSystem.deleteFile(path);

        res.status(200).json({
            message: "File deleted"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to delete file"
        });
    }
});


// SAVE FILE
router.put("/files", async (req, res) => {
    try {
        const { path, content } = req.body;

        await fileSystem.saveFile(path, content);

        res.status(200).json({
            message: "File saved"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to save file"
        });
    }
});


// MOVE FILE / SAVE AS
router.patch("/files/move", async (req, res) => {
    try {
        const {
            path,
            newPath,
            newName
        } = req.body;

        await fileSystem.moveFile(
            path,
            newPath,
            newName
        );

        res.status(200).json({
            message: "File moved"
        });

    } catch (error) {
        res.status(500).json({
            error: "Failed to move file"
        });
    }
});

router.get("/folders", async (req, res) => {
    try {
        const { name, path } = req.query;

        const folderName =
            typeof name === "string" ? name : null;

        const parentPath =
            typeof path === "string" ? path : "";

        const contents = await fileSystem.readDirectory(
            folderName,
            parentPath
        );

        res.status(200).json(contents);

    } catch (error) {
        console.error(error);

        res.status(500).json({
            error: "Failed to read directory"
        });
    }
});

router.get("/files", async (req, res) => {
    try {
        const { path } = req.query;

        if (typeof path !== "string" || !path) {
            return res.status(400).json({
                error: "File path is required"
            });
        }

        const file = await fileSystem.readFile(path);

        return res.status(200).json(file);

    } catch (error) {
        console.error(error);

        return res.status(500).json({
            error: "Failed to read file"
        });
    }
});


export default router;