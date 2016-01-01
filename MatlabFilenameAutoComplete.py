import sublime, sublime_plugin
import os, re


class MatlabFilenameAutoComplete(sublime_plugin.EventListener):

	def on_query_completions(self, view, prefix, locations):
		scope = view.scope_name(view.sel()[0].begin());

		if not scope.startswith('source.matlab'):
			return None

		self.max_depth = 8
		self.fun_reg = re.compile(r'function.+[a-zA-Z]+[a-zA-Z0-9_]*\(.*\).*')
		self.fun_line_reg = re.compile(r'[a-zA-Z]+[a-zA-Z0-9_]*\(.*\)')

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
			full_f = os.path.join(folder, f)
			if os.path.isfile(full_f) and f.endswith( ('.m','.dll','.mexa64','mexmaci64','mexw32') ): 
				func = f[:-2]
				if f.endswith('.m'):
					with open(full_f, 'r') as fh:
						rdstr = fh.readline()
						if self.fun_reg.match(rdstr):
							m = self.fun_line_reg.search(rdstr)
							func = m.group()
				completions.append([func, func])
			else:
				if os.path.isdir(full_f) and self.depth < self.max_depth:
					completions.extend(self.__get_completions(full_f))
		self.depth -= 1
		if completions.count == 0:
			return None
		return completions
