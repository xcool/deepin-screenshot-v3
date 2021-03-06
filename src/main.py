#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2014 Deepin, Inc.
#               2011 ~ 2014 Andy Stewart
# 
# Author:     Andy Stewart <lazycat.manatee@gmail.com>
# Maintainer: Andy Stewart <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
if os.name == 'posix':
    QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads, True)
    
from PyQt5.QtQuick import QQuickView
from PyQt5.QtGui import QSurfaceFormat, QColor, QGuiApplication, qRed, qGreen, qBlue
from PyQt5 import QtCore, QtQuick

import sys
from PyQt5.QtWidgets import QApplication, qApp
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtGui
import signal
from window_info import WindowInfo
from PyQt5.QtDBus import QDBusConnection, QDBusInterface

class Window(QQuickView):

    def __init__(self):
        QQuickView.__init__(self)
        
        surface_format = QSurfaceFormat()
        surface_format.setAlphaBufferSize(8)
        
        self.setColor(QColor(0, 0, 0, 0))
        self.setFlags(QtCore.Qt.FramelessWindowHint)
        self.setResizeMode(QtQuick.QQuickView.SizeRootObjectToView)
        self.setFormat(surface_format)
        
        self.qml_context = self.rootContext()
        
        self.qpixmap = QGuiApplication.primaryScreen().grabWindow(0)
        self.qpixmap.save("/tmp/deepin-screenshot.png")
        self.qimage = self.qpixmap.toImage()
        
        self.window_info = WindowInfo()
        
    @pyqtSlot(int, int, result="QVariant")    
    def get_color_at_point(self, x, y):
        rgb = self.qimage.pixel(x, y)
        return [qRed(rgb), qGreen(rgb), qBlue(rgb)]
        
    @pyqtSlot(result="QVariant")    
    def get_window_info_at_pointer(self):
        return self.window_info.get_window_info_at_pointer()
    
    @pyqtSlot(result="QVariant")    
    def get_cursor_pos(self):
        return QtGui.QCursor.pos()        
            
    @pyqtSlot()    
    def enable_zone(self):
        try:
            iface = QDBusInterface("com.deepin.daemon.Zone", "/com/deepin/daemon/Zone", '', QDBusConnection.sessionBus())
            iface.asyncCall("EnableZoneDetected", True)
        except:
            pass
        
    @pyqtSlot()    
    def disable_zone(self):
        try:
            iface = QDBusInterface("com.deepin.daemon.Zone", "/com/deepin/daemon/Zone", '', QDBusConnection.sessionBus())
            iface.asyncCall("EnableZoneDetected", False)
        except:
            pass
        
    def exit_app(self):
        self.enable_zone()
        qApp.quit()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = Window()
    
    qApp.lastWindowClosed.connect(view.exit_app)
    
    qml_context = view.rootContext()
    qml_context.setContextProperty("windowView", view)
    qml_context.setContextProperty("qApp", qApp)
    qml_context.setContextProperty("screenWidth", view.window_info.screen_width)
    qml_context.setContextProperty("screenHeight", view.window_info.screen_height)
        
    view.setSource(QtCore.QUrl.fromLocalFile(os.path.join(os.path.dirname(__file__), 'Main.qml')))
        
    view.disable_zone()
    view.showFullScreen()
            
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec_())
    
