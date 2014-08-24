package main

import (
    "log"
    "fmt"
    "net/http"
    "encoding/json"
    "github.com/gorilla/mux"
    "github.com/garyburd/redigo/redis"
    "github.com/googollee/go-socket.io"
    "./filter"
)

// global to store redis connection
var c redis.Conn

func LatestHandler(w http.ResponseWriter, r *http.Request) {

    tweet_strings, err := redis.Strings(c.Do("LRANGE", "tweets", 0, 15))
    if (err != nil) {
        fmt.Println("Some error occured")
    }

    // Unmarshall tweets
    fmt.Printf("%T\n", tweet_strings)
    w.Header().Add("Content-Type", "application/json")

    var tweets []daemon.Tweet

    for _, twit := range tweet_strings {
        var tweet daemon.Tweet

        if err := json.Unmarshal([]byte(twit), &tweet); err != nil {
            fmt.Println("Error parsing JSON: ", err)
        }

        fmt.Println(tweet)
        tweets = append(tweets, tweet)

    }

    json_tweets, err := json.Marshal(tweets)
    fmt.Fprintf(w, string(json_tweets))
}

func main() {

    var err error

    c, err = redis.Dial("tcp", ":6379")
    if err != nil {
        panic(err)
    }

    running := false

    server, err := socketio.NewServer(nil)
    if err != nil {
        log.Fatal(err)
    }

    messages := make(chan bool)

    server.On("connection", func(so socketio.Socket) {
        if !running {
            go daemon.StreamTweets(messages)
            running = true
        }
        log.Println("on connection")
        so.Join("tweets")
        so.On("disconnection", func() {
            messages <- true
            log.Println("on disconnect")
        })
    })
    server.On("error", func(so socketio.Socket, err error) {
        log.Println("error:", err)
    })

    r := mux.NewRouter()
    r.HandleFunc("/latest", LatestHandler).Methods("GET")
    r.PathPrefix("/socket.io/").Handler(server)
    r.PathPrefix("/").Handler(http.FileServer(http.Dir("./frontend")))

    http.Handle("/", r)
    fmt.Println("listening")
    http.ListenAndServe(":8080", nil)

}
