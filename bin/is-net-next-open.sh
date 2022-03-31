#!/bin/bash

# check if net-next is open
curl http://vger.kernel.org/~davem/net-next.html 2>/dev/null | grep "net-next is CLOSED" > /dev/null && echo "net-next is closed :(" || echo "net-next is open :)"
