# Simple HTTP Server Snippet
This snippet implements a small HTTP server defined as the `SimpleHttpServer` class. The application joins a Wi-Fi network and starts the simple HTTP server to serve out static `.html` files from the local filesystem.

# Using this Snippet
Note this snippet requires both the `simple_http_server.py` and the `index.html` file to be copied to the Canvas device filesystem. You may also wish to create your own `.html` files to serve. As written, the simple HTTP server assumes it is serving out content of type `text/html`, so if you wish to serve other types of files you'll need to modify the `Content-Type` header of the corresponding `GET` request handler.

# Supported Boards
This snippet was originally designed for the Veda SL917 SoC Explorer board (brd2911a).
