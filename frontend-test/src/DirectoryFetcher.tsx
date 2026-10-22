import { useEffect, useState } from "react";
import DirectoryBuilder, {
    type DirectoryEntry
} from "./DirectoryBuilder";

export default function DirectoryFetcher() {

    const [entries, setEntries] = useState<DirectoryEntry[]>([]);
    const [loadedDirectories, setLoadedDirectories] =
        useState<Set<string>>(new Set());

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

        // Don't request a directory that has already been loaded
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

            setEntries(previous => {

                const existing = new Set(
                    previous.map(entry =>
                        `${entry.parent}/${entry.name}`
                    )
                );

                const newEntries = directory.filter(
                    entry =>
                        !existing.has(
                            `${entry.parent}/${entry.name}`
                        )
                );

                return [
                    ...previous,
                    ...newEntries
                ];
            });

            setLoadedDirectories(previous => {

                const next = new Set(previous);

                next.add(directoryKey);

                return next;
            });

        } catch (error) {

            console.error(
                "Failed to fetch directory:",
                error
            );
        }
    };

    // Load the root directory when the sidebar starts
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