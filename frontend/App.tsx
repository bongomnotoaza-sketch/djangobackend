import React from "react";
import DirectoryFetcher from "./DirectoryFetcher";

export default function App() {
    return (
        <aside
            style={{
                width: "300px",
                height: "100vh",
                borderRight: "1px solid #ccc",
                padding: "10px",
                boxSizing: "border-box"
            }}
        >
            <DirectoryFetcher />
        </aside>
    );
}