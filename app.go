package main

import (
    "fmt"
    "net/http"
    //"encoding/json"
    "github.com/gorilla/mux"
    "github.com/garyburd/redigo/redis"
)

// global to store redis connection
var c redis.Conn

func LatestHandler(w http.ResponseWriter, r *http.Request) {

    tweets, err := redis.Strings(c.Do("LRANGE", "tweets", 0, 15))
    if (err != nil) {
        fmt.Println("Some error occured")
    }

    // Parse/Unmarshall tweets
    fmt.Printf("%T\n", tweets)
    w.Header().Add("Content-Type", "application/json")

    for _, tweet := range tweets {
        fmt.Println(tweet)
        fmt.Fprintf(w, tweet)
    }

    //b, err := json.Marshal(tweets)

    //if (err != nil){
        //fmt.Println("here")
    //}

    //defer c.Close()
}

func main() {

    var err error

    c, err = redis.Dial("tcp", ":6379")
    if err != nil {
        panic(err)
    }

    r := mux.NewRouter()
    r.HandleFunc("/latest", LatestHandler).Methods("GET")

    http.Handle("/", r)
    fmt.Println("listening")
    http.ListenAndServe(":8080", nil)

}
