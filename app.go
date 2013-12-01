package main

import (
    "fmt"
    "net/http"
)


func latest(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "/latest handler")
}

func main() {
    http.HandleFunc("/latest", latest)
    http.ListenAndServe(":8080", nil)
}
