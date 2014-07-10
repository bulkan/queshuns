package main

import (
  "flag"
  "log"
  "time"
  "strings"
  "github.com/darkhelmet/twitterstream"
)


var (
    consumerKey    = flag.String("consumer-key", "", "consumer key")
    consumerSecret = flag.String("consumer-secret", "", "consumer secret")
    accessToken    = flag.String("access-token", "", "access token")
    accessSecret   = flag.String("access-secret", "", "access token secret")
    keywords       = flag.String("keywords", "", "keywords to track")
    wait           = 1
    maxWait        = 600 // Seconds
)


func decodeTweets(conn *twitterstream.Connection) {
    for {
        if tweet, err := conn.Next(); err == nil {
            if(tweet.InReplyToScreenName == nil  &&
               len(tweet.Text) > 0  &&
               !strings.Contains(tweet.Text, "@") &&
               strings.HasSuffix(tweet.Text, "?")) {

                log.Printf(tweet.Text)
            }
        } else {
            log.Printf("decoding tweet failed: %s", err)
            conn.Close()
            return
        }
    }
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}

func streamTweets() {
    client := twitterstream.NewClient(*consumerKey, *consumerSecret, *accessToken, *accessSecret)
    for {
        log.Printf("tracking keywords %s", *keywords)
        conn, err := client.Track(*keywords)
        if err != nil {
            log.Printf("tracking failed: %s", err)
            wait = wait << 1
            log.Printf("waiting for %d seconds before reconnect", min(wait, maxWait))
            time.Sleep(time.Duration(min(wait, maxWait)) * time.Second)
            continue
        } else {
            wait = 1
        }
        decodeTweets(conn)
    }
}


func main() {
    flag.Parse()

    if *consumerKey == "" || *consumerSecret == "" {
        log.Fatalln("consumer tokens left blank")
    }

    if *accessToken == "" || *accessSecret == "" {
        log.Fatalln("access tokens left blank")
    }

    if *keywords == "" {
        log.Fatalln("keywords left blank")
    }

    streamTweets()
}
