import sublime, sublime_plugin
import os, re

class MatlabFilenameAutoComplete(sublime_plugin.EventListener):
	def __init__(self):
		super(MatlabFilenameAutoComplete, self).__init__()
		self.max_depth = 8

		self.fun_reg = re.compile(r'function.+[a-zA-Z]+[a-zA-Z0-9_]*\(.*\).*')
		self.fun_line_reg = re.compile(r'[a-zA-Z]+[a-zA-Z0-9_]*\(.*\)')
		self.param_reg = re.compile(r'[\(,]?\s*([a-zA-Z]+[a-zA-Z0-9_]*)\s*[\),]?')

	def on_query_completions(self, view, prefix, locations):
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
			full_f = os.path.join(folder, f)
			if os.path.isfile(full_f) and f.endswith( ('.m','.dll','.mexa64','mexmaci64','mexw32') ): 
				trigger = f[:-2]
				content = trigger
				if f.endswith('.m'):
					with open(full_f, 'r') as fh:
						rdstr = fh.readline()
						if self.fun_reg.match(rdstr):
							m = self.fun_line_reg.search(rdstr)
							func = m.group()
							params = self.param_reg.findall(func)
							content = params[0] + '('
							nParam = len(params)
							for ii in range(1,nParam):
								content += '${' + str(ii) + ':' + params[ii] + '}' + (', ' if ii!=nParam-1 else '')
							content += ')'
				completions.append([trigger, content])
			else:
				if os.path.isdir(full_f) and self.depth < self.max_depth:
					completions.extend(self.__get_completions(full_f))
		self.depth -= 1
		if completions.count == 0:
			return None
		return completions
