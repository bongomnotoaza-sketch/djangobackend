import { useEffect, useState } from "react";

type DirectoryEntry = {
    name: string;
    type: "file" | "directory";
    parent: string | null;
};

// --- File icon badges, VS Code explorer style -------------------------

const FILE_BADGES: Record<
    string,
    { label: string; bg: string; text?: string }
> = {
    ts: { label: "TS", bg: "#3178c6" },
    tsx: { label: "TS", bg: "#3178c6" },
    js: { label: "JS", bg: "#f0db4f", text: "#1e1e1e" },
    jsx: { label: "JS", bg: "#f0db4f", text: "#1e1e1e" },
    json: { label: "{ }", bg: "#cbcb41", text: "#1e1e1e" },
    css: { label: "#", bg: "#2965f1" },
    html: { label: "<>", bg: "#e34c26" },
    md: { label: "M↓", bg: "#519aba" },
    py: { label: "PY", bg: "#3572a5" },
    yml: { label: "YML", bg: "#a0a0a0", text: "#1e1e1e" },
    yaml: { label: "YML", bg: "#a0a0a0", text: "#1e1e1e" }
};

function getExtension(name: string): string {
    const idx = name.lastIndexOf(".");
    if (idx <= 0) return "";
    return name.slice(idx + 1).toLowerCase();
}

function FileIcon({ name }: { name: string }) {

    const badge = FILE_BADGES[getExtension(name)];

    if (!badge) {
        return (
            <svg
                viewBox="0 0 20 20"
                className="h-3.5 w-3.5 shrink-0 text-[#8c8c8c]"
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

    return (
        <span
            className="flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded-[3px] text-[7px] font-bold leading-none"
            style={{
                backgroundColor: badge.bg,
                color: badge.text ?? "#ffffff"
            }}
        >
            {badge.label}
        </span>
    );
}

function ChevronIcon({ open }: { open: boolean }) {
    return (
        <svg
            viewBox="0 0 16 16"
            className={`h-3 w-3 shrink-0 text-[#c5c5c5] transition-transform duration-100 ${
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

// --- Sidebar ------------------------------------------------------------

export default function Sidebar() {

    const [entries, setEntries] = useState<DirectoryEntry[]>([]);
    const [loadedDirectories, setLoadedDirectories] =
        useState<Set<string>>(new Set());
    const [openFolders, setOpenFolders] =
        useState<Set<string>>(new Set());
    const [selectedPath, setSelectedPath] =
        useState<string | null>(null);

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

            setEntries(previous => {

                const existing = new Set(
                    previous.map(
                        entry => `${entry.parent}/${entry.name}`
                    )
                );

                const newEntries = directory.filter(
                    entry =>
                        !existing.has(
                            `${entry.parent}/${entry.name}`
                        )
                );

                return [...previous, ...newEntries];
            });

            setLoadedDirectories(previous => {
                const next = new Set(previous);
                next.add(directoryKey);
                return next;
            });

        } catch (error) {
            console.error("Failed to fetch directory:", error);
        }
    };

    useEffect(() => {
        fetchDirectory(null, "");
    }, []);

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
                fetchDirectory(folderName, parentPath);
            }

            return next;
        });
    };

    const selectFile = (filePath: string) => {
        setSelectedPath(filePath);
    };

    const renderDirectory = (
        parent: string | null,
        parentPath = "",
        level = 0
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

        return children.map(entry => {

            const currentPath = parentPath
                ? `${parentPath}/${entry.name}`
                : entry.name;

            const isSelected = selectedPath === currentPath;
            const indent = 8 + level * 12;

            if (entry.type === "file") {
                return (
                    <div
                        key={currentPath}
                        onClick={() => selectFile(currentPath)}
                        className={`flex h-[22px] cursor-pointer items-center gap-1.5 pr-2 text-[13px] ${
                            isSelected
                                ? "bg-[#37373d] text-white"
                                : "text-[#cccccc] hover:bg-[#2a2d2e]"
                        }`}
                        style={{ paddingLeft: `${indent + 15}px` }}
                    >
                        <FileIcon name={entry.name} />
                        <span className="truncate">
                            {entry.name}
                        </span>
                    </div>
                );
            }

            const isOpen = openFolders.has(currentPath);

            return (
                <div key={currentPath}>

                    <div
                        onClick={() =>
                            toggleFolder(entry.name, parentPath)
                        }
                        className={`flex h-[22px] cursor-pointer items-center gap-1 pr-2 text-[13px] ${
                            isSelected
                                ? "bg-[#37373d] text-white"
                                : "text-[#cccccc] hover:bg-[#2a2d2e]"
                        }`}
                        style={{ paddingLeft: `${indent}px` }}
                    >
                        <ChevronIcon open={isOpen} />
                        <span className="truncate">
                            {entry.name}
                        </span>
                    </div>

                    {isOpen &&
                        renderDirectory(
                            entry.name,
                            currentPath,
                            level + 1
                        )}

                </div>
            );
        });
    };

    return (
        <div className="flex h-full w-full flex-col overflow-hidden bg-[#252526] text-[#cccccc]">

            <div className="px-4 pb-1 pt-3">
                <span className="text-[11px] font-semibold uppercase tracking-wide text-[#bbbbbb]">
                    Explorer
                </span>
            </div>

            <div className="flex items-center gap-1 px-2 py-1 text-[11px] font-bold uppercase tracking-wide text-[#cccccc]">
                <ChevronIcon open />
                <span>Project</span>
            </div>

            <div className="flex-1 overflow-y-auto pb-4">
                {renderDirectory(null)}
            </div>

        </div>
    );
}