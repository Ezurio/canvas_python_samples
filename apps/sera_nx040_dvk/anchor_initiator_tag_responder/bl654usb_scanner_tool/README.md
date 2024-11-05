# UWB Anchor Initiator/Tag Responder BLE Scanning Tool
The uwb_scanner.py script can be programmed onto a BL654 USB adapter (or similar) running Canvas firmware to scan for nearby Sera NX040 DVK boards running the "Anchor Initiator/Tag Responder" application script and repeatedly display a simple JSON object indicating range data between "Tags" and "Anchors" in the system.

# Getting Started
Copy the `uwb_scanner.py` file to the BL654 USB adapter using Xbit VS Code extension or similar tools. Rename the script to `main.py` and restart or remove/re-instart the USB adapter. If the corresponding USB-Serial port is opened in a terminal application (115200 baud, 8N1), the REPL console should display a continuous stream of JSON objects similar to seen below indicating the "local tag" short address followed by key/value pairs for each "Anchor" short address and distance to each (in cm).

```
{"local":"b015","ebcd":113,"6f95":153,"562a":140,"3367":144}
{"local":"b015","ebcd":122,"6f95":153,"562a":140,"3367":139}
{"local":"b015","ebcd":121,"6f95":157,"562a":140,"3367":142}
{"local":"b015","ebcd":118,"6f95":157,"562a":140,"3367":142}
{"local":"b015","ebcd":119,"6f95":156,"562a":139,"3367":144}
{"local":"b015","ebcd":113,"6f95":156,"562a":139,"3367":144}
{"local":"b015","ebcd":120,"6f95":155,"562a":139,"3367":140}
{"local":"b015","ebcd":118,"6f95":155,"562a":139,"3367":141}
{"local":"b015","ebcd":120,"6f95":155,"562a":138,"3367":138}
{"local":"b015","ebcd":121,"6f95":155,"562a":138,"3367":138}
{"local":"b015","ebcd":120,"6f95":158,"562a":138,"3367":140}
{"local":"b015","ebcd":117,"6f95":158,"562a":138,"3367":140}
{"local":"b015","ebcd":117,"6f95":155,"562a":141,"3367":142}
{"local":"b015","ebcd":123,"6f95":155,"562a":141,"3367":141}
```