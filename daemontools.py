from sublime_plugin import WindowCommand
from .utils import remoteCommand
from sublime import set_timeout, message_dialog

class Daemontools(WindowCommand):

    def run(self):
        self.view = self.window.active_view()
        services = remoteCommand(self.view, "ls -1 /etc/service").strip().split('\n')
        self.window.show_quick_panel(services, lambda i: self._showActions(services[i]) if i != -1 else None)

    def _showActions(self, service):
        actions = ['start', 'stop', 'restart', 'status']
        set_timeout(lambda: self.window.show_quick_panel(actions, lambda i: self._doAction(service, actions[i]) if i != -1 else None), 0)

    def _doAction(self, service, action):
        if action == 'status':
            message_dialog(remoteCommand(self.view, "svstat /etc/service/{0}".format(service)).strip())
            return
        else:
            actionOptions = {
                'start': 'u',
                'stop': 'd',
                'restart': 't'
            }
        print (remoteCommand(self.view, "svc -{0} /etc/service/{1}".format(actionOptions[action], service)))

