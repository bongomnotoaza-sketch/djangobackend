import React, { useState } from "react";

type DirectoryEntry = {
    name: string;
    type: "file" | "directory";
    parent: string | null;
};

type DirectoryBuilderProps = {
    entries: DirectoryEntry[];
    onFolderOpen: (
        folderName: string,
        parentPath: string
    ) => void;
};

export default function DirectoryBuilder({
    entries,
    onFolderOpen
}: DirectoryBuilderProps) {

    const [openFolders, setOpenFolders] = useState<Set<string>>(
        new Set()
    );

    const toggleFolder = (
        folderName: string,
        parentPath: string
    ) => {

        const folderKey = parentPath
            ? `${parentPath}/${folderName}`
            : folderName;

        setOpenFolders(previous => {

            const next = new Set(previous);

            if (next.has(folderKey)) {
                next.delete(folderKey);
            } else {
                next.add(folderKey);

                // Tell the fetcher that this folder was opened
                onFolderOpen(
                    folderName,
                    parentPath
                );
            }

            return next;
        });
    };

    const renderDirectory = (
        parent: string | null,
        parentPath: string = "",
        level: number = 0
    ): React.ReactNode => {

        const children = entries.filter(
            entry => entry.parent === parent
        );

        return children.map(entry => {

            const currentPath = parentPath
                ? `${parentPath}/${entry.name}`
                : entry.name;

            if (entry.type === "file") {
                return (
                    <div
                        key={currentPath}
                        style={{
                            paddingLeft: `${level * 20}px`
                        }}
                    >
                        📄 {entry.name}
                    </div>
                );
            }

            const isOpen = openFolders.has(currentPath);

            return (
                <div key={currentPath}>

                    <div
                        style={{
                            paddingLeft: `${level * 20}px`,
                            cursor: "pointer"
                        }}
                        onClick={() =>
                            toggleFolder(
                                entry.name,
                                parentPath
                            )
                        }
                    >
                        {isOpen ? "▾" : "▸"} 📁 {entry.name}
                    </div>

                    {isOpen &&
                        renderDirectory(
                            entry.name,
                            currentPath,
                            level + 1
                        )
                    }

                </div>
            );
        });
    };

    return (
        <div>
            {renderDirectory(null)}
        </div>
    );
}