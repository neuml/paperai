"""
Report factory module
"""

import os.path

from .csvr import CSV
from .markdown import Markdown
from .task import Task

from ..models import Models

class Execute(object):
    """
    Creates a Report
    """

    @staticmethod
    def create(render, embeddings, db, qa):
        """
        Factory method to construct a Report.

        Args:
            render: report rendering format
            embeddings: embeddings index
            db: database connection
            qa: qa model path

        Returns:
            Report
        """

        if render == "csv":
            return CSV(embeddings, db, qa)
        elif render == "md":
            return Markdown(embeddings, db, qa)

        return None

    @staticmethod
    def run(task, topn=None, render=None, path=None, qa=None):
        """
        Reads a list of queries from a task file and builds a report.

        Args:
            task: input task file
            topn: number of results
            render: report rendering format ("md" for markdown, "csv" for csv)
            path: embeddings model path
            qa: qa model path
        """

        # Load model
        embeddings, db = Models.load(path)

        # Read task configuration
        name, queries, outdir = Task.load(task)

        # Derive report format
        render = render if render else "md"

        # Create report object. Default to Markdown.
        report = Execute.create(render, embeddings, db, qa)

        # Generate output filename
        outfile = os.path.join(outdir, "%s.%s" % (name, render))

        # Stream report to file
        with open(outfile, "w") as output:
            # Build the report
            report.build(queries, topn, output)

        # Free any resources
        report.cleanup(outfile)

        # Free resources
        Models.close(db)
