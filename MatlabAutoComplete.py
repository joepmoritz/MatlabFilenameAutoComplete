import sublime, sublime_plugin
import os


class MatlabAutoComplete(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		scope = view.scope_name(view.sel()[0].begin());

		if not scope.startswith('source.matlab'):
			return None

		completions = []
		for folder in sublime.active_window().folders():
			for f in os.listdir(folder):
				if f.startswith('.'): continue
				if not f.endswith('.m'): continue
				f = f[:-2]
				completions.append([f, f]);

		return completions
