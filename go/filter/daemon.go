package daemon

import (
  //"flag"
  "log"
  "fmt"
  "os"
  "time"
  "strings"
  "encoding/json"
  "github.com/darkhelmet/twitterstream"
  "github.com/garyburd/redigo/redis"
)


var (
    wait           = 1
    maxWait        = 600 // Seconds

    // global to store redis connection
    c redis.Conn

    trimThreshold = 100
    trimCount     = 0
)


type Tweet struct {
  Username string `json:"username"`
  Name string `json:"name"`
  Profile_image_url string `json:"profile_image_url"`
  Text string `json:"text"`
  Userid uint64 `json:"userid"`
  Id string `json:"id"`
  Received_at  int64 `json:"received_at"`
}

func trimTweets(){
    _, err := c.Do("LTRIM", "tweets", 0, 20)
    if (err != nil) {
        log.Printf("failed to LTRIM %s", err)
        return
    }
}

func pushToRedis(tweet *twitterstream.Tweet){
    t := Tweet{
        Username: tweet.User.ScreenName,
        Profile_image_url: tweet.User.ProfileImageUrl,
        Text: tweet.Text,
        Id: tweet.IdString,
        Received_at: time.Now().Unix(),
    }

    trimCount += 1

    if trimCount >= trimThreshold {
        trimCount = 0
        trimTweets()
    }

    fmt.Println(t.Text)
    fmt.Println("\t", t.Username, t.Received_at, "\n")

    jsonned, err := json.Marshal(t)

    if (err != nil) {
        log.Printf("failed to json.Marshall: %s", err)
        return
    }
    _, rerr := c.Do("LPUSH", "tweets", jsonned)
    if (rerr != nil) {
        log.Printf("failed to LPUSH %s", err)
        return
    }

}


func decodeTweets(conn *twitterstream.Connection, messages <-chan bool) bool {
    stopMsg := false
    for !stopMsg {
        select {
            case stopMsg = <-messages:
                log.Printf("got stop message")
                break;
            default:
                if tweet, err := conn.Next(); err == nil {
                    if(tweet.InReplyToScreenName == nil  && len(tweet.Text) > 0  && !strings.Contains(tweet.Text, "@") && strings.HasSuffix(tweet.Text, "?")) {
                        pushToRedis(tweet)
                        //time.Sleep(time.Duration(5 * time.Second))
                    }

                } else {
                    log.Printf("decoding tweet failed: %s", err)
                    conn.Close()
                }
        }
    }

    log.Printf("here1")
    return true
}

func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}

func StreamTweets(messages <-chan bool) {
    var err error

    c, err = redis.Dial("tcp", ":6379")
    if err != nil {
        panic(err)
    }

    c.Do("AUTH", "foobared")

    trimThreshold, err = redis.Int(c.Do("LLEN", "tweets"))
    if (err != nil) {
        fmt.Println("Some error occured")
    }

    if trimThreshold >= trimCount {
        trimTweets()
    }

    consumerKey:= os.Getenv("CONSUMERKEY")
    consumerSecret:= os.Getenv("CONSUMERSECRET")
    accessToken :=  os.Getenv("ACCESSTOKEN")
    accessSecret := os.Getenv("ACCESSSECRET")

    keywords := "why,when,how,then"

    client := twitterstream.NewClient(consumerKey, consumerSecret, accessToken, accessSecret)
    for {
        log.Printf("tracking keywords %s", keywords)
        conn, err := client.Track(keywords)
        if err != nil {
            log.Printf("tracking failed: %s", err)
            wait = wait << 1
            log.Printf("waiting for %d seconds before reconnect", min(wait, maxWait))
            time.Sleep(time.Duration(min(wait, maxWait)) * time.Second)
            continue
        } else {
            wait = 1
        }
        stop := decodeTweets(conn, messages)


        if stop {
            log.Printf("stopping")
            break
        }
    }
}
