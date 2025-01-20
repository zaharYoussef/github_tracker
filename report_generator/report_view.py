# report_view.py
import panel as pn
import hvplot.pandas
import pandas as pd
from datetime import datetime, timedelta

class ReportView:
    """
    Handles the creation of the UI layout and visualizations for the report.
    """
    def __init__(self, data_loader):
        self.data_loader = data_loader
        pn.extension()

    def _create_general_report(self):
        """Build the General Report view."""
        metrics = self.data_loader.get_overall_metrics()
        file_types = self.data_loader.get_file_type_breakdown()
        top_n_languages = self.data_loader.get_top_languages()
        repo_summary = self.data_loader.get_repo_contributions_summary()

        metrics_table = pn.pane.Markdown(
            f"""
            ### General Report
            - **Total Commits**: {metrics['total_commits']}
            - **PRs Submitted**: {metrics['total_prs_submitted']}
            - **PRs Reviewed**: {metrics['total_prs_comments']}
            
            ### Top Languages
            {', '.join([f'{lang}: {count}' for lang, count in top_n_languages.items()])}
            
            """
        )

        file_type_plot = self._plot_file_types(file_types, title="File Type Breakdown")
        
        repos_summary = self._create_repo_table(repo_summary, title="Repository Contribution Summary")

        commits_plot = self._placeholder_plot("commits heat map")

        return pn.Column(metrics_table, file_type_plot, repos_summary, commits_plot)

    def _create_repo_tab(self, repo_name):
        """Build a report view for a specific repository."""
        repo_metrics = self.data_loader.get_repo_specific_metrics(repo_name)

        metrics_table = pn.pane.Markdown(
            f"""
            ### Report for {repo_name}
            - **Total Commits**: {repo_metrics['total_commits']}
            - **PRs Submitted**: {repo_metrics['total_prs_submitted']}
            - **PRs Reviewed**: {repo_metrics['total_prs_comments']}
            """
        )

        file_type_plot = self._plot_file_types(repo_metrics['file_types'], title=f"File Type Breakdown for {repo_name}")

        commits_plot = self._placeholder_plot("commits heat map")

        return pn.Column(metrics_table, file_type_plot, commits_plot)
    

    def _plot_file_types(self, file_types, title):
        """Create an interactive bar plot for file type breakdown."""
        data = pd.DataFrame(list(file_types.items()), columns=["File Type", "Count"])
        if data.empty:
            return pn.pane.Markdown("No file data available.")

        return data.hvplot.bar(
            x="File Type",
            y="Count",
            title=title,
            xlabel="File Type",
            ylabel="Count",
            width=600,
            height=400,
            dynamic=False
        ).opts(
            shared_axes=False,  # each plot gets independent x-/y-axes
            framewise=True      # redraw the axis range for each plot based on its own data
        )
    
    def _create_repo_table(self, repo_summary, title):
        """Create a repository contribution summary table with filters for time ranges."""
        
        time_filter = pn.widgets.Select(
            name="Filter by Date",
            options=["None", "Last Month", "Last 6 Months", "Last Year"],
            value="None",
        )

        def filter_table(event):
            filtered_data = repo_summary.copy()
            now = pd.Timestamp.now()

            if event.new == "Last Month":
                start_date = now - pd.DateOffset(months=1)
                filtered_data = filtered_data[
                    filtered_data["Last Contribution Date"] >= start_date
                ]
            elif event.new == "Last 6 Months":
                start_date = now - pd.DateOffset(months=6)
                filtered_data = filtered_data[
                    filtered_data["Last Contribution Date"] >= start_date
                ]
            elif event.new == "Last Year":
                start_date = now - pd.DateOffset(years=1)
                filtered_data = filtered_data[
                    filtered_data["Last Contribution Date"] >= start_date
                ]
            elif event.new == "None":
                filtered_data = repo_summary

            repo_table.value = filtered_data.reset_index(drop=True)

        time_filter.param.watch(filter_table, "value")

        repo_table = pn.widgets.Tabulator(
            repo_summary,
            pagination="remote",
            page_size=2,
            sizing_mode="stretch_width",
        )

        table_title = pn.pane.Markdown(f"### {title}")

        return pn.Column(table_title, time_filter, repo_table)
    

    def _placeholder_plot(self, title):
        """Create a placeholder plot for sections not yet implemented."""
        return pn.pane.Markdown(f"### {title}\n*(Plot not implemented yet)*")

    def build_view(self):
        """Build the complete Panel application view."""
        general_report = self._create_general_report()

        tabs = pn.Tabs(("General Report", general_report))
        for repo_name in self.data_loader.data["repos"].keys():
            tabs.append((repo_name, self._create_repo_tab(repo_name)))

        return tabs