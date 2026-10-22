const { useState, useEffect } = React;
const { createRoot } = ReactDOM;

function DirectoryBuilder() {

    const [entries, setEntries] = useState([]);
    const [openFolders, setOpenFolders] = useState(new Set());
    const [loadedDirectories, setLoadedDirectories] = useState(new Set());

    useEffect(() => {
        fetchDirectory(null, "");
    }, []);

    async function fetchDirectory(folderName, parentPath) {

        const directoryKey =
            folderName === null
                ? ""
                : parentPath
                    ? `${parentPath}/${folderName}`
                    : folderName;

        // Already loaded
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
                    `HTTP ${response.status}`
                );
            }

            const directory = await response.json();

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
                "Directory fetch failed:",
                error
            );
        }
    }

    function toggleFolder(
        folderName,
        parentPath
    ) {

        const key = parentPath
            ? `${parentPath}/${folderName}`
            : folderName;

        setOpenFolders(previous => {

            const next = new Set(previous);

            if (next.has(key)) {

                next.delete(key);

            } else {

                next.add(key);

                fetchDirectory(
                    folderName,
                    parentPath
                );
            }

            return next;
        });
    }

    function renderDirectory(
        parent,
        parentPath = "",
        level = 0
    ) {

        const children = entries.filter(
            entry => entry.parent === parent
        );

        return children.map(entry => {

            const currentPath = parentPath
                ? `${parentPath}/${entry.name}`
                : entry.name;

            if (entry.type === "file") {

                return React.createElement(
                    "div",
                    {
                        key: currentPath,
                        className: "file",
                        style: {
                            paddingLeft:
                                `${level * 20}px`
                        }
                    },
                    `📄 ${entry.name}`
                );
            }

            const isOpen =
                openFolders.has(currentPath);

            return React.createElement(
                "div",
                {
                    key: currentPath
                },

                React.createElement(
                    "div",
                    {
                        className: "folder",
                        style: {
                            paddingLeft:
                                `${level * 20}px`
                        },
                        onClick: () =>
                            toggleFolder(
                                entry.name,
                                parentPath
                            )
                    },

                    `${isOpen ? "▾" : "▸"} 📁 ${entry.name}`
                ),

                isOpen &&
                    React.createElement(
                        "div",
                        {
                            className: "children"
                        },

                        renderDirectory(
                            entry.name,
                            currentPath,
                            level + 1
                        )
                    )
            );
        });
    }

    return React.createElement(
        "div",
        null,
        renderDirectory(null)
    );
}

createRoot(
    document.getElementById("sidebar")
).render(
    React.createElement(DirectoryBuilder)
);