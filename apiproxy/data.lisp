; this file specifies the data model for the API server
; it's done in lisp notation because lisp is the language the universe itself is written in

; no seriously, it is:
; https://en.wikipedia.org/wiki/Lambda_calculus
; https://en.wikipedia.org/wiki/Church%E2%80%93Turing%E2%80%93Deutsch_principle
(
(trending_tags (summary "Currently trending tags")
               (description "Returns the currently trending tags at time of call")
               (update_frequency 240)
               (max_datums 10)
               (rpc_method get_trending_tags ("" !count)))

(blocks (summary "Recent blocks")
        (description "Returns up to the last 10 blocks")
        (update_frequency -1)
        (max_datums 10)
	(custom_handler get_recent_blocks))

(block (summary "Block data")
       (description "Returns a single block's data")
       (update_frequency -1)
       (unique_id name)
       (rpc_method get_smoke_block (!id)))

(witnesses (summary "List of witnesses")
           (description "Returns the current list of witnesses, both active and backup")
           (update_frequency 240)
           (max_datums 100)
           (rpc_method get_witnesses ("0" !count)))

(witness (summary "Witness data")
         (description "Returns data about a specific individual witness")
         (update_frequency 240)
         (unique_id name)
         (rpc_method get_witness_data (!id)))

(account (summary "Account data")
         (description "Returns acount data about a specific individual account")
         (update_frequency 60)
         (unique_id name)
         (rpc_method get_user_data (!id)))

(posts (summary "Posts")
       (description "Get a list of posts for a specific user")
       (update_frequency 240)
       (max_datums 10)
       (unique_id name)
       (single_field permlink)
       (custom_handler get_blog_posts))

;(post (description "Get an individual post")
;      (update_frequency 240)
;      (unique_ids (username post))
;      (rpc_method get_user_post))

(network (summary "Network data")
         (description "Returns various bits of data about the current network state and blockchain configuration")
         (update_frequency 240)
         (max_datums 1)
         (rpc_method get_network_data ()))
)
