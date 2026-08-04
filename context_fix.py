from copy import copy as _copy

try:
    from django.template import context

    def _basecontext_copy(self):
        duplicate = object.__new__(type(self))
        duplicate.dicts = self.dicts[:]
        return duplicate

    def _context_copy(self):
        duplicate = _basecontext_copy(self)
        duplicate.render_context = _copy(self.render_context)
        return duplicate

    def _requestcontext_copy(self):
        duplicate = _context_copy(self)
        duplicate.request = self.request
        duplicate.template = self.template
        duplicate.template_name = self.template_name
        return duplicate

    context.BaseContext.__copy__ = _basecontext_copy
    context.Context.__copy__ = _context_copy
    context.RequestContext.__copy__ = _requestcontext_copy
except Exception:
    pass
