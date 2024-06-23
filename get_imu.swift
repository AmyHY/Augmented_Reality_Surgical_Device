import Foundation

// Create a TCP/IP socket
let clientSocket = try! Socket.create()
try! clientSocket.connect(to: "Jetson_Nano_IP", port: 12345)

while true {
    // Receive IMU data from the server
    let data = try! clientSocket.read()

    // Parse JSON data received from server
    if let imuData = try? JSONDecoder().decode(IMUData.self, from: data) {
        // Process the received IMU data
        print("Received IMU Data:")
        print("X Acceleration: \(imuData.x_accel)")
        print("Y Acceleration: \(imuData.y_accel)")
        print("Z Acceleration: \(imuData.z_accel)")
    }
}

// Close the socket when done
clientSocket.close()
