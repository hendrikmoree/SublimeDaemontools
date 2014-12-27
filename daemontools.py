from sublime_plugin import WindowCommand, TextCommand
from .utils import remoteCommand
from sublime import set_timeout, message_dialog, Region, active_window

class Daemontools(WindowCommand):

    def run(self):
        self.view = self.window.active_view()
        self._listServices()

    def _listServices(self):
        result = remoteCommand(self.view, "svstat /etc/service/*").strip()
        if result:
            services = [s[len('/etc/service/'):] for s in result.split('\n')]
            set_timeout(lambda: self.window.show_quick_panel(services, lambda i: self._showActions(services[i].split(':')[0]) if i != -1 else None), 0)
        else:
            message_dialog("No service found")

    def _showActions(self, service):
        actions = ['start', 'stop', 'restart', 'view log']
        status = remoteCommand(self.view, "svstat /etc/service/{0}".format(service)).strip()[len('/etc/service/'):]

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
        if action == 'view log':
            self._showLog(service)
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

    def _showLog(self, service):
        name = "Log {0}".format(service)
        newView = self.view.window().new_file()
        newView.set_name(name)
        newView.set_syntax_file("Packages/Text/Plain text.tmLanguage")
        newView.set_scratch(True)
        refreshLog(service, newView)

def refreshLog(service, view, lines=0):
    if not view.window():
        return
    visibleRegion = view.visible_region()
    currentLine = view.line(Region(visibleRegion.b, visibleRegion.b))
    lastLine = view.line(Region(view.size(), view.size()))
    if currentLine == lastLine and active_window().active_view() == view:
        logData = remoteCommand(view, "cat /etc/service/{0}/log/main/current | tail -n +{1} | tai64nlocal".format(service, lines + 1))
        lines += logData.count("\n")
        view.set_read_only(False)
        view.run_command("add_text", {"data": logData})
        view.set_read_only(True)
        view.show(Region(view.size(), view.size()))
    set_timeout(lambda: refreshLog(service, view, lines), 1000)

class AddText(TextCommand):
    def run(self, edit, data):
        self.view.insert(edit, self.view.size(), data)
