# -*- coding: utf-8 -*-
# Copyright (C) 2021 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.
#
# Agradecer la cesión de código a los siguientes proyectos:
#
# - Javi Domínguez
# https://github.com/javidominguez/MozillaScripts
# - Hamada Trichine
# https://github.com/hamadatrichine/nvda-screen-rapping
#
# Importación módulos necesarios

import appModuleHandler
import addonHandler
import api
import gui
import config
import textInfos
import wx
import re
import time
import winUser
from scriptHandler import script, executeScript
from globalCommands import commands
from sayAllHandler import readText, CURSOR_CARET
from globalPluginHandler import GlobalPlugin
from browseMode import BrowseModeTreeInterceptor
from core import callLater
from inputCore import SCRCAT_BROWSEMODE
from ui import message
from tones import beep
from speech import cancelSpeech, speak
from scriptHandler import willSayAllResume

# Línea para definir la traducción
addonHandler.initTranslation()

confspec = {'isActive':'boolean(default=True)'}
config.conf.spec['chromeconfig'] = confspec

oldQuickNav = BrowseModeTreeInterceptor._quickNavScript

# Text to translate
# Translators: Text spoken when screen rapping to top.
msgrpTop = _('Foco al inicio')
# Translators: Text spoken when screen rapping to bottom.
msgrpBottom = _('Foco al final')

def getCurrentPos(self):
	currentPosStart = self.makeTextInfo(textInfos.POSITION_FIRST)
	currentPosEnd = self.makeTextInfo(textInfos.POSITION_CARET)
	currentPosStart.setEndPoint(currentPosEnd, 'endToStart')
	return len(currentPosStart.text)

def resetPosition(self, positionNumber,itemType):
	pos = self.makeTextInfo(textInfos.POSITION_FIRST)
	pos.move(textInfos.UNIT_CHARACTER, positionNumber)
	if hasattr(self, 'selection'):
		self.selection = pos
	else:
		pos.updateCaret()
	cancelSpeech()
	pos.move(textInfos.UNIT_LINE,1,endPoint="end")
	itemText = '{}s'.format(itemType) if itemType[-1] != 'x' else '{}es'.format(itemType)
	message(
			# translators: Text spoken when the type of nav items does not exist in the page.
			_('No hay controles en la pagina.'))
#			_('No existe {} en esta página.').format(itemText))

def updatePosition(obj,position):
	objPos = obj.makeTextInfo(position)
	objPos.updateCaret()
	cancelSpeech()

def initNavItemsGenerator(self,itemType):
	if itemType=="notLinkBlock":
		return self._iterNotLinkBlock
	else:
		return lambda direction,info: self._iterNodesByType(itemType,direction,info)

def screenRapping(self,itemType,readUnit,msg,rpTo,tone=(500,80),reverse='previous',direction='next'):
	updatePosition(self,rpTo)
	navItems = initNavItemsGenerator(self,itemType)
	try:
		rapping = next(navItems(direction,self.selection))
		speak([msg])
		rapping.moveTo()
		try:
			rapping = next(navItems(reverse,self.selection))
			callLater(300,rapping.moveTo)
		except StopIteration:
			pass
		beep(tone[0],tone[1])
		rapping.report(readUnit=readUnit)
		return True
	except StopIteration:
		pass

def quickNavRapping(self,gesture, itemType, direction, errorMessage, readUnit):
	iterFactory = initNavItemsGenerator(self,itemType)
	try:
		item = next(iterFactory(direction, self.selection))
	except NotImplementedError:
		# Translators: a message when a particular quick nav command is not supported in the current document.
		message(_('No soportado en este documento'))
		return
	except StopIteration:
		if direction == 'next':
			lastPos = getCurrentPos(self)
			if not screenRapping(self,itemType,readUnit,msgrpTop,rpTo=textInfos.POSITION_FIRST):
				resetPosition(self,lastPos,itemType)
		else:
			lastPos = getCurrentPos(self)
			if not screenRapping(self,itemType,readUnit,msgrpBottom,rpTo=textInfos.POSITION_LAST,tone=(100,80),reverse='next',direction='previous'):
				resetPosition(self,lastPos,itemType)
		return

	item	.moveTo()
	if not gesture or not willSayAllResume(gesture):
		item.report(readUnit=readUnit)

isActivated = config.conf['chromeconfig']['isActive']
if isActivated: BrowseModeTreeInterceptor._quickNavScript = quickNavRapping

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

# Function taken from the Mozilla add-on to search objects
def searchObject(path):
	obj = api.getForegroundObject()
	for milestone in path:
		obj = searchAmongTheChildren(milestone, obj)
		if not obj:
			return
	return obj

# Function taken from the Mozilla add-on to search objects
def searchAmongTheChildren(id, into):
	if not into:
		return(None)
	key, value = id
	obj = into.firstChild
	if hasattr(obj, "IA2Attributes") and key in obj.IA2Attributes.keys():
		if re.match(value, obj.IA2Attributes[key]):
			return(obj)
	while obj:
		if hasattr(obj, "IA2Attributes") and key in obj.IA2Attributes.keys():
			if re.match(value, obj.IA2Attributes[key]):
				break
		obj = obj.next
	return(obj)

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

class AppModule(appModuleHandler.AppModule):
	@script(gesture="kb:NVDA+F6", description= _("Displays the list of tabs"), category= _("Chrome Utilities"))
	def script_chromeTab(self, gesture):
		lista = []
		chromeObj = api.getForegroundObject()
		# Buscar pestañas.
		pestañasTab = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","TabStripRegionView"),
			("class","TabStrip"))
		obj = searchObject(pestañasTab).firstChild
		if obj == None: # Antigua manera apuntando directamente al objeto
			obj = chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).firstChild

		while obj:
			if hasattr(obj, "IA2Attributes") and "class" in obj.IA2Attributes and obj.IA2Attributes["class"] == None:
				break
			lista.append(obj.name)
			obj = obj.next
		for i in lista:
			if i == None:
				lista.remove(None)

		self._TabDialog = TabDialog(gui.mainFrame, lista, chromeObj)
		gui.mainFrame.prePopup()
		self._TabDialog.Show()

	@script(gesture="kb:F7", description= _("Displays a menu with the history of visited pages backwards"), category= _("Chrome Utilities"))
	def script_chromeback(self, gesture):
		atrasBTN = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"))
		obj = searchObject(atrasBTN).getChild(0)
		if obj == None:
			try:
				obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(0)
			except AttributeError:
				# Translators: Message indicating that the button was not found
				message(_("El botón no existe"))
				return
		if obj.isFocusable == False:
			# Translators: Message indicating no history
			message(_("No hay historial para mostrar"))
		else:
			mouseClick(obj, "right")
			webRoot = (
				("class","NonClientView"),
				("class","BrowserView"),
				("class","View"),
				("tag","#document"))
			objRot = searchObject(webRoot)
			if objRot == None:
				api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1))
			else:
				api.setNavigatorObject(objRot)


	@script(gesture="kb:F8", description= _("Displays a menu with the history of visited pages forward"), category= _("Chrome Utilities"))
	def script_chromenext(self, gesture):
		atrasBTN = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"))
		obj = searchObject(atrasBTN).getChild(1)
		if obj == None:
			try:
				obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(1)
			except AttributeError:
				# Translators: Message indicating that the button was not found
				message(_("El botón no existe"))
				return
		if obj.isFocusable == False:
			# Translators: Message indicating no history
			message(_("No hay historial para mostrar"))
		else:
			mouseClick(obj, "right")
			webRoot = (
				("class","NonClientView"),
				("class","BrowserView"),
				("class","View"),
				("tag","#document"))
			objRot = searchObject(webRoot)
			if objRot == None:
				api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1))
			else:
				api.setNavigatorObject(objRot)

	@script(gesture="kb:F9", description= _("Activates and deactivates the reading mode"), category= _("Chrome Utilities"))
	def script_chromeReader(self, gesture):
		path = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"),
			("class","LocationBarView"),
			("class","PageActionIconContainerView"),
			("class","ReaderModeIconView"))
		obj = searchObject(path)
		if obj:
			if obj.isFocusable == False:
				# Translators: Indicates with a message that read mode is not available
				message(_("Modo lectura no disponible"))
			else:
				try:
					if api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
						# Translators: Indicates with a message that we are leaving the reading mode
						message(_("Desactivando modo lectura..."))
						time.sleep(0.5)
					else:
						# Translators: Indicates with a message that we are entering reading mode
						message(_("Activando modo lectura..."))
						time.sleep(0.5)
				except:
					# Translators: Indicates with a message that we are entering reading mode
					message(_("Activando modo lectura..."))
					time.sleep(0.5)
				api.setNavigatorObject(obj)
				try:
					executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter")
				except:
					mouseClick(obj, "left")
				cancelSpeech()

	@script(gesture="kb:shift+f9", description= _("Read the result in read mode"), category= _("Chrome Utilities"))
	def script_modeReaderSpeak(self, gesture):
		try:
			if api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
				readText(CURSOR_CARET)
		except:
			message(_("No esta en modo lectura"))

	@script(gesture="kb:shift+f4", description= _("Modo ciclico"), category= _("Chrome Utilities"))
	def script_ciclicoChrome(self, gesture):
		global oldQuickNav, isActivated

		if isActivated:
			BrowseModeTreeInterceptor._quickNavScript = oldQuickNav
			config.conf['chromeconfig']['isActive'] = False
			isActivated = config.conf['chromeconfig']['isActive']
			message(
					# Translators: Text spoken when screen rapping is turned off.
					_('Navegación cíclica desactivada.'))
			beep(100,150)
		else:
			BrowseModeTreeInterceptor._quickNavScript = quickNavRapping
			config.conf['chromeconfig']['isActive'] = True
			isActivated = config.conf['chromeconfig']['isActive']
			message(
					# Translators: Text spoken when screen rapping is turned on.
					_('Navegación cíclica activada.'))
			beep(400,150)


class TabDialog(wx.Dialog):
	def __init__(self, parent, lista, chromeObj):
		WIDTH = 800
		HEIGHT = 600
		pos = _calculatePosition(WIDTH, HEIGHT)

		# Translators: Title of the Tab List dialog box
		super(TabDialog, self).__init__(parent, -1, title=_("Lista de pestañas"), pos = pos, size = (WIDTH, HEIGHT))

		self.lista = lista
		self.chromeObj = chromeObj

		self.Panel = wx.Panel(self)

		self.myListBox = wx.ListBox(self.Panel)
		self.myListBox.Append(self.lista)
		self.myListBox.SetSelection(0)
		self.Bind(wx.EVT_LISTBOX, self.OnSelection, self.myListBox)
		self.myListBox.Bind(wx.EVT_KEY_UP, self.SelectListbox)
		self.Bind(wx.EVT_ACTIVATE, self.onExit)

		# Translators: A button on the list dialog to perform left mouse click.
		self.clicLeftBTN = wx.Button(self.Panel, wx.ID_ANY, _("Clic en botón &Izquierdo"))
		self.Bind(wx.EVT_BUTTON, self.clicLeft, self.clicLeftBTN)

		# Translators: A button in the list dialog to perform right mouse click.
		self.clicRightBTN = wx.Button(self.Panel, wx.ID_ANY, _("Clic en botón &Derecho"))
		self.Bind(wx.EVT_BUTTON, self.clicRight, self.clicRightBTN)

		# Translators: New Tab Button Name
		self.clicNewTabBTN = wx.Button(self.Panel, wx.ID_ANY, _("&Nueva pestaña"))
		self.Bind(wx.EVT_BUTTON, self.clicNewTab, self.clicNewTabBTN)

		# Translators: Exit button name
		self.closeBTN = wx.Button(self.Panel, wx.ID_CANCEL, _("&Cerrar"))
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

	def searchObject(self, path, valor, event=None):
		obj = valor
		for milestone in path:
			obj = searchAmongTheChildren(milestone, obj)
			if not obj:
				return
		if event == None:
			return obj
		else:
			return obj.getChild(event)

	def OnSelection(self, event):
		pass

	def SelectListbox(self, event):
		if event.GetKeyCode() ==13:
			self.clicLeft(None)

	def clicLeft(self, event):
		indice = self.myListBox.GetSelection()
		clic = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","TabStripRegionView"),
			("class","TabStrip"))
		objeto = self.searchObject(clic, self.chromeObj, indice)
		if objeto == None:
			objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "left")
		webRoot = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","View"),
			("tag","#document"))
		objRot = self.searchObject(webRoot, self.chromeObj)
		if objRot == None:
			api.setNavigatorObject(self.chromeObj.getChild(0).getChild(1).getChild(1).getChild(1))
		else:
			api.setNavigatorObject(objRot)
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicRight(self, event):
		indice = self.myListBox.GetSelection()
		clic = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","TabStripRegionView"),
			("class","TabStrip"))
		objeto = self.searchObject(clic, self.chromeObj, indice)
		if objeto == None:
			objeto = self.chromeObj.getChild(0).getChild(1).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "right")
		webRoot = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","View"),
			("tag","#document"))
		objRot = self.searchObject(webRoot, self.chromeObj)
		if objRot == None:
			api.setNavigatorObject(self.chromeObj.getChild(0).getChild(1).getChild(1).getChild(1))
		else:
			api.setNavigatorObject(objRot)
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicNewTab(self, event):
		# Para versiones Finales
		nuevaPestañaBoton = (
			("class","NonClientView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","TabStripRegionView"),
			("class","TabStrip"),
			("class","View"),
			("class","NewTabButton"))
		objeto = self.searchObject(nuevaPestañaBoton, self.chromeObj)
		if objeto == None:
			# Para versiones beta y canary
			nuevaPestañaBoton = (
				("class","NonClientView"),
				("class","BrowserView"),
				("class","TopContainerView"),
				("class","TabStripRegionView"),
				("class","NewTabButton"))
			objeto = self.searchObject(nuevaPestañaBoton, self.chromeObj)

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
