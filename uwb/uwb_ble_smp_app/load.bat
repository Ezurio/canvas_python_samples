@echo off

mcumgr -c %1 fs upload ble_ad_flags.py /lfs1/ble_ad_flags.py
mcumgr -c %1 fs upload boot.py /lfs1/boot.py
mcumgr -c %1 fs upload config.py /lfs1/config.py
mcumgr -c %1 fs upload device_db.py /lfs1/device_db.py
mcumgr -c %1 fs upload main.py /lfs1/main.py
mcumgr -c %1 fs upload sync.py /lfs1/sync.py
mcumgr -c %1 fs upload util.py /lfs1/util.py
mcumgr -c %1 fs upload uwb_ble_advertiser.py /lfs1/uwb_ble_advertiser.py
mcumgr -c %1 fs upload uwb_ble_connect.py /lfs1/uwb_ble_connect.py
mcumgr -c %1 fs upload uwb_ble_scanner.py /lfs1/uwb_ble_scanner.py
mcumgr -c %1 fs upload uwb_manager.py /lfs1/uwb_manager.py
mcumgr -c %1 fs upload uwb_smp_client.py /lfs1/uwb_smp_client.py
mcumgr -c %1 fs upload uwb_smp_common.py /lfs1/uwb_smp_common.py
mcumgr -c %1 fs upload uwb_smp_server.py /lfs1/uwb_smp_server.py
