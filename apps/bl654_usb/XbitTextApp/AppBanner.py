#
# Banner
#
# Utility functions to print an application banner with a colorful background
#
class Banner:
    def printCanvasLine():
        lineColors = [[24, 112, 239],[36, 103, 237],[55, 88, 233],[87, 63, 227],[108, 45, 223],[127, 23, 217],[152, 12, 215],[166, 1, 213]]
        fgbg = lambda text, fgr, fgg, fgb, bgr, bgg, bgb: "\033[38;2;" + str(fgr) + ";" + str(fgg) + ";" + str(fgb) + "m" + "\033[48;2;" + str(bgr) + ";" + str(bgg) + ";" + str(bgb) + "m" + text + "\33[0;0m"
        lineText = ''
        for i in range(0, 8):
            lineText += fgbg('~~~~~', lineColors[i][0], lineColors[i][1], lineColors[i][2], 43, 49, 54)
        print(lineText)

    def printBanner(text, fg):
        fgbg = lambda text, fgr, fgg, fgb, bgr, bgg, bgb: "\033[38;2;" + str(fgr) + ";" + str(fgg) + ";" + str(fgb) + "m" + "\033[48;2;" + str(bgr) + ";" + str(bgg) + ";" + str(bgb) + "m" + text + "\33[0;0m"
        bannerWidth = 40
        text = text[:bannerWidth]
        pad = " " * ((bannerWidth - len(text))//2)
        centeredText = pad + text + pad
        if(len(centeredText) % 2 != 0):
            centeredText += " "
        print(fgbg(centeredText, fg, fg, fg, 43, 49, 54))

    # Print the application name and version
    def printAppBanner(app_id, app_ver):
        print('')
        Banner.printCanvasLine()
        Banner.printBanner(app_id + ' ' + app_ver, 255)
        Banner.printBanner('Canvas Software Suite', 128)
        Banner.printCanvasLine()
    
Banner.printCanvasLine = staticmethod(Banner.printCanvasLine)
Banner.printBanner = staticmethod(Banner.printBanner)
Banner.printAppBanner = staticmethod(Banner.printAppBanner)
