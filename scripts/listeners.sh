#!/bin/bash
# Start multiple listeners for reverse shell practice
# Usage: ./listeners.sh [start|stop|status]

LISTENER_PORTS=(4444 5555 6666 7777 8888 9999)
LISTENER_DIR="/tmp/drakonix_listeners"
PID_FILE="$LISTENER_DIR/pids.txt"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

start_listeners() {
    echo -e "${GREEN}[*] Starting reverse shell listeners...${NC}"

    mkdir -p "$LISTENER_DIR"

    for port in "${LISTENER_PORTS[@]}"; do
        # Check if port is in use
        if lsof -i :"$port" >/dev/null 2>&1; then
            echo -e "${YELLOW}[!] Port $port already in use, skipping${NC}"
            continue
        fi

        # Start netcat listener in background
        nc -lvnp "$port" > "$LISTENER_DIR/port_$port.log" 2>&1 &
        local pid=$!
        echo "$pid:$port" >> "$PID_FILE"
        echo -e "${GREEN}[+] Listening on port $port (PID: $pid)${NC}"
    done

    echo ""
    echo -e "${GREEN}[*] All listeners started!${NC}"
    echo -e "${YELLOW}[*] Logs directory: $LISTENER_DIR${NC}"
    echo -e "${YELLOW}[*] Use './listeners.sh status' to see active shells${NC}"
}

stop_listeners() {
    echo -e "${RED}[*] Stopping all listeners...${NC}"

    if [[ ! -f "$PID_FILE" ]]; then
        echo -e "${YELLOW}[!] No PID file found${NC}"
        return
    fi

    while IFS=: read -r pid port; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo -e "${RED}[-] Stopped listener on port $port (PID: $pid)${NC}"
        fi
    done < "$PID_FILE"

    rm -f "$PID_FILE"
    echo -e "${GREEN}[*] All listeners stopped${NC}"
}

status_listeners() {
    echo -e "${GREEN}[*] Active listeners:${NC}"
    echo ""

    local found=false

    for port in "${LISTENER_PORTS[@]}"; do
        local pid=$(lsof -ti :"$port")
        if [[ -n "$pid" ]]; then
            echo -e "${GREEN}[+] Port $port${NC} - PID: $pid"
            found=true
        fi
    done

    if [[ "$found" == false ]]; then
        echo -e "${YELLOW}[!] No active listeners found${NC}"
    fi

    echo ""
    echo -e "${YELLOW}[*] Recent connection logs:${NC}"
    if [[ -d "$LISTENER_DIR" ]]; then
        for logfile in "$LISTENER_DIR"/port_*.log; do
            if [[ -f "$logfile" && -s "$logfile" ]]; then
                echo -e "${GREEN}$(basename "$logfile"):${NC}"
                tail -3 "$logfile" | sed 's/^/    /'
            fi
        done
    fi
}

case "$1" in
    start)
        start_listeners
        ;;
    stop)
        stop_listeners
        ;;
    status)
        status_listeners
        ;;
    restart)
        stop_listeners
        sleep 1
        start_listeners
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start all listeners (ports: ${LISTENER_PORTS[*]})"
        echo "  stop    - Stop all listeners"
        echo "  status  - Show active listeners and recent connections"
        echo "  restart - Restart all listeners"
        exit 1
        ;;
esac
