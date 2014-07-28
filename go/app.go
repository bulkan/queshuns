package main

import (
    "fmt"
    "net/http"
    "encoding/json"
    "github.com/gorilla/mux"
    "github.com/garyburd/redigo/redis"
)

type Tweet struct {
  Username string `json:"username"`
  Name string `json:"name"`
  Profile_image_url string `json:"profile_image_url"`
  Text string `json:"text"`
  Userid uint64 `json:"userid"`
  Id uint64 `json:"id"`
  Received_at float32 `json:"received_at"`
}

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

    var tweets []Tweet

    for _, twit := range tweet_strings {
        var tweet Tweet

        if err := json.Unmarshal([]byte(twit), &tweet); err != nil {
    		    fmt.Println("Error parsing JSON: ", err)
    	  }

        fmt.Println(tweet)
        tweets = append(tweets, tweet)

    }

    json_tweets, err := json.Marshal(tweets)
    fmt.Fprintf(w, string(json_tweets))

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
