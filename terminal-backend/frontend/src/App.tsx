import { useEffect, useRef } from "react"
import { Terminal } from "@xterm/xterm"
import { FitAddon } from "@xterm/addon-fit"

import "@xterm/xterm/css/xterm.css"


function App() {
  const terminalRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!terminalRef.current) {
      return
    }

    const terminal = new Terminal({
      cursorBlink: true,
      fontFamily: "monospace",
      fontSize: 15,

      theme: {
        background: "#000000",
        foreground: "#00ff66",
        cursor: "#00ff66",

        black: "#000000",
        green: "#00ff66",
        brightGreen: "#00ff66",
      },
    })

    const fitAddon = new FitAddon()

    terminal.loadAddon(fitAddon)
    terminal.open(terminalRef.current)

    fitAddon.fit()

    const socket = new WebSocket(
      `ws://${window.location.hostname}:4000/terminal`
    )

    socket.binaryType = "arraybuffer"

    socket.onopen = () => {
      terminal.write(
        "\r\n\x1b[32mConnected to Ubuntu terminal\x1b[0m\r\n\r\n"
      )
    }

    socket.onmessage = (event) => {
      if (event.data instanceof ArrayBuffer) {
        const data = new Uint8Array(event.data)
        terminal.write(data)
      } else {
        terminal.write(event.data)
      }
    }

    socket.onerror = () => {
      terminal.write(
        "\r\n\x1b[31mWebSocket connection error\x1b[0m\r\n"
      )
    }

    socket.onclose = () => {
      terminal.write(
        "\r\n\x1b[31mConnection closed\x1b[0m\r\n"
      )
    }

    terminal.onData((data) => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(data)
      }
    })

    const handleResize = () => {
      fitAddon.fit()
    }

    window.addEventListener("resize", handleResize)

    return () => {
      window.removeEventListener("resize", handleResize)

      socket.close()
      terminal.dispose()
    }
  }, [])

  return (
    <div className="w-screen h-screen bg-black flex flex-col overflow-hidden">

      {/* Green top strip */}
      <div className="h-1 bg-green-500 shrink-0" />

      {/* Terminal */}
      <div
        ref={terminalRef}
        className="flex-1 min-w-0 min-h-0 w-full p-3 overflow-hidden"
      />

    </div>
  )
}

export default App