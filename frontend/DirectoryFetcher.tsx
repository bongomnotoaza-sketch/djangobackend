import React, { useEffect, useState } from "react";
import DirectoryBuilder from "./DirectoryBuilder";

type DirectoryEntry = {
    name: string;
    type: "file" | "directory";
    parent: string | null;
};

export default function DirectoryFetcher() {
    const [entries, setEntries] = useState<DirectoryEntry[]>([]);
    const [loadedDirectories, setLoadedDirectories] = useState<Set<string>>(
        new Set()
    );

    const fetchDirectory = async (
        folderName: string | null,
        parentPath: string
    ) => {
        const directoryKey =
            folderName === null
                ? ""
                : parentPath
                    ? `${parentPath}/${folderName}`
                    : folderName;

        if (loadedDirectories.has(directoryKey)) {
            return;
        }

        try {
            const params = new URLSearchParams();

            if (folderName !== null) {
                params.set("name", folderName);
                params.set("path", parentPath);
            }

            const response = await fetch(
                `http://localhost:3005/api/folders?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error(
                    `Failed to fetch directory: ${response.status}`
                );
            }

            const directory: DirectoryEntry[] =
                await response.json();

            setEntries(previous => [
                ...previous,
                ...directory
            ]);

            setLoadedDirectories(previous => {
                const next = new Set(previous);
                next.add(directoryKey);
                return next;
            });

        } catch (error) {
            console.error("Directory fetch failed:", error);
        }
    };

    useEffect(() => {
        fetchDirectory(null, "");
    }, []);

    return (
        <DirectoryBuilder
            entries={entries}
            onFolderOpen={fetchDirectory}
        />
    );
}