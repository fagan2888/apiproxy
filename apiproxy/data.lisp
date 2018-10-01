; this file specifies the data model for the API server
; it's done in lisp notation because lisp is the language the universe itself is written in

; no seriously, it is:
; https://en.wikipedia.org/wiki/Lambda_calculus
; https://en.wikipedia.org/wiki/Church%E2%80%93Turing%E2%80%93Deutsch_principle
(
(trending_tags (description "The currently trending tags at time of call")
               (update_frequency 240)
               (max_datums 10)
               (unique_id name)
               (rpc_method get_trending_tags ("" !count)))

(blocks (description "Raw blockchain data")
        (update_frequency -1)
        (max_datums 10)
        (unique_id block_id)
        (rpc_method get_smoke_block (!count)))

(witnesses (description "Witness data")
           (update_frequency 240)
           (max_datums 20)
           (unique_id name)
           (rpc_method get_witnesses ("0" !count)))

)
