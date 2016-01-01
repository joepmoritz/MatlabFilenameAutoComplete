import sublime, sublime_plugin
import os, re

class MatlabFilenameAutoComplete(sublime_plugin.EventListener):
	def __init__(self):
		super(MatlabFilenameAutoComplete, self).__init__()
		self.max_depth = 8
		self.depth = 0

		self.fun_reg = re.compile(r'function.+[\s=]([a-zA-Z]\w*\s*\(.*\))')
		self.param_reg = re.compile(r'[\(,]?\s*([a-zA-Z]+[a-zA-Z0-9_]*)\s*[\),]?')

	def on_query_completions(self, view, prefix, locations):
		scope = view.scope_name(view.sel()[0].begin());
		if not scope.startswith('source.matlab'):
			return None

		completions = []
		for folder in sublime.active_window().folders():
			completions += self.__get_completions(folder)

		return completions

	def __get_completions(self, folder):
		self.depth += 1
		completions = []
		for f in os.listdir(folder):
			if f.startswith('.'): continue
			full_f = os.path.join(folder, f)
			[f, ext] = os.path.splitext(f)
			if os.path.isfile(full_f) and ext in ('.m','.mexa64','.mexmaci64','.mexw32'): 
				(trigger, content) = (f, f)
				if ext == '.m':
					with open(full_f, 'r') as fh:
						func = self.fun_reg.findall(fh.readline())
						if len(func) > 0:
							params = self.param_reg.findall(func[0])
							trigger += '('
							content += '('
							nParam = len(params)
							for ii in range(1,nParam):
								content += '${' + str(ii) + ':' + params[ii] + '}' + (', ' if ii!=nParam-1 else '')
								trigger += params[ii] + (', ' if ii!=nParam-1 else '')
							content += ')'
							trigger += ')'
				completions.append([trigger, content])
			elif os.path.isdir(full_f) and self.depth < self.max_depth:
				completions += self.__get_completions(full_f)
		self.depth -= 1
		return completions
