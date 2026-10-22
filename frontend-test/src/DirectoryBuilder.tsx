import { useState } from "react";

export type DirectoryEntry = {
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

function ChevronIcon({ open }: { open: boolean }) {
    return (
        <svg
            viewBox="0 0 16 16"
            className={`h-3 w-3 shrink-0 text-zinc-400 transition-transform duration-150 ${
                open ? "rotate-90" : ""
            }`}
            fill="none"
            stroke="currentColor"
            strokeWidth={1.75}
            strokeLinecap="round"
            strokeLinejoin="round"
        >
            <path d="M6 4l4 4-4 4" />
        </svg>
    );
}

function FolderIcon({ open }: { open: boolean }) {
    return (
        <svg
            viewBox="0 0 20 20"
            className={`h-4 w-4 shrink-0 ${
                open ? "text-teal-600" : "text-zinc-400"
            }`}
            fill="currentColor"
        >
            <path d="M2 5.75A1.75 1.75 0 0 1 3.75 4h3.69c.46 0 .9.18 1.238.516l1.06 1.06c.14.14.328.22.525.22H16.25A1.75 1.75 0 0 1 18 7.55v7.2A1.75 1.75 0 0 1 16.25 16.5H3.75A1.75 1.75 0 0 1 2 14.75V5.75Z" />
        </svg>
    );
}

function FileIcon() {
    return (
        <svg
            viewBox="0 0 20 20"
            className="h-4 w-4 shrink-0 text-zinc-400"
            fill="none"
            stroke="currentColor"
            strokeWidth={1.4}
            strokeLinejoin="round"
        >
            <path d="M5 2.75h5L15 7v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3.75a1 1 0 0 1 1-1Z" />
            <path d="M10 2.75V6a1 1 0 0 0 1 1h4" />
        </svg>
    );
}

export default function DirectoryBuilder({
    entries,
    onFolderOpen
}: DirectoryBuilderProps) {

    const [openFolders, setOpenFolders] = useState<Set<string>>(
        new Set()
    );

    const [selectedPath, setSelectedPath] = useState<string | null>(
        null
    );

    const toggleFolder = (
        folderName: string,
        parentPath: string
    ) => {

        const folderPath = parentPath
            ? `${parentPath}/${folderName}`
            : folderName;

        setSelectedPath(folderPath);

        setOpenFolders(previous => {

            const next = new Set(previous);

            if (next.has(folderPath)) {
                next.delete(folderPath);
            } else {
                next.add(folderPath);

                onFolderOpen(
                    folderName,
                    parentPath
                );
            }

            return next;
        });
    };

    const selectFile = (filePath: string) => {
        setSelectedPath(filePath);
    };

    const renderDirectory = (
        parent: string | null,
        parentPath = ""
    ): React.ReactNode => {

        const children = entries
            .filter(entry => entry.parent === parent)
            .slice()
            .sort((a, b) => {
                if (a.type !== b.type) {
                    return a.type === "directory" ? -1 : 1;
                }
                return a.name.localeCompare(b.name);
            });

        return (
            <div className="flex flex-col gap-px">
                {children.map(entry => {

                    const currentPath = parentPath
                        ? `${parentPath}/${entry.name}`
                        : entry.name;

                    const isSelected =
                        selectedPath === currentPath;

                    if (entry.type === "file") {

                        return (
                            <div
                                key={currentPath}
                                onClick={() =>
                                    selectFile(currentPath)
                                }
                                className={`
                                    flex h-[30px] items-center gap-2
                                    rounded-md px-2 text-[13px]
                                    font-mono tracking-tight
                                    cursor-pointer select-none
                                    transition-colors duration-100
                                    ${
                                        isSelected
                                            ? "bg-teal-50 text-teal-900 font-medium"
                                            : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                                    }
                                `}
                            >
                                <FileIcon />
                                <span className="truncate">
                                    {entry.name}
                                </span>
                            </div>
                        );
                    }

                    const isOpen =
                        openFolders.has(currentPath);

                    return (
                        <div key={currentPath}>

                            <div
                                onClick={() =>
                                    toggleFolder(
                                        entry.name,
                                        parentPath
                                    )
                                }
                                className={`
                                    flex h-[30px] items-center gap-1.5
                                    rounded-md px-2 text-[13px]
                                    font-mono tracking-tight
                                    cursor-pointer select-none
                                    transition-colors duration-100
                                    ${
                                        isSelected
                                            ? "bg-zinc-100 text-zinc-900 font-medium"
                                            : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                                    }
                                `}
                            >
                                <ChevronIcon open={isOpen} />
                                <FolderIcon open={isOpen} />
                                <span className="truncate">
                                    {entry.name}
                                </span>
                            </div>

                            {isOpen && (
                                <div className="ml-[11px] border-l border-zinc-200 pl-[10px]">
                                    {renderDirectory(
                                        entry.name,
                                        currentPath
                                    )}
                                </div>
                            )}

                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <div className="w-full px-2">
            {renderDirectory(null)}
        </div>
    );
}