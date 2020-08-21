import appModuleHandler
import api
import ui
from scriptHandler import script
import scriptHandler
import globalCommands

class AppModule(appModuleHandler.AppModule):
	@script(gesture="kb:F9")
	def script_chromeReader(self, gesture):
		obj = api.getForegroundObject().children[0].children[1].children[0].children[1].children[4].children[24].children[9]
		ffVersion = int(self.productVersion.split(".")[0])
		if ffVersion == 84:
			if obj.isFocusable == False:
				ui.message("Modo lectura no disponible")
			else:
				tituloVentana = api.getForegroundObject().children[0].children[1].children[1].children[1]
				tituloTrozos = tituloVentana.name.split(" - ")
				if len(tituloTrozos) == 1:
					ui.message("Cargando modo lectura...")
					api.setNavigatorObject(obj) 
					scriptHandler.executeScript(globalCommands.commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
				elif tituloTrozos[1] == "Modo de lectura":
					ui.message("Descargando modo lectura...")
					api.setNavigatorObject(obj) 
					scriptHandler.executeScript(globalCommands.commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
				else:
					ui.message("Cargando modo lectura...")
					api.setNavigatorObject(obj) 
					scriptHandler.executeScript(globalCommands.commands.script_review_activate, "kb(desktop):NVDA+numpadEnter") 
		else:
			pass
