from sublime_plugin import WindowCommand
from .utils import remoteCommand
from sublime import set_timeout

class Daemontools(WindowCommand):

    def run(self):
        self.view = self.window.active_view()
        self._listServices()

    def _listServices(self):
        services = remoteCommand(self.view, "ls -1 /etc/service").strip().split('\n')
        set_timeout(lambda: self.window.show_quick_panel(services, lambda i: self._showActions(services[i]) if i != -1 else None), 0)

    def _showActions(self, service):
        actions = ['start', 'stop', 'restart']
        status = remoteCommand(self.view, "svstat /etc/service/{0}".format(service)).strip()

        def choose(i):
            if i == -1:
                return
            elif i == 0:
                self._listServices()
            elif i == 1:
                self._showActions(service)
            else:
                self._doAction(service, actions[i - 2])
        set_timeout(lambda: self.window.show_quick_panel(["..", status] + actions, choose), 0)

    def _doAction(self, service, action):
        if action == 'status':
            self._showMessage(service, )
            return
        else:
            actionOptions = {
                'start': 'u',
                'stop': 'd',
                'restart': 't'
            }
        remoteCommand(self.view, "svc -{0} /etc/service/{1}".format(actionOptions[action], service))
        self._showActions(service)

    def _showMessage(self, service, message):
        set_timeout(lambda: self.window.show_quick_panel([message], lambda i: self._showActions(service) if i != -1 else None), 0)
