import panel as pn
from .report_view import ReportView
from .data_loader import DataLoader

class ReportController:
    """
    Orchestrates the data and view layers to build and serve the report application.
    """
    def __init__(self, data_file="github_data.json"):
        self.data_loader = DataLoader(data_file)
        self.report_view = ReportView(self.data_loader)

    def build_app(self):
        """Build the Panel application."""
        return self.report_view.build_view()

    def server_app(self,title, port, address="0.0.0.0"):
        pn.extension()
        app = self.build_app()
        pn.serve(
            app,
            title=title,
            port=port
        )
