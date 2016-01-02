import sublime, sublime_plugin
import os, re

class MatlabFilenameAutoComplete(sublime_plugin.EventListener):
	def __init__(self):
		# invoked when loading plugin.
		super(MatlabFilenameAutoComplete, self).__init__()
		self.max_depth = 10
		self.depth = 0
		self.completion_cached = False
		self.cache = []

		self.fun_reg = re.compile(r'function.*[\s=][a-zA-Z]\w*\s*\((.*\))')
		self.param_reg = re.compile(r'([a-zA-Z]\w*)\s*[\),]')

	def on_query_completions(self, view, prefix, locations):
		scope = view.scope_name(view.sel()[0].begin());
		if not scope.startswith('source.matlab'):
			return None

		if not self.completion_cached:
			for folder in sublime.active_window().folders():
				self.cache += self.__get_completions(folder, prefix)
			self.completion_cached = True

		completions = self.cache + view.extract_completions(prefix)
		return (completions, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

	def on_activated(self, view):
		scope = view.scope_name(view.sel()[0].begin());
		if not scope.startswith('source.matlab'):
			return
		self.completion_cached = False
		self.cache = []

	def __get_completions(self, folder, prefix):
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
						func = fh.readline()
						if self.fun_reg.match(func):
							func = self.fun_reg.findall(func)
							params = self.param_reg.findall(func[0])
							trigger += '\t('
							content += '('
							nParam = len(params)
							for ii in range(0, nParam-1):
								content += '${' + str(ii+1) + ':' + params[ii] + '}, '
								trigger += params[ii] + ', '
							if nParam >= 1:
								content += '${' + str(nParam) + ':' + (params[nParam-1] if params[nParam-1] != 'varargin' else '...') + '}' 
								trigger += (params[nParam-1] if params[nParam-1] != 'varargin' else '...')
							content += ')'
							trigger += ')'
						else:
							trigger += '\tScript'
				completions.append((trigger, content))
			elif os.path.isdir(full_f) and self.depth < self.max_depth:
				completions += self.__get_completions(full_f, prefix)
		self.depth -= 1
		return completions
