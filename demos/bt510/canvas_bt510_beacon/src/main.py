app_id = 'canvas_bt510_beacon'
app_ver = '1.0.0'

from app import App

print('\r\n\r\nStarting app: %s v%s\r\n' % (app_id, app_ver))
app = App()
app.start()
