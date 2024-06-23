#!/usr/bin/swift

import Foundation

class SocketClient {
    var socketFD: Int32 = -1

    func createSocket() {
        socketFD = socket(AF_INET, SOCK_STREAM, 0)
        guard socketFD >= 0 else {
            print("Error creating socket")
            return
        }

        var serverAddress = sockaddr_in()
        serverAddress.sin_family = sa_family_t(AF_INET)
        serverAddress.sin_port = UInt16(40849).bigEndian
        serverAddress.sin_addr.s_addr = inet_addr("10.4.16.141")

        var addr = sockaddr()
        memcpy(&addr, &serverAddress, MemoryLayout<sockaddr_in>.size)
        let connectResult = withUnsafePointer(to: &addr) {
            $0.withMemoryRebound(to: sockaddr.self, capacity: 1) {
                connect(socketFD, $0, socklen_t(MemoryLayout<sockaddr_in>.size))
            }
        }

        if connectResult < 0 {
            print("Error connecting to socket")
            return
        }
    }

    func receiveData() {
        while true {
            var buffer = [UInt8](repeating: 0, count: 1024)
            let bytesRead = read(socketFD, &buffer, 1024)
            if bytesRead > 0 {
                print("Received data: \(String(bytes: buffer, encoding: .utf8) ?? "")")
            } else if bytesRead == 0 {
                print("Connection closed by remote peer")
                break
            } else {
                print("Error reading from socket")
                break
            }
        }
    }

    deinit {
        close(socketFD)
    }
}

// Function to start the process
func main() {
    let client = SocketClient()
    client.createSocket()
    client.receiveData()
}

main() // Call main() function
