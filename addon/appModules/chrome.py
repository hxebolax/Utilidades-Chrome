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
import ctypes
from scriptHandler import script, executeScript
from globalCommands import commands
try:
	from sayAllHandler import readText, CURSOR_CARET
except:
	from speech.sayAll import CURSOR # .CARET
	from speech.sayAll import SayAllHandler  # readText
from globalPluginHandler import GlobalPlugin
from browseMode import BrowseModeTreeInterceptor
from core import callLater
from inputCore import SCRCAT_BROWSEMODE
from ui import message
from tones import beep
from speech import cancelSpeech, speak
from scriptHandler import willSayAllResume
from gui import guiHelper, nvdaControls
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel

# Línea para definir la traducción
addonHandler.initTranslation()

confspec = {
	'isActive':'boolean(default=False)',
	"maximizar": "boolean(default=False)",
}
config.conf.spec['chromeconfig'] = confspec

# Translators: Texto que avisa cuando se desplaza al inicio
msgrpTop = _('Foco al inicio')
# Translators: Texto que avisa cuando se desplaza al final
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
			# translators: Mensaje que avisa la falta de controles
			_('No hay controles en la página.'))

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
	if api.getForegroundObject().appModule.productName == "Google Chrome":
		iterFactory = initNavItemsGenerator(self,itemType)
		try:
			item = next(iterFactory(direction, self.selection))
		except NotImplementedError:
			# Translators: Mensaje que indica que no se soporta en el documento
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
	else:
		if itemType=="notLinkBlock":
			iterFactory=self._iterNotLinkBlock
		else:
			iterFactory=lambda direction,info: self._iterNodesByType(itemType,direction,info)
		info=self.selection
		try:
			item = next(iterFactory(direction, info))
		except NotImplementedError:
			# Translators: a message when a particular quick nav command is not supported in the current document.
			message(_("No soportado en este documento"))
			return
		except StopIteration:
			message(errorMessage)
			return
		# #8831: Report before moving because moving might change the focus, which
		# might mutate the document, potentially invalidating info if it is
		# offset-based.
		if not gesture or not willSayAllResume(gesture):
			item.report(readUnit=readUnit)
		item.moveTo()

def mouseClick(obj, button="left"):
	api.moveMouseToNVDAObject(obj)
	api.setMouseObject(obj)
	if button == "left":
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_LEFTUP,0,0,None,None)
	if button == "right":
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTDOWN,0,0,None,None)
		winUser.mouse_event(winUser.MOUSEEVENTF_RIGHTUP,0,0,None,None)

def searchObject(path):
	obj = api.getForegroundObject()
	for milestone in path:
		obj = searchAmongTheChildren(milestone, obj)
		if not obj:
			return
	return obj

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
	def __init__(self, *args, **kwargs):
		super(AppModule, self).__init__(*args, **kwargs)

		# Mirar sustituir por shellapi.ShellExecute
		if config.conf["chromeconfig"]["maximizar"]:
			user32 = ctypes.WinDLL('user32')
			hWnd = user32.GetForegroundWindow()
			user32.ShowWindow(hWnd, 3)

		self.oldQuickNav = BrowseModeTreeInterceptor._quickNavScript

		self.isActivated = config.conf['chromeconfig']['isActive']
		if self.isActivated: BrowseModeTreeInterceptor._quickNavScript = quickNavRapping

		NVDASettingsDialog.categoryClasses.append(ChromePanel)

	def terminate(self):
		try:
			NVDASettingsDialog.categoryClasses.remove(ChromePanel)
			if self.isActivated:
				BrowseModeTreeInterceptor._quickNavScript = self.oldQuickNav
		except:
			pass

	@script(
		gesture="kb:NVDA+F6",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Muestra diálogo de pestañas"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_chromeTab(self, gesture):
		lista = []
		chromeObj = api.getForegroundObject()
		# Buscar pestañas.
		pestañasTab = (
			("class","BrowserRootView"),
			("class","NonClientView"),
			("class","GlassBrowserFrameView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","TabStripRegionView"),
			("class","TabStrip"))
		try:
			obj = searchObject(pestañasTab).firstChild
		except:
			obj = chromeObj.getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).firstChild

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

	@script(
		gesture="kb:F7",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Muestra el historial atrás"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_chromeback(self, gesture):
		atrasBTN = (
			("class","NonClientView"),
			("class","GlassBrowserFrameView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"))

		obj = searchObject(atrasBTN).getChild(0)
		if obj == None:
			try:
				obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(0)
			except AttributeError:
				# Translators: Mensaje indicando que no existe el botón
				message(_("El botón no existe"))
				return
		if obj.isFocusable == False:
			# Translators: Mensaje que indica que no hay historial
			message(_("No hay historial para mostrar"))
		else:
			mouseClick(obj, "right")
			api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(0).getChild(0).getChild(1).getChild(1).getChild(0))

	@script(
		gesture="kb:F8",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Muestra el historial adelante"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_chromenext(self, gesture):
		adelanteBTN = (
			("class","NonClientView"),
			("class","GlassBrowserFrameView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"))
		obj = searchObject(adelanteBTN).getChild(1)
		if obj == None:
			try:
				obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(1)
			except AttributeError:
				# Translators: Mensaje indicando que no existe el botón
				message(_("El botón no existe"))
				return
		if obj.isFocusable == False:
			# Translators: Mensaje que indica que no hay historial
			message(_("No hay historial para mostrar"))
		else:
			mouseClick(obj, "right")
			api.setNavigatorObject(api.getForegroundObject().getChild(0).getChild(0).getChild(0).getChild(1).getChild(1).getChild(0))

	@script(
		gesture="kb:F9",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Activa y desactiva modo lectura"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_chromeReader(self, gesture):
		path = (
			("class","NonClientView"),
			("class","GlassBrowserFrameView"),
			("class","BrowserView"),
			("class","TopContainerView"),
			("class","ToolbarView"),
			("class","LocationBarView"),
			("class","PageActionIconContainerView"),
			("class","ReaderModeIconView"))
		obj = searchObject(path)
		if obj:
			if obj.isFocusable == False:
				# Translators: Mensaje que indica que no hay modo lectura
				message(_("Modo lectura no disponible"))
			else:
				try:
					if api.getForegroundObject().getChild(0).getChild(0).getChild(0).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
						# Translators: Mensaje indicando que se desactiva el modo lectura
						message(_("Desactivando modo lectura..."))
						time.sleep(0.5)
					else:
						# Translators: Mensaje indicando que se activa el modo lectura
						message(_("Activando modo lectura..."))
						time.sleep(0.5)
				except:
					# Translators: Mensaje indicando que se activa el modo lectura
					message(_("Activando modo lectura..."))
					time.sleep(0.5)
				api.setNavigatorObject(obj)
				try:
					executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter")
				except:
					mouseClick(obj, "left")
				cancelSpeech()

	@script(
		gesture="kb:shift+f9",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Leer el resultado en modo lectura"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_modeReaderSpeak(self, gesture):
		try:
			if api.getForegroundObject().getChild(0).getChild(0).getChild(0).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
				try:
					readText(CURSOR_CARET)
				except:
					SayAllHandler.readText(CURSOR.CARET)
		except:
			# Translators: Mensaje que indica que no estamos en modo lectura
			message(_("No esta en modo lectura"))

	@script(
		gesture="kb:shift+f4",
		# Translators: Descripción del elemento en el diálogo de gestos de entrada
		description= _("Activar y desactivar navegación cíclica"),
		# Translators: Nombre complemento y categoría
		category= _("Utilidades Chrome"))
	def script_ciclicoChrome(self, gesture):
		if self.productName == "Google Chrome":

			if self.isActivated:
				BrowseModeTreeInterceptor._quickNavScript = self.oldQuickNav
				config.conf['chromeconfig']['isActive'] = False
				self.isActivated = config.conf['chromeconfig']['isActive']
				message(
						# Translators: Mensaje que anuncia la desactivación de la navegación cíclica
						_('Navegación cíclica desactivada.'))
				beep(100,150)
			else:
				BrowseModeTreeInterceptor._quickNavScript = quickNavRapping
				config.conf['chromeconfig']['isActive'] = True
				self.isActivated = config.conf['chromeconfig']['isActive']
				message(
						# Translators: Mensaje que anuncia la activación de la navegación cíclica
						_('Navegación cíclica activada.'))
				beep(400,150)

class TabDialog(wx.Dialog):
	def __init__(self, parent, lista, chromeObj):

		WIDTH = 800
		HEIGHT = 600
		pos = _calculatePosition(WIDTH, HEIGHT)

		# Translators: Titulo de la ventana de diálogo de pestañas
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

		# Translators: Nombre para el botón clic izquierdo
		self.clicLeftBTN = wx.Button(self.Panel, wx.ID_ANY, _("Clic en botón &Izquierdo"))
		self.Bind(wx.EVT_BUTTON, self.clicLeft, self.clicLeftBTN)

		# Translators: Nombre para el botón clic derecho
		self.clicRightBTN = wx.Button(self.Panel, wx.ID_ANY, _("Clic en botón &Derecho"))
		self.Bind(wx.EVT_BUTTON, self.clicRight, self.clicRightBTN)

		# Translators: Nombre para el botón nueva pestaña
		self.clicNewTabBTN = wx.Button(self.Panel, wx.ID_ANY, _("&Nueva pestaña"))
		self.Bind(wx.EVT_BUTTON, self.clicNewTab, self.clicNewTabBTN)

		# Translators: Nombre para el botón cerrar
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
		objeto = self.chromeObj.getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "left")
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicRight(self, event):
		indice = self.myListBox.GetSelection()
		objeto = self.chromeObj.getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(indice)
		mouseClick(objeto, "right")
		self.Destroy()
		gui.mainFrame.postPopup()

	def clicNewTab(self, event):
		objeto = self.chromeObj.getChild(0).getChild(0).getChild(0).getChild(0).getChild(0).getChild(1)
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

class ChromePanel(SettingsPanel):
	#TRANSLATORS: title for the Update Channel settings category
	title=_("Utilidades Chrome")

	def makeSettings(self, sizer):
		helper=guiHelper.BoxSizerHelper(self, sizer=sizer)

		self.chromeCheckBoxMaximize = helper.addItem(wx.CheckBox(self, label=_("Abrir las ventanas de Chrome maximizadas")))
		self.chromeCheckBoxMaximize.Value = config.conf["chromeconfig"]["maximizar"]

	def onSave(self):
		maxWinChrome = config.conf["chromeconfig"]["maximizar"]
		config.conf["chromeconfig"]["maximizar"] = self.chromeCheckBoxMaximize.Value
