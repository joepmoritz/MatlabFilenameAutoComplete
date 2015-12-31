import sublime, sublime_plugin
import os

class MatlabFilenameAutoComplete(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		self.max_depth = 8
		scope = view.scope_name(view.sel()[0].begin());

		if not scope.startswith('source.matlab'):
			return None

		completions = []
		for folder in sublime.active_window().folders():
			self.depth = 0
			completions.extend(self.__get_completions(folder))

		return completions

	def __get_completions(self, folder):
		self.depth += 1
		completions = []
		for f in os.listdir(folder):
			if f.startswith('.'): continue
			if not f.endswith('.m'): 
				full_f = os.path.join(folder, f)
				if os.path.isdir(full_f) and self.depth < self.max_depth:
					completions.extend(self.__get_completions(full_f))
					continue
				else:
					continue
			f = f[:-2]
			completions.append([f, f])
		self.depth -= 1
		if completions.count == 0:
			return None
		return completions
