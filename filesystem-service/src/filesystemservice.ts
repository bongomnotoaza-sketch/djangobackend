import { promises as fs } from "node:fs";
import path from "node:path";

export class FileSystemService {

    private readonly root = "/tmp/filesystem-test";

    async createFolder(
        name: string,
        parentPath: string
    ): Promise<void> {

        const folderPath = path.resolve(
            this.root,
            parentPath,
            name
        );

        // Prevent escaping /home/terminal
        if (
            folderPath !== this.root &&
            !folderPath.startsWith(this.root + path.sep)
        ) {
            throw new Error("Invalid path");
        }

        await fs.mkdir(folderPath);
    }

     async renameFolder(
        folderPath: string,
        newName: string
    ): Promise<void> {

        const currentPath = path.resolve(
            this.root,
            folderPath
        );

        const newPath = path.join(
            path.dirname(currentPath),
            newName
        );

        // Prevent access outside /home/terminal
        if (
            !currentPath.startsWith(this.root + path.sep) ||
            !newPath.startsWith(this.root + path.sep)
        ) {
            throw new Error("Invalid path");
        }

        await fs.rename(
            currentPath,
            newPath
        );
    }

    async deleteFolder(folderPath: string): Promise<void> {
    const targetPath = path.resolve(
        this.root,
        folderPath
    );

    if (
        !targetPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.rm(targetPath, {
        recursive: true,
        force: false
    });
    
    }

    async createFile(fileName: string, parentPath: string): Promise<void> {
    const filePath = path.resolve(
        this.root,
        parentPath,
        fileName
    );

    if (
        !filePath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.writeFile(filePath, "");

    }

    async renameFile(
    filePath: string,
    newName: string
    ): Promise<void> {
    const currentPath = path.resolve(
        this.root,
        filePath
    );

    const newPath = path.join(
        path.dirname(currentPath),
        newName
    );

    if (
        !currentPath.startsWith(this.root + path.sep) ||
        !newPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.rename(currentPath, newPath);

    }

    async deleteFile(filePath: string): Promise<void> {
    const targetPath = path.resolve(
        this.root,
        filePath
    );

    if (
        !targetPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.unlink(targetPath);
    
    }

    async saveFile(filePath: string, content: string): Promise<void> {
    const targetPath = path.resolve(
        this.root,
        filePath
    );

    if (
        !targetPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.writeFile(targetPath, content, "utf8");

    }

    async moveFile(
    filePath: string,
    newPath: string,
    newName: string
    ): Promise<void> {
    const currentPath = path.resolve(
        this.root,
        filePath
    );

    const targetPath = path.resolve(
        this.root,
        newPath,
        newName
    );

    if (
        !currentPath.startsWith(this.root + path.sep) ||
        !targetPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    await fs.rename(currentPath, targetPath);

    }

    async readDirectory(
    folderName: string | null,
    parentPath: string
): Promise<{
    name: string;
    type: "file" | "directory";
    parent: string | null;
}[]> {

    const folderPath = folderName
        ? path.resolve(this.root, parentPath, folderName)
        : path.resolve(this.root, parentPath);

    if (
        folderPath !== this.root &&
        !folderPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    const entries = await fs.readdir(folderPath, {
        withFileTypes: true
    });

    const parent = folderPath === this.root
        ? null
        : folderName;

    return entries.map(entry => ({
        name: entry.name,
        type: entry.isDirectory()
            ? "directory"
            : "file",
        parent
    }));
    
    }

    async readFile(filePath: string): Promise<{
    name: string;
    type: "file";
    parent: string;
    content: string;
}> {

    const targetPath = path.resolve(
        this.root,
        filePath
    );

    if (
        !targetPath.startsWith(this.root + path.sep)
    ) {
        throw new Error("Invalid path");
    }

    const content = await fs.readFile(
        targetPath,
        "utf8"
    );

    return {
        name: path.basename(targetPath),
        type: "file",
        parent: path.basename(path.dirname(targetPath)),
        content
    };
    
    }
}