# -*- coding: utf-8 -*-
# Copyright (C) 2020 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

# import the necessary modules.
import wx
import gui
import appModuleHandler
import addonHandler
import api
import ui
import time
import winUser
from globalCommands import commands
from scriptHandler import script, executeScript
from tones import beep
from speech import cancelSpeech

# For translation
addonHandler.initTranslation()

# Function taken from the add-on emoticons to center the window
def _calculatePosition(width, height):
	w = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_X)
	h = wx.SystemSettings.GetMetric(wx.SYS_SCREEN_Y)
	# Centre of the screen
	x = w / 2
	y = h / 2
	# Minus application offset
	x -= (width / 2)
	y -= (height / 2)
	return (x, y)

# Function taken from the Mozilla add-on to simulate mouse clicks
def mouseClick(obj, button="left"):
	api.moveMouseToNVDAObject(obj)
	api.setMouseObject(obj)
	if button == "left":
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
	if button == "right":
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)

class AppModule(appModuleHandler.AppModule):
	@script(gesture="kb:NVDA+F6")
	def script_chromeTab(self, gesture):
		lista = []
		chromeObj = api.getForegroundObject()
		obj = chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).firstChild
		while obj:
			if hasattr(obj, "IA2Attributes") and "class" in obj.IA2Attributes and obj.IA2Attributes["class"] == None:
				break
			lista.append(obj.name)
			obj = obj.next
		control = False
		try:
			lista.remove(None)
			control = True
		except:
			pass
		if control == False:
			try:
				del lista[-1]
			except:
				pass

		self._TabDialog = TabDialog(gui.mainFrame, lista, chromeObj, control)
		gui.mainFrame.prePopup()
		self._TabDialog.Show()

	@script(gesture="kb:F7")
	def script_chromeback(self, gesture):
		try:
			obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(0)
		except AttributeError:
			# Translators: Message indicating that the button was not found
			ui.message(_("Button not found"))
			return
		if obj.isFocusable == False:
			# Translators: Message indicating no history
			ui.message(_("No history to display"))
		else:
			mouseClick(obj, "right")
			api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1))

	@script(gesture="kb:F8")
	def script_chromenext(self, gesture):
		try:
			obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(1)
		except AttributeError:
			# Translators: Message indicating that the button was not found
			ui.message(_("Button not found"))
			return
		if obj.isFocusable == False:
			# Translators: Message indicating no history
			ui.message(_("No history to display"))
		else:
			mouseClick(obj, "right")
			api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1))

	@script(gesture="kb:F9")
	def script_chromeReader(self, gesture):
		try:
			obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(4).getChild(24).firstChild
		except AttributeError:
			# Translators: Indicates with a message that the read mode was not found
			ui.message(_("Read mode not found"))
			return
		while obj:
			if hasattr(obj, "IA2Attributes") and "class" in obj.IA2Attributes and obj.IA2Attributes["class"] == "ReaderModeIconView":
				break
			obj = obj.next
		if obj:
			if obj.isFocusable == False:
				# Translators: Indicates with a message that read mode is not available
				ui.message(_("Read mode not available"))
			else:
				try:
					if api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
						# Translators: Indicates with a message that we are leaving the reading mode
						ui.message(_("Downloading read mode..."))
						beep(100,150)
						time.sleep(0.5)
					else:
						# Translators: Indicates with a message that we are entering reading mode
						ui.message(_("Loading readout mode..."))
						beep(100,150)
						time.sleep(0.5)
				except:
					# Translators: Indicates with a message that we are entering reading mode
					ui.message(_("Loading readout mode..."))
					beep(100,150)
					time.sleep(0.5)

				api.setNavigatorObject(obj)
				executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter")
				cancelSpeech()

class TabDialog(wx.Dialog):
	def __init__(self, parent, lista, chromeObj, control):
		WIDTH = 800
		HEIGHT = 600
		pos = _calculatePosition(WIDTH, HEIGHT)

		# Translators: Title of the Tab List dialog box
		super(TabDialog, self).__init__(parent, -1, title=_("List of tabs"), pos = pos, size = (WIDTH, HEIGHT))

		self.lista = lista
		self.chromeObj = chromeObj
		self.control = control

		self.Panel = wx.Panel(self)

		self.myListBox = wx.ListBox(self.Panel)
		self.myListBox.Append(self.lista)
		self.myListBox.SetSelection(0)
		self.Bind(wx.EVT_LISTBOX, self.OnSelection, self.myListBox)
		self.myListBox.Bind(wx.EVT_KEY_UP, self.SelectListbox)
		self.Bind(wx.EVT_ACTIVATE, self.onExit)

		# Translators: A button on the list dialog to perform left mouse click.
		self.clicLeftBTN = wx.Button(self.Panel, wx.ID_ANY, _("&Left Click"))
		self.Bind(wx.EVT_BUTTON, self.clicLeft, self.clicLeftBTN)

		# Translators: A button in the list dialog to perform right mouse click.
		self.clicRightBTN = wx.Button(self.Panel, wx.ID_ANY, _("&Right Click"))
		self.Bind(wx.EVT_BUTTON, self.clicRight, self.clicRightBTN)

		# Translators: New Tab Button Name
		self.clicNewTabBTN = wx.Button(self.Panel, wx.ID_ANY, _("&New tab"))
		self.Bind(wx.EVT_BUTTON, self.clicNewTab, self.clicNewTabBTN)

		# Translators: Exit button name
		self.closeBTN = wx.Button(self.Panel, wx.ID_CANCEL, _("&Close"))
		self.Bind(wx.EVT_BUTTON, self.onExit, id=wx.ID_CANCEL)

		sizeV = wx.BoxSizer(wx.VERTICAL)
		sizeH = wx.BoxSizer(wx.HORIZONTAL)
		sizeV.Add(self.myListBox, 1, wx.EXPAND|wx.ALL, 5)
		sizeH.Add(self.clicLeftBTN, 2, wx.CENTER)
		sizeH.Add(self.clicRightBTN, 2, wx.CENTER)
		sizeH.Add(self.clicNewTabBTN, 2, wx.CENTER)
		sizeH.Add(self.closeBTN, 2, wx.CENTER)
		sizeV.Add(sizeH, 0, wx.CENTER)
		self.Panel.SetSizer(sizeV)

	def OnSelection(self, event):
		pass

	def SelectListbox(self, event):
		if event.GetKeyCode() ==13:
			self.clicLeft(None)

	def clicLeft(self, event):
		indice = self.myListBox.GetSelection()
		objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "left")
		api.setNavigatorObject(self.chromeObj.getChild(0).getChild(1).getChild(1).getChild(1))
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicRight(self, event):
		indice = self.myListBox.GetSelection()
		objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "right")
		api.setNavigatorObject(self.chromeObj.getChild(0).getChild(1).getChild(1).getChild(1))
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicNewTab(self, event):
		if self.control == False:
			objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(len(self.lista))
		else:
			objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(len(self.lista)).getChild(0)

		mouseClick(objeto, "left")
		self.Destroy()
		gui.mainFrame.postPopup()

	def onExit(self, event):
		if event.GetEventType() == 10012:
			self.Destroy()
			gui.mainFrame.postPopup()
		elif event.GetActive() == False:
			self.Destroy()
			gui.mainFrame.postPopup()
		event.Skip()
