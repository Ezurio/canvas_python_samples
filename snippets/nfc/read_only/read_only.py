"""This example demonstrates how to setup the NFC tag with a text record and a URL/URI record.
The tag is in read-only mode.
The following mobile app is recommended for testing reading and writing to the NFC tag:
Android:
https://play.google.com/store/apps/details?id=com.wakdev.wdnfc&pcampaignid=web_share
iOS:
https://apps.apple.com/us/app/nfc-tools/id1252962749
"""

import canvas

# Create a records list with a text record
records = [{'id': b'', 'type': b'T', 'tnf': 1,
            'payload': b'\x02enI\xe2\x80\x99m an NFC tag!'}]

# Add an URL/URI record
records.append({'id': b'', 'type': b'U', 'tnf': 1,
                'payload': b'\x04google.com'})

tag = canvas.NFCTag(256, records)

