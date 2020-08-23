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

class AppModule(appModuleHandler.AppModule):
	@script(gesture="kb:F9")
	def script_chromeReader(self, gesture):
		try:
			obj = api.getForegroundObject().getChild(0).getChild(1).getChild(0).getChild(1).getChild(4).getChild(24).getChild(9)
			if obj.IA2Attributes["class"] == "ReaderModeIconView":
				if int(self.productVersion.split(".")[0]) >= 84:
					if obj.isFocusable == False:
						# Translators: Indicates with a message that read mode is not available
						ui.message(_("Read mode not available"))
					else:
						try:
							objBoton = api.getForegroundObject().getChild(0).getChild(1).getChild(1).getChild(1).getChild(0).getChild(0).getChild(0).getChild(0)
							# Translators: Indicates with a message that we are leaving the reading mode
							ui.message(_("Downloading read mode..."))
							api.setNavigatorObject(obj) 
							executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
						except:
							# Translators: Indicates with a message that we are entering reading mode
							ui.message(_("Loading readout mode..."))
							api.setNavigatorObject(obj) 
							executeScript(commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
				else:
					# Translators: Indicates with a message that the plug-in is only valid for Chrome 84.0 and above
					ui.message(_("Supported add-on from Chrome +84.0"))
		except (KeyError, AttributeError):
			# Translators: Indicates with a message that the read mode was not found
			ui.message(_("Read mode not found"))
