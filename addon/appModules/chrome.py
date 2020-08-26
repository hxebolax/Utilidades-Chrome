# -*- coding: utf-8 -*-
# Copyright (C) 2020 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

# import the necessary modules.
import appModuleHandler
import addonHandler
import api
import ui
from globalCommands import commands
from scriptHandler import script, executeScript

# For translation
addonHandler.initTranslation()

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

class AppModule(appModuleHandler.AppModule):
	@script(gesture="kb:F9")
	def script_chromeReader(self, gesture):
		try:
			obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(4).getChild(24).firstChild
		except AttributeError:
			# Translators: Indicates with a message that the read mode was not found
			ui.message(_("Read mode not found"))
			return
		while obj: # mientras obj no sea None
			if hasattr(obj, "IA2Attributes") and "class" in obj.IA2Attributes and obj.IA2Attributes["class"] == "ReaderModeIconView":
				break
			obj = obj.next
		if obj:
			if obj.isFocusable == False:
				# Translators: Indicates with a message that read mode is not available
				ui.message(_("Read mode not available"))
			else:
				try:
					objBoton = api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0)
					# Translators: Indicates with a message that we are leaving the reading mode
					ui.message(_("Downloading read mode..."))
				except:
					# Translators: Indicates with a message that we are entering reading mode
					ui.message(_("Loading readout mode..."))
				api.setNavigatorObject(obj) 
				executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
