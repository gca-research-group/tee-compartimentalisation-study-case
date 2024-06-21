# Memory Information
echo "Total Physical Memory (RAM):"
sysctl hw.physmem

# Processor Information
echo "Processor Model:"
sysctl hw.model

echo "Number of CPUs:"
sysctl hw.ncpu

echo "Detailed Processor Information:"
dmesg | grep -i cpu

# Operating System Information
echo "Operating System Version:"
uname -r

echo "Operating System Name:"
uname -s

echo "Host Name:"
uname -n

echo "Complete Operating System Information:"
uname -a

