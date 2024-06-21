# Memory Information
echo "Total Physical Memory (RAM):"
sysctl hw.physmem

echo "Used and Free Memory:"
top -d1 | head -n 10

# Processor Information
echo "Processor Model:"
sysctl hw.model

echo "Processor Frequency:"
sysctl hw.clockrate

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

