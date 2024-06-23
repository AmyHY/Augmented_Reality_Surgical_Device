from subprocess import call
import paramiko

call(["scp", "-r", "team69@10.4.16.141:~/Documents/csi-camera-capture/dedinside/", "./Images/"])
