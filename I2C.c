#include <stdio.h> 
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

#define I2C_DEV "/dev/i2c-1"
#define I2C_ADDRESS 0x68

// Function to send a START condition
int i2c_start(int file) {
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    // Prepare the I2C message
    messages[0].addr = I2C_ADDRESS; // Address of the I2C device
    messages[0].flags = 0;           // No special flags for START
    messages[0].len = 0;             // No data to send, just START

    // Prepare the packet to be sent
    packets.msgs = messages;
    packets.nmsgs = 1;  // Number of messages in the packet (1 for START)

    // Send the packet with START condition
    if (ioctl(file, I2C_RDWR, &packets) < 0) {
        perror("Failed to send START condition");
        return -1;
    }

    return 0;
}

// Function to send a STOP condition
int i2c_stop(int file) {
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    // Prepare the I2C message
    messages[0].addr = I2C_ADDRESS;  // Address of the I2C device
    messages[0].flags = I2C_M_NOSTART; // Set flag for STOP without START
    messages[0].len = 0;              // No data to send, just STOP

    // Prepare the packet to be sent
    packets.msgs = messages;
    packets.nmsgs = 1;  // Number of messages in the packet (1 for STOP)

    // Send the packet with STOP condition
    if (ioctl(file, I2C_RDWR, &packets) < 0) {
        perror("Failed to send STOP condition");
        return -1;
    }

    return 0;
}

// Function to send a repeated START condition
int i2c_repeated_start(int file) {
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    // Prepare the I2C message
    messages[0].addr = I2C_ADDRESS;  // Address of the I2C device
    messages[0].flags = I2C_M_NOSTART; // Set flag for Repeated START
    messages[0].len = 0;              // No data to send, just Repeated START

    // Prepare the packet to be sent
    packets.msgs = messages;
    packets.nmsgs = 1;  // Number of messages in the packet (1 for Repeated START)

    // Send the packet with Repeated START condition
    if (ioctl(file, I2C_RDWR, &packets) < 0) {
        perror("Failed to send repeated START condition");
        return -1;
    }

    return 0;
}

int main() {
    int file;
    char filename[20];

    // Open the I2C device file
    snprintf(filename, 19, "%s", I2C_DEV);
    if ((file = open(filename, O_RDWR)) < 0) {
        perror("Failed to open the i2c bus");
        return 1;
    }

    // Send a START condition
    if (i2c_start(file) < 0) {
        return 1;
    }

    // Send a STOP condition
    if (i2c_stop(file) < 0) {
        return 1;
    }

    // Send a repeated START condition
    if (i2c_repeated_start(file) < 0) {
        return 1;
    }

    // Send a STOP condition again
    if (i2c_stop(file) < 0) {
        return 1;
    }

    // Close the I2C device file
    close(file);

    return 0;
}
