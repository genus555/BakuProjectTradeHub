package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type LogData struct {
	Level	string	`json:"level"`
	Message	string	`json:"message"`
	Details	string	`json:"details"`
}

func writeToFile(fn string, logText string) {
	f, err := os.OpenFile(fn, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Printf("Failed to write to file %s: %v", fn, err)
		return
	}
	defer f.Close()

	if _, err := f.WriteString(logText); err != nil {
		log.Printf("Failed to write text to %s: %v", fn, err)
	}
}

func logHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not alowed", http.StatusMethodNotAllowed)
		return
	}

	var data LogData
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	formattedLog := fmt.Sprintf("[%s] %s\n%s\n----------------------\n",
		data.Level,
		data.Message,
		data.Details,
	)
	writeToFile("go_all_logs.txt", formattedLog)
	if data.Level == "WARNING" || data.Level == "ERROR" || data.Level == "CRITICAL" {
		writeToFile("warning_logs.txt", formattedLog)
	}

	w.WriteHeader(http.StatusOK)
}

func main() {
	http.HandleFunc("/log", logHandler)
	log.Println("Listening to logs on http://localhost:8080...")
	log.Fatal(http.ListenAndServe(":8080", nil))
}