# -*- coding: utf-8 -*-
# Copyright (C) 2020 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

# import the necessary modules.
import appModuleHandler
import addonHandler
import api
import ui
import time
from globalCommands import commands
from scriptHandler import script, executeScript
from tones import beep
from speech import cancelSpeech

# For translation
addonHandler.initTranslation()

def script_test():
		if api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0).isFocusable == True:
			ui.message(_("Se encontro el botón"))
		else:
			ui.message(_("No encontro el botón"))

class AppModule(appModuleHandler.AppModule):
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
